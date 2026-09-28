#!/usr/bin/env python3
"""Coletor do Radar n8n — varre as instancias configuradas e agrega erros por fluxo.

Le o `.env` da raiz do workspace (mesmo formato do n8n-manager: N8N_<INST>_API_URL /
N8N_<INST>_API_KEY), pagina as execucoes de uma janela de tempo, agrupa por workflow e
classifica a causa raiz de cada erro a partir da mensagem do no que falhou.

Uso:
    python3 scripts/radar_n8n.py                      # janela padrao 24h, todas as instancias
    python3 scripts/radar_n8n.py --hours 168          # 7 dias
    python3 scripts/radar_n8n.py --instance CRM_PROD   # so uma instancia (repetivel)
    python3 scripts/radar_n8n.py --json-out radar.json --state-dir ~/.hermes/radar-n8n

Saida: JSON no stdout (ou no --json-out) com placar por instancia, top fluxos com erro,
causa raiz classificada e o diff contra a coleta anterior guardada em --state-dir.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_WORKSPACE = Path(os.environ.get("WORKSPACE_DIR", Path.cwd()))
PAGE_LIMIT = 250
MAX_PAGES = 40
SAMPLES_POR_FLUXO = 1

# Classificacao de causa raiz: (regex, rotulo, dica de acao)
PADROES_CAUSA = [
    (r"could not be decrypted|bad decrypt|encryptionKey",
     "credencial-nao-descriptografavel",
     "N8N_ENCRYPTION_KEY divergente do que cifrou as credenciais. Recriar a credencial na instancia."),
    (r"\b401\b|unauthorized|invalid[_ ]api[_ ]key|authentication failed|forbidden|\b403\b",
     "credencial-invalida",
     "Token expirado ou sem escopo. Renovar a credencial no n8n."),
    (r"\b429\b|rate.?limit|too many requests|quota",
     "rate-limit",
     "Adicionar retry com backoff no no ou reduzir concorrencia."),
    (r"EAI_AGAIN|ENOTFOUND",
     "dns-nao-resolve",
     "Hostname nao resolve de dentro do container n8n (servico ausente na rede/compose)."),
    (r"ETIMEDOUT|ECONNREFUSED|socket hang up|network|timeout",
     "rede-indisponivel",
     "Endpoint fora do ar ou inacessivel. Verificar o servico de destino."),
    (r"\b5\d\d\b|internal server error|bad gateway|service unavailable",
     "erro-no-servico-externo",
     "Falha do lado do provedor. Adicionar branch de erro e retry."),
    (r"Cannot read propert|undefined is not|is not a function|TypeError|ReferenceError",
     "dado-inesperado",
     "Payload sem o campo esperado. Validar entrada antes do no."),
    (r"expression|\[Item .*\]|Referenced node is unexecuted|No data|paired item",
     "expressao-quebrada",
     "Revisar expressao n8n (skill n8n-expression-syntax)."),
    (r"JSON|parse|SyntaxError",
     "parsing",
     "Resposta em formato inesperado. Tratar antes de parsear."),
    (r"duplicate key|constraint|SQLSTATE|ORA-|ER_",
     "erro-de-banco",
     "Violacao de constraint ou schema divergente."),
]


def carregar_env(workspace: Path) -> dict:
    """Le o .env da raiz do workspace, sem sobrescrever variaveis ja exportadas."""
    env = {}
    caminho = workspace / ".env"
    if caminho.is_file():
        for linha in caminho.read_text(encoding="utf-8", errors="replace").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, _, valor = linha.partition("=")
            env[chave.strip()] = valor.strip().strip('"').strip("'")
    for chave, valor in os.environ.items():
        if chave.startswith("N8N_") and valor:
            env[chave] = valor
    return env


def instancias_de(env: dict) -> dict:
    """Extrai {NOME: (url, key)} dos pares N8N_<NOME>_API_URL / _API_KEY preenchidos."""
    achadas = {}
    for chave, valor in env.items():
        if not (chave.startswith("N8N_") and chave.endswith("_API_URL")):
            continue
        nome = chave[len("N8N_"):-len("_API_URL")]
        url = (valor or "").strip().rstrip("/")
        key = (env.get(f"N8N_{nome}_API_KEY") or "").strip()
        if url and key:
            achadas[nome] = (re.sub(r"/api/v1/?$", "", url), key)
    return achadas


def _requisitar(url: str, api_key: str, timeout: int = 45):
    req = urllib.request.Request(url, headers={
        "X-N8N-API-KEY": api_key,
        "Accept": "application/json",
        "User-Agent": "radar-n8n/1.0",
    })
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def buscar_execucoes(base: str, api_key: str, status: str, desde: datetime, timeout: int):
    """Pagina /executions ate sair da janela. O n8n nao filtra por data, entao cortamos aqui."""
    itens, cursor, paginas = [], None, 0
    while paginas < MAX_PAGES:
        params = {"limit": PAGE_LIMIT, "status": status, "includeData": "false"}
        if cursor:
            params["cursor"] = cursor
        url = f"{base}/api/v1/executions?{urllib.parse.urlencode(params)}"
        dados = _requisitar(url, api_key, timeout)
        lote = dados.get("data") or []
        if not lote:
            break
        fora_da_janela = False
        for ex in lote:
            quando = _parse_data(ex.get("startedAt") or ex.get("createdAt"))
            if quando and quando < desde:
                fora_da_janela = True
                continue
            itens.append(ex)
        cursor = dados.get("nextCursor")
        paginas += 1
        if fora_da_janela or not cursor:
            break
    return itens


def _parse_data(valor):
    if not valor:
        return None
    try:
        return datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except ValueError:
        return None


def mensagem_de_erro(base: str, api_key: str, exec_id, timeout: int):
    """Puxa uma execucao com dados e extrai (mensagem, no_que_falhou)."""
    try:
        url = f"{base}/api/v1/executions/{exec_id}?includeData=true"
        dados = _requisitar(url, api_key, timeout)
    except Exception as exc:  # noqa: BLE001 - amostra e best-effort
        return f"<falha ao obter detalhe: {exc}>", None
    d = (dados.get("data") or {}).get("resultData") or {}
    erro = d.get("error") or {}
    msg = erro.get("message") or erro.get("description") or ""
    no = (erro.get("node") or {}).get("name") if isinstance(erro.get("node"), dict) else None
    if not msg:
        for nome, saidas in (d.get("runData") or {}).items():
            for saida in saidas or []:
                e = (saida or {}).get("error") or {}
                if e.get("message"):
                    return str(e["message"])[:500], nome
    return str(msg)[:500], no


def nomes_de_workflows(base: str, api_key: str, timeout: int) -> dict:
    """Mapa {workflow_id: nome}. A listagem de execucoes nao traz o nome do fluxo."""
    nomes, cursor, paginas = {}, None, 0
    while paginas < MAX_PAGES:
        params = {"limit": PAGE_LIMIT}
        if cursor:
            params["cursor"] = cursor
        try:
            dados = _requisitar(f"{base}/api/v1/workflows?{urllib.parse.urlencode(params)}", api_key, timeout)
        except Exception:  # noqa: BLE001 - nome e enfeite, nunca derruba a coleta
            break
        for wf in dados.get("data") or []:
            nomes[str(wf.get("id"))] = wf.get("name") or ""
        cursor = dados.get("nextCursor")
        paginas += 1
        if not cursor:
            break
    return nomes


def classificar(msg: str):
    for padrao, rotulo, acao in PADROES_CAUSA:
        if re.search(padrao, msg or "", re.IGNORECASE):
            return rotulo, acao
    return "nao-classificado", "Abrir a execucao no n8n e inspecionar o no que falhou."


def coletar(nome, base, api_key, desde, timeout):
    resultado = {
        "instancia": nome, "url": base, "erros": 0, "sucessos": 0,
        "fluxos": [], "retencao_mais_antiga": None, "falha": None,
    }
    try:
        erros = buscar_execucoes(base, api_key, "error", desde, timeout)
        sucessos = buscar_execucoes(base, api_key, "success", desde, timeout)
    except urllib.error.HTTPError as exc:
        resultado["falha"] = f"HTTP {exc.code} ao consultar a API"
        return resultado
    except Exception as exc:  # noqa: BLE001
        resultado["falha"] = f"{type(exc).__name__}: {exc}"
        return resultado

    resultado["erros"] = len(erros)
    resultado["sucessos"] = len(sucessos)
    nomes = nomes_de_workflows(base, api_key, timeout)

    datas = [_parse_data(e.get("startedAt")) for e in erros + sucessos]
    datas = [d for d in datas if d]
    if datas:
        resultado["retencao_mais_antiga"] = min(datas).isoformat()

    por_fluxo = {}
    for ex in erros:
        wid = str(ex.get("workflowId") or "?")
        alvo = por_fluxo.setdefault(wid, {
            "workflow_id": wid,
            "nome": (ex.get("workflowData") or {}).get("name") or ex.get("workflowName")
                    or nomes.get(wid) or "",
            "erros": 0, "sucessos": 0, "amostras": [],
        })
        alvo["erros"] += 1
        if len(alvo["amostras"]) < SAMPLES_POR_FLUXO:
            alvo["amostras"].append(ex.get("id"))
    for ex in sucessos:
        wid = str(ex.get("workflowId") or "?")
        if wid in por_fluxo:
            por_fluxo[wid]["sucessos"] += 1

    for fluxo in sorted(por_fluxo.values(), key=lambda f: -f["erros"]):
        for exec_id in fluxo.pop("amostras", []):
            msg, no = mensagem_de_erro(base, api_key, exec_id, timeout)
            rotulo, acao = classificar(msg)
            fluxo["causa"] = rotulo
            fluxo["acao"] = acao
            fluxo["no"] = no
            fluxo["mensagem"] = msg
            fluxo["execucao_exemplo"] = exec_id
            break
        resultado["fluxos"].append(fluxo)
    return resultado


def diffar(atual, anterior):
    """Compara com a coleta anterior: fluxos novos quebrando, resolvidos e agravados."""
    if not anterior:
        return {"primeira_coleta": True, "novos": [], "resolvidos": [], "agravados": [], "melhorados": []}
    def indexar(snap):
        idx = {}
        for inst in snap.get("instancias", []):
            for f in inst.get("fluxos", []):
                idx[(inst["instancia"], f["workflow_id"])] = f
        return idx
    a, b = indexar(atual), indexar(anterior)
    novos, agravados, melhorados = [], [], []
    for chave, f in a.items():
        antigo = b.get(chave)
        item = {"instancia": chave[0], "workflow_id": chave[1],
                "nome": f.get("nome"), "erros": f["erros"],
                "causa": f.get("causa"), "antes": (antigo or {}).get("erros", 0)}
        if antigo is None:
            novos.append(item)
        elif f["erros"] > antigo["erros"] * 1.5 and f["erros"] - antigo["erros"] >= 5:
            agravados.append(item)
        elif f["erros"] < antigo["erros"] * 0.5:
            melhorados.append(item)
    resolvidos = [
        {"instancia": k[0], "workflow_id": k[1], "nome": f.get("nome"), "antes": f["erros"]}
        for k, f in b.items() if k not in a
    ]
    return {"primeira_coleta": False, "novos": novos, "resolvidos": resolvidos,
            "agravados": agravados, "melhorados": melhorados}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workspace", default=str(DEFAULT_WORKSPACE), help="raiz do workspace com o .env")
    ap.add_argument("--hours", type=int, default=24, help="janela em horas (padrao 24)")
    ap.add_argument("--instance", action="append", default=[], help="limitar a uma instancia (repetivel)")
    ap.add_argument("--timeout", type=int, default=45, help="timeout por request em segundos")
    ap.add_argument("--json-out", help="grava o JSON aqui em vez do stdout")
    ap.add_argument("--state-dir", default=str(Path.home() / ".hermes" / "radar-n8n"),
                    help="onde guardar o snapshot anterior para o diff")
    args = ap.parse_args()

    workspace = Path(os.path.expanduser(args.workspace))
    env = carregar_env(workspace)
    alvos = instancias_de(env)
    if args.instance:
        querem = {i.upper() for i in args.instance}
        alvos = {k: v for k, v in alvos.items() if k in querem}

    agora = datetime.now(timezone.utc)
    desde = agora - timedelta(hours=args.hours)
    saida = {
        "gerado_em": agora.isoformat(),
        "janela_horas": args.hours,
        "janela_inicio": desde.isoformat(),
        "instancias": [],
    }

    if not alvos:
        saida["erro_fatal"] = (
            f"Nenhuma instancia com N8N_<X>_API_URL e N8N_<X>_API_KEY preenchidos em {workspace / '.env'}"
        )
    else:
        for nome, (base, key) in sorted(alvos.items()):
            saida["instancias"].append(coletar(nome, base, key, desde, args.timeout))

    total_e = sum(i["erros"] for i in saida["instancias"])
    total_s = sum(i["sucessos"] for i in saida["instancias"])
    saida["total"] = {
        "erros": total_e, "sucessos": total_s, "execucoes": total_e + total_s,
        "taxa_erro": round(100 * total_e / (total_e + total_s), 1) if (total_e + total_s) else 0.0,
    }

    state_dir = Path(os.path.expanduser(args.state_dir))
    state_dir.mkdir(parents=True, exist_ok=True)
    anterior_path = state_dir / "ultimo.json"
    anterior = None
    if anterior_path.is_file():
        try:
            anterior = json.loads(anterior_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            anterior = None
    saida["diff"] = diffar(saida, anterior)
    if not saida.get("erro_fatal"):
        anterior_path.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
        historico = state_dir / "historico.jsonl"
        with historico.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "gerado_em": saida["gerado_em"],
                "total": saida["total"],
                "por_instancia": {i["instancia"]: {"erros": i["erros"], "sucessos": i["sucessos"]}
                                  for i in saida["instancias"]},
            }, ensure_ascii=False) + "\n")

    texto = json.dumps(saida, ensure_ascii=False, indent=2)
    if args.json_out:
        Path(os.path.expanduser(args.json_out)).write_text(texto, encoding="utf-8")
        print(f"JSON gravado em {args.json_out} — {total_e} erros / {total_e + total_s} execucoes")
    else:
        print(texto)
    return 1 if saida.get("erro_fatal") else 0


if __name__ == "__main__":
    sys.exit(main())
