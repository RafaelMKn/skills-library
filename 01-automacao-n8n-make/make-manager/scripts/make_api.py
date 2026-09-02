#!/usr/bin/env python3
"""CLI segura e enxuta para a API v2 do Make."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

def load_env(path: Path) -> dict:
    values = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def request(url: str, token: str, method="GET", payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method=method, headers={
        "Authorization": f"Token {token}", "Accept": "application/json", "Content-Type": "application/json",
        "User-Agent": "agent-creator-hub-make-manager/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            if not raw:
                return response.status, {}
            try:
                return response.status, json.loads(raw)
            except json.JSONDecodeError:
                return response.status, {"body": raw}
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            return error.code, json.loads(raw)
        except json.JSONDecodeError:
            return error.code, {"message": raw}
    except urllib.error.URLError as error:
        return 0, {"message": str(error.reason)}


def fail(message, *, status=None):
    result = {"error": message}
    if status is not None:
        result["status"] = status
    print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(1)


def payload_from(path: str):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Arquivo de payload não encontrado: {path}")
    except json.JSONDecodeError as error:
        fail(f"JSON inválido em {path}: {error}")


def query_url(base: str, endpoint: str, params: dict) -> str:
    clean = {key: value for key, value in params.items() if value is not None}
    query = urllib.parse.urlencode(clean, doseq=True)
    return f"{base}{endpoint}" + (f"?{query}" if query else "")


def zone_from(value):
    """Extrai um domínio público de zona do campo `zone` da organização."""
    text = json.dumps(value) if isinstance(value, (dict, list)) else str(value or "")
    match = re.search(r"(?:us|eu)\d+\.make\.com", text, re.IGNORECASE)
    return match.group(0).lower() if match else None


def iter_modules(blueprint):
    """Percorre módulos de subfluxos e do fluxo principal de um blueprint."""
    for subflow in blueprint.get("subflows", []):
        yield from subflow.get("flow", [])
    yield from blueprint.get("flow", [])


def error_route_has_email_and_ignore(route):
    modules = []

    def visit(nodes):
        for node in nodes or []:
            modules.append(node.get("module"))
            visit(node.get("onerror"))

    visit(route)
    return "email:ActionSendEmail" in modules and "builtin:Ignore" in modules


def inspect_lead_error_handlers(base, token, scenario):
    status, response = 0, {}
    for attempt in range(3):
        status, response = request(f"{base}/scenarios/{scenario['id']}/blueprint", token)
        if status != 429:
            break
        time.sleep(2 ** attempt)
    result = {"id": scenario["id"], "name": scenario.get("name"), "active": scenario.get("isActive")}
    if status != 200:
        result.update({"status": "unreadable", "http_modules": []})
        return result
    blueprint = response.get("response", {}).get("blueprint", {})
    http_modules = [module for module in iter_modules(blueprint) if str(module.get("module", "")).startswith("http:")]
    handlers = [{
        "id": module.get("id"),
        "protected": error_route_has_email_and_ignore(module.get("onerror")),
    } for module in http_modules]
    if not handlers:
        state = "not_applicable"
    elif all(handler["protected"] for handler in handlers):
        state = "protected"
    elif any(handler["protected"] for handler in handlers):
        state = "partial"
    else:
        state = "pending"
    result.update({"status": state, "http_modules": handlers})
    return result


def campaign_code_from_blueprint(blueprint):
    """Extrai somente o identificador comercial do corpo HTTP, sem expor o payload."""
    for module in iter_modules(blueprint):
        if not str(module.get("module", "")).startswith("http:"):
            continue
        mapper = module.get("mapper", {})
        body = mapper.get("jsonStringBodyContent") or mapper.get("data") or ""
        match = re.search(r'"campaing_code"\s*:\s*"([^"\n]+)"', body)
        if match:
            return match.group(1)
    return None


def read_with_backoff(url, token, attempts=4):
    status, response = 0, {}
    for attempt in range(attempts):
        status, response = request(url, token)
        if status != 429:
            return status, response
        time.sleep(2 ** attempt)
    return status, response


SAFE_CONNECTION_FIELDS = (
    "id", "name", "accountName", "accountLabel", "accountType", "teamId",
    "organizationId", "uid", "expire", "scoped", "scopesCnt", "editable", "upgradeable",
)


def safe_connection(connection):
    """Projeta só campos não sensíveis. O segredo da conexão nunca sai daqui."""
    item = {field: connection.get(field) for field in SAFE_CONNECTION_FIELDS}
    metadata = connection.get("metadata")
    item["label"] = metadata.get("value") if isinstance(metadata, dict) else None
    scopes = connection.get("scopes")
    if isinstance(scopes, list):
        item["scopes"] = [scope.get("id") if isinstance(scope, dict) else scope for scope in scopes]
    return item


def list_connections(base, token, team_id):
    endpoint = query_url(base, "/connections", {"teamId": team_id})
    status, response = request(endpoint, token)
    if status != 200:
        fail("Não foi possível listar as conexões da equipe.", status=status)
    connections = [safe_connection(item) for item in response.get("connections", [])]
    print(json.dumps({"total": len(connections), "connections": connections}, indent=2, ensure_ascii=False))


def get_connection(base, token, connection_id):
    status, response = request(f"{base}/connections/{connection_id}", token)
    if status != 200:
        fail("Não foi possível ler a conexão.", status=status)
    print(json.dumps({"connection": safe_connection(response.get("connection", {}))}, indent=2, ensure_ascii=False))


def map_lead_scenarios(base, token, team_id, active_only):
    scenarios, offset = [], 0
    while True:
        endpoint = query_url(base, "/scenarios", {"teamId": team_id, "pg[limit]": 100, "pg[offset]": offset})
        status, response = request(endpoint, token)
        if status != 200:
            fail("Não foi possível listar os cenários para o mapeamento.", status=status)
        page = response.get("scenarios", [])
        scenarios.extend(page)
        if len(page) < 100:
            break
        offset += 100

    selected = [scenario for scenario in scenarios
                if "facebook-lead-ads" in scenario.get("usedPackages", [])
                and (scenario.get("isActive") or not active_only)]
    result = []
    for scenario in selected:
        item = {"scenario_id": scenario["id"], "scenario": scenario.get("name"),
                "active": scenario.get("isActive"), "hook_id": scenario.get("hookId"),
                "page_id": None, "form_id": None, "campaing_code": None, "status": "ok"}
        if not item["hook_id"]:
            item["status"] = "hook_ausente"
            result.append(item)
            continue
        hook_status, hook_response = read_with_backoff(f"{base}/hooks/{item['hook_id']}", token)
        if hook_status != 200:
            item["status"] = f"hook_nao_lido_{hook_status}"
            result.append(item)
            continue
        hook_data = hook_response.get("hook", {}).get("data", {})
        item["page_id"] = hook_data.get("pageId")
        item["form_id"] = hook_data.get("formId")
        blueprint_status, blueprint_response = read_with_backoff(f"{base}/scenarios/{scenario['id']}/blueprint", token)
        if blueprint_status != 200:
            item["status"] = f"blueprint_nao_lido_{blueprint_status}"
            result.append(item)
            continue
        item["campaing_code"] = campaign_code_from_blueprint(
            blueprint_response.get("response", {}).get("blueprint", {}),
        )
        if not item["page_id"] or not item["form_id"] or not item["campaing_code"]:
            item["status"] = "identificador_ausente"
        result.append(item)
        time.sleep(0.25)
    result.sort(key=lambda item: (item["scenario"] or "", item["scenario_id"]))
    print(json.dumps({"total": len(result), "scenarios": result}, indent=2, ensure_ascii=False))


def add_lead_error_handler(blueprint, module_id, recipient, connection_id):
    """Adiciona no HTTP informado a rota email -> Ignore, sem tocar no fluxo normal."""
    target = next((module for module in iter_modules(blueprint) if str(module.get("id")) == str(module_id)), None)
    if target is None:
        fail(f"Módulo {module_id} não encontrado no blueprint.")
    if not str(target.get("module", "")).startswith("http:"):
        fail(f"Módulo {module_id} não é um módulo HTTP.")
    if target.get("onerror"):
        fail(f"Módulo {module_id} já possui uma rota de erro; a ferramenta não a sobrescreve.")

    def collect_ids(nodes):
        ids = []
        for node in nodes or []:
            if str(node.get("id", "")).isdigit():
                ids.append(int(node["id"]))
            ids.extend(collect_ids(node.get("onerror")))
        return ids

    used_ids = collect_ids(list(iter_modules(blueprint)))
    email_id = max(used_ids, default=0) + 1
    ignore_id = email_id + 1
    position = target.get("metadata", {}).get("designer", {})
    x = position.get("x", 0)
    y = position.get("y", 0)
    target["onerror"] = [
        {
            "id": email_id,
            "module": "email:ActionSendEmail",
            "version": 7,
            "parameters": {"account": int(connection_id), "saveAfterSent": False},
            "mapper": {
                "to": [recipient], "cc": [], "bcc": [], "from": "", "sender": "", "headers": [],
                "replyTo": "", "inReplyTo": "", "references": [], "attachments": [], "priority": "normal",
                "contentType": "text",
                "subject": "Erro no Make — {{var.scenario.name}}",
                "text": f"Fluxo: {{{{var.scenario.name}}}}\nMódulo com falha: {{{{`{module_id}`}}}}\nErro: {{{{{module_id}.error}}}}\nLead ID: {{{{2.leadgenId}}}}",
            },
            "metadata": {"designer": {"x": x + 300, "y": y}},
        },
        {
            "id": ignore_id,
            "module": "builtin:Ignore",
            "version": 1,
            "parameters": {},
            "mapper": {},
            "metadata": {"designer": {"x": x + 600, "y": y}},
        },
    ]
    return email_id, ignore_id


def main():
    parser = argparse.ArgumentParser(description="Gerencia cenários do Make via API v2.")
    parser.add_argument("--account", required=True, help="Conta configurada no .env, por exemplo PROD ou MINHA_CONTA.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    detect_zone = subparsers.add_parser("detect-zone", help="Detecta a zona pela organização sem exibir dados de usuário.")
    detect_zone.add_argument("--organization-id", help="Restringe a detecção à organização informada quando o token tiver mais de uma.")
    subparsers.add_parser("probe", help="Confirma token e URL sem exibir dados da conta.")
    subparsers.add_parser("list-organizations")

    list_hooks = subparsers.add_parser("list-hooks")
    list_hooks.add_argument("team_id")
    list_hooks.add_argument("--limit", type=int, default=100)
    list_hooks.add_argument("--offset", type=int, default=0)

    list_connections_parser = subparsers.add_parser("list-connections", help="Lista as conexões da equipe sem expor segredos.")
    list_connections_parser.add_argument("team_id")

    get_connection_parser = subparsers.add_parser("get-connection", help="Detalha uma conexão sem expor segredos.")
    get_connection_parser.add_argument("connection_id")

    map_leads = subparsers.add_parser("map-lead-scenarios", help="Mapeia cenários Meta ativos aos pares página/formulário e ao código de campanha.")
    map_leads.add_argument("team_id")
    map_leads.add_argument("--include-inactive", action="store_true")

    list_teams = subparsers.add_parser("list-teams")
    list_teams.add_argument("organization_id")
    list_teams.add_argument("--limit", type=int, default=100)
    list_teams.add_argument("--offset", type=int, default=0)
    list_scenarios = subparsers.add_parser("list-scenarios")
    list_scenarios.add_argument("team_id")
    list_scenarios.add_argument("--limit", type=int, default=100)
    list_scenarios.add_argument("--offset", type=int, default=0)
    get_scenario = subparsers.add_parser("get-scenario")
    get_scenario.add_argument("scenario_id")
    get_hook = subparsers.add_parser("get-hook")
    get_hook.add_argument("hook_id")
    get_blueprint = subparsers.add_parser("get-blueprint")
    get_blueprint.add_argument("scenario_id")
    get_blueprint.add_argument("--draft", choices=("true", "false"))
    list_logs = subparsers.add_parser("list-logs")
    list_logs.add_argument("scenario_id")
    list_logs.add_argument("--limit", type=int, default=20)
    list_logs.add_argument("--offset", type=int, default=0)
    get_execution = subparsers.add_parser("get-execution")
    get_execution.add_argument("scenario_id")
    get_execution.add_argument("execution_id")
    audit = subparsers.add_parser("audit-lead-error-handlers", help="Audita os módulos HTTP dos cenários de uma equipe.")
    audit.add_argument("team_id")
    audit.add_argument("--limit", type=int, default=100)
    handler = subparsers.add_parser("add-lead-error-handler", help="Adiciona email + Ignore ao módulo HTTP de um cenário.")
    handler.add_argument("scenario_id")
    handler.add_argument("module_id")
    handler.add_argument("--recipient", required=True)
    handler.add_argument("--email-connection", required=True)
    handler.add_argument("--confirm", action="store_true", help="Confirma a alteração do cenário ativo.")
    bulk_handler = subparsers.add_parser("add-lead-error-handlers", help="Replica email + Ignore em todos os HTTPs pendentes de uma equipe.")
    bulk_handler.add_argument("team_id")
    bulk_handler.add_argument("--recipient", required=True)
    bulk_handler.add_argument("--email-connection", required=True)
    bulk_handler.add_argument("--active-only", action="store_true", help="Limita a alteração aos cenários ativos.")
    bulk_handler.add_argument("--confirm", action="store_true", help="Confirma a alteração em massa dos cenários.")

    for name in ("create-scenario", "update-scenario", "start-scenario", "stop-scenario", "run-scenario", "delete-scenario"):
        action = subparsers.add_parser(name)
        if name != "create-scenario":
            action.add_argument("scenario_id")
        if name in ("create-scenario", "update-scenario", "run-scenario"):
            action.add_argument("json_file")
        action.add_argument("--confirm", action="store_true", help="Confirma ação que altera ou executa automações.")

    args = parser.parse_args()
    account = args.account.strip().upper()
    # Busca .env no diretório atual e nos pais
    config = {}
    curr = Path.cwd()
    for directory in [curr, *curr.parents]:
        env_file = directory / ".env"
        if env_file.is_file():
            config = load_env(env_file)
            if f"MAKE_{account}_API_TOKEN" in config:
                break
    token = os.environ.get(f"MAKE_{account}_API_TOKEN") or config.get(f"MAKE_{account}_API_TOKEN")
    if not token:
        fail(f"MAKE_{account}_API_TOKEN não encontrado no .env.")

    if args.command == "detect-zone":
        # /ping funciona em todas as zonas e não as diferencia. A resposta de
        # /organizations traz o campo `zone`, conforme a referência oficial.
        discovery_base = "https://us1.make.com/api/v2"
        endpoint = query_url(discovery_base, "/organizations", {"cols[]": ["id", "name", "zone"]})
        status, response = request(endpoint, token)
        if status != 200:
            fail("Não foi possível consultar as organizações para descobrir a zona.", status=status)
        organizations = response.get("organizations", [])
        if args.organization_id:
            organizations = [org for org in organizations if str(org.get("id", org.get("organizationId", ""))) == args.organization_id]
        candidates = []
        for organization in organizations:
            domain = zone_from(organization.get("zone"))
            if domain:
                candidates.append({
                    "organization_id": organization.get("id", organization.get("organizationId")),
                    "name": organization.get("name"),
                    "api_url": f"https://{domain}/api/v2",
                })
        urls = sorted({candidate["api_url"] for candidate in candidates})
        if len(urls) == 1:
            print(json.dumps({"api_url": urls[0], "organizations": candidates}, ensure_ascii=False))
            return
        print(json.dumps({
            "error": "A organização não retornou uma única zona pública.",
            "organizations": candidates,
            "next_step": "Informe --organization-id ou copie a URL da barra de endereço do Make.",
        }, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)

    base = (os.environ.get(f"MAKE_{account}_API_URL") or config.get(f"MAKE_{account}_API_URL", "")).rstrip("/")
    if not base:
        fail(f"MAKE_{account}_API_URL não encontrado no .env. Execute detect-zone primeiro.")
    if not base.endswith("/api/v2"):
        fail(f"MAKE_{account}_API_URL deve terminar em /api/v2.")
    if args.command == "probe":
        status, _ = request(f"{base}/ping", token)
        if status == 200:
            print(json.dumps({"ok": True, "api_url": base}, ensure_ascii=False))
            return
        fail("Autenticação ou zona inválida.", status=status)

    if args.command == "list-connections":
        list_connections(base, token, args.team_id)
        return

    if args.command == "get-connection":
        get_connection(base, token, args.connection_id)
        return

    if args.command == "map-lead-scenarios":
        map_lead_scenarios(base, token, args.team_id, active_only=not args.include_inactive)
        return

    if args.command == "audit-lead-error-handlers":
        scenarios, offset = [], 0
        while True:
            endpoint = query_url(base, "/scenarios", {"teamId": args.team_id, "pg[limit]": args.limit, "pg[offset]": offset})
            status, response = request(endpoint, token)
            if status != 200:
                fail("Não foi possível listar os cenários para a auditoria.", status=status)
            page = response.get("scenarios", [])
            scenarios.extend(page)
            if len(page) < args.limit:
                break
            offset += args.limit
        reports = []
        # Três chamadas concorrentes terminam dentro do limite do executor sem
        # produzir o pico de oito requisições que a API recusou anteriormente.
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(inspect_lead_error_handlers, base, token, scenario) for scenario in scenarios]
            for future in as_completed(futures):
                reports.append(future.result())
        reports.sort(key=lambda report: (report["name"] or "", report["id"]))
        summary = {state: sum(report["status"] == state for report in reports) for state in ("protected", "partial", "pending", "not_applicable", "unreadable")}
        pending = [report for report in reports if report["status"] in {"partial", "pending", "unreadable"}]
        print(json.dumps({"summary": {"total": len(reports), **summary}, "needs_attention": pending}, indent=2, ensure_ascii=False))
        return

    if args.command == "add-lead-error-handler":
        if not args.confirm:
            fail("Ação com efeito externo: execute novamente com --confirm após autorização explícita do usuário.")
        status, response = request(f"{base}/scenarios/{args.scenario_id}/blueprint", token)
        if status != 200:
            fail("Não foi possível buscar o blueprint atual do cenário.", status=status)
        blueprint = response.get("response", {}).get("blueprint")
        if not blueprint:
            fail("A API não retornou o blueprint do cenário.")
        email_id, ignore_id = add_lead_error_handler(blueprint, args.module_id, args.recipient, args.email_connection)
        payload = {"blueprint": json.dumps(blueprint, ensure_ascii=False, separators=(",", ":"))}
        status, _ = request(f"{base}/scenarios/{args.scenario_id}", token, "PATCH", payload)
        if not 200 <= status < 300:
            fail("A API do Make recusou a atualização do cenário.", status=status)
        status, response = request(f"{base}/scenarios/{args.scenario_id}/blueprint", token)
        verified = status == 200 and any(
            str(module.get("id")) == str(args.module_id) and error_route_has_email_and_ignore(module.get("onerror"))
            for module in iter_modules(response.get("response", {}).get("blueprint", {}))
        )
        if not verified:
            fail("A atualização foi aceita, mas a rota de erro não pôde ser verificada. Não replique o padrão ainda.")
        print(json.dumps({"ok": True, "scenario_id": args.scenario_id, "module_id": args.module_id, "email_module_id": email_id, "ignore_module_id": ignore_id}, ensure_ascii=False))
        return

    if args.command == "add-lead-error-handlers":
        if not args.confirm:
            fail("Ação em massa com efeito externo: execute novamente com --confirm após autorização explícita do usuário.")
        scenarios, offset = [], 0
        while True:
            endpoint = query_url(base, "/scenarios", {"teamId": args.team_id, "pg[limit]": 100, "pg[offset]": offset})
            status, response = request(endpoint, token)
            if status != 200:
                fail("Não foi possível listar os cenários para a atualização em massa.", status=status)
            page = response.get("scenarios", [])
            scenarios.extend(page)
            if len(page) < 100:
                break
            offset += 100

        results = []
        for scenario in scenarios:
            if args.active_only and not scenario.get("isActive"):
                continue
            status, response = request(f"{base}/scenarios/{scenario['id']}/blueprint", token)
            if status != 200:
                results.append({"id": scenario["id"], "name": scenario.get("name"), "status": "failed_to_read"})
                continue
            blueprint = response.get("response", {}).get("blueprint", {})
            target_ids = [module.get("id") for module in iter_modules(blueprint)
                          if str(module.get("module", "")).startswith("http:") and not module.get("onerror")]
            if not target_ids:
                results.append({"id": scenario["id"], "name": scenario.get("name"), "status": "already_protected"})
                continue
            try:
                for module_id in target_ids:
                    add_lead_error_handler(blueprint, module_id, args.recipient, args.email_connection)
            except SystemExit:
                results.append({"id": scenario["id"], "name": scenario.get("name"), "status": "failed_to_prepare"})
                continue
            payload = {"blueprint": json.dumps(blueprint, ensure_ascii=False, separators=(",", ":"))}
            status, _ = request(f"{base}/scenarios/{scenario['id']}", token, "PATCH", payload)
            if not 200 <= status < 300:
                results.append({"id": scenario["id"], "name": scenario.get("name"), "status": "failed_to_update", "http_modules": target_ids})
                continue
            status, response = request(f"{base}/scenarios/{scenario['id']}/blueprint", token)
            verified = status == 200 and all(
                any(str(module.get("id")) == str(module_id) and error_route_has_email_and_ignore(module.get("onerror"))
                    for module in iter_modules(response.get("response", {}).get("blueprint", {})))
                for module_id in target_ids
            )
            results.append({"id": scenario["id"], "name": scenario.get("name"),
                            "status": "updated" if verified else "failed_to_verify", "http_modules": target_ids})

        summary = {state: sum(result["status"] == state for result in results)
                   for state in ("updated", "already_protected", "failed_to_read", "failed_to_prepare", "failed_to_update", "failed_to_verify")}
        failures = [result for result in results if result["status"].startswith("failed")]
        print(json.dumps({"summary": summary, "failures": failures}, indent=2, ensure_ascii=False))
        if failures:
            raise SystemExit(1)
        return

    writes = {"create-scenario", "update-scenario", "start-scenario", "stop-scenario", "run-scenario", "delete-scenario"}
    if args.command in writes and not args.confirm:
        fail("Ação com efeito externo: execute novamente com --confirm após autorização explícita do usuário.")

    if args.command == "list-organizations":
        endpoint, method, data = "/organizations", "GET", None
    elif args.command == "list-hooks":
        endpoint = query_url(base, "/hooks", {"teamId": args.team_id, "pg[limit]": args.limit, "pg[offset]": args.offset})
        method, data, base = "GET", None, ""
    elif args.command == "list-teams":
        endpoint = query_url(base, "/teams", {"organizationId": args.organization_id, "pg[limit]": args.limit, "pg[offset]": args.offset})
        method, data, base = "GET", None, ""
    elif args.command == "list-scenarios":
        endpoint = query_url(base, "/scenarios", {"teamId": args.team_id, "pg[limit]": args.limit, "pg[offset]": args.offset})
        method, data, base = "GET", None, ""
    elif args.command == "get-scenario":
        endpoint, method, data = f"/scenarios/{args.scenario_id}", "GET", None
    elif args.command == "get-hook":
        endpoint, method, data = f"/hooks/{args.hook_id}", "GET", None
    elif args.command == "get-blueprint":
        endpoint, method, data = f"/scenarios/{args.scenario_id}/blueprint", "GET", None
        if args.draft is not None:
            endpoint, base = query_url(base, endpoint, {"draft": args.draft}), ""
    elif args.command == "list-logs":
        endpoint = query_url(base, f"/scenarios/{args.scenario_id}/logs", {"pg[limit]": args.limit, "pg[offset]": args.offset})
        method, data, base = "GET", None, ""
    elif args.command == "get-execution":
        endpoint, method, data = f"/scenarios/{args.scenario_id}/executions/{args.execution_id}", "GET", None
    elif args.command == "create-scenario":
        endpoint, method, data = "/scenarios", "POST", payload_from(args.json_file)
    elif args.command == "update-scenario":
        endpoint, method, data = f"/scenarios/{args.scenario_id}", "PATCH", payload_from(args.json_file)
    elif args.command == "start-scenario":
        endpoint, method, data = f"/scenarios/{args.scenario_id}/start", "POST", {}
    elif args.command == "stop-scenario":
        endpoint, method, data = f"/scenarios/{args.scenario_id}/stop", "POST", {}
    elif args.command == "run-scenario":
        endpoint, method, data = f"/scenarios/{args.scenario_id}/run", "POST", payload_from(args.json_file)
    else:
        endpoint, method, data = f"/scenarios/{args.scenario_id}", "DELETE", None

    status, response = request(f"{base}{endpoint}", token, method, data)
    if 200 <= status < 300:
        print(json.dumps(response, indent=2, ensure_ascii=False))
        return
    fail("A API do Make recusou a operação.", status=status)


if __name__ == "__main__":
    main()
