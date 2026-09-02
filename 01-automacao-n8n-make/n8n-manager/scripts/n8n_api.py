#!/usr/bin/env python3
import os
import sys
import json
import argparse
import urllib.request
import urllib.parse
from urllib.error import HTTPError, URLError

def load_env(env_path='.env'):
    config = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    config[key] = val
    return config

def make_request(url, method='GET', data=None, headers=None):
    if data is not None:
        req_body = json.dumps(data).encode('utf-8')
    else:
        req_body = None

    req = urllib.request.Request(url, data=req_body, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)

    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            if res_body:
                return response.status, json.loads(res_body)
            else:
                return response.status, {}
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            err_json = json.loads(error_body)
        except Exception:
            err_json = {"message": error_body}
        return e.code, err_json
    except URLError as e:
        return 500, {"message": str(e.reason)}

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    # Attempt to load .env from the current working directory
    env = load_env()

    # Fallback to check parent directory if .env not found
    if not env:
        env = load_env('../.env')

    # Fallback final: .env na raiz do workspace (4 níveis acima deste script)
    if not env:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_root = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))
        env = load_env(os.path.join(workspace_root, '.env'))

    # Seleção da instância: `--instance <NOME>` ou variável de ambiente N8N_INSTANCE.
    # É obrigatório: sem isso não dá pra saber se a chamada vai para a instância
    # pessoal do desenvolvedor ou de um cliente/ambiente.
    instance = os.environ.get('N8N_INSTANCE', '').strip().upper()
    if '--instance' in sys.argv:
        i = sys.argv.index('--instance')
        if i + 1 < len(sys.argv):
            instance = sys.argv[i + 1].strip().upper()
            del sys.argv[i:i + 2]

    disponiveis = sorted(
        k[len('N8N_'):-len('_API_URL')]
        for k in env
        if k.startswith('N8N_') and k.endswith('_API_URL')
    )

    if not instance:
        print(json.dumps({
            "error": "Instância não informada. Use --instance <NOME> ou a variável N8N_INSTANCE.",
            "disponiveis": disponiveis,
        }), file=sys.stderr)
        sys.exit(1)

    api_url = env.get(f'N8N_{instance}_API_URL')
    api_key = env.get(f'N8N_{instance}_API_KEY')

    if not api_url or not api_key:
        print(json.dumps({
            "error": f"N8N_{instance}_API_URL / N8N_{instance}_API_KEY não encontrados no .env.",
            "disponiveis": disponiveis,
        }), file=sys.stderr)
        sys.exit(1)

    # Aceita a URL com ou sem o sufixo /api/v1 — o launcher do MCP usa a base pura,
    # este script fala direto com a Public API.
    api_url = api_url.rstrip('/')
    if not api_url.endswith('/api/v1'):
        api_url = f"{api_url}/api/v1"

    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    parser = argparse.ArgumentParser(description="CLI to manage workflows on n8n instance.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list-workflows
    list_parser = subparsers.add_parser("list-workflows", help="List all workflows.")
    list_parser.add_argument("--name", help="Filter by workflow name.")
    list_parser.add_argument("--active", choices=["true", "false"], help="Filter by active status.")
    list_parser.add_argument("--limit", type=int, default=100, help="Maximum number of items to return.")
    list_parser.add_argument("--cursor", help="Pagination cursor.")

    # get-workflow
    get_parser = subparsers.add_parser("get-workflow", help="Retrieve workflow details.")
    get_parser.add_argument("id", help="The ID of the workflow.")
    get_parser.add_argument("--exclude-pinned", action="store_true", help="Avoid retrieving pinned data.")

    # create-workflow
    create_parser = subparsers.add_parser("create-workflow", help="Create a new workflow.")
    create_parser.add_argument("json_file", help="Path to JSON file containing the workflow details.")

    # update-workflow
    update_parser = subparsers.add_parser("update-workflow", help="Update an existing workflow.")
    update_parser.add_argument("id", help="The ID of the workflow to update.")
    update_parser.add_argument("json_file", help="Path to JSON file containing the updated workflow details.")

    # delete-workflow
    delete_parser = subparsers.add_parser("delete-workflow", help="Delete a workflow.")
    delete_parser.add_argument("id", help="The ID of the workflow to delete.")

    # activate-workflow
    activate_parser = subparsers.add_parser("activate-workflow", help="Activate/Publish a workflow.")
    activate_parser.add_argument("id", help="The ID of the workflow to activate.")

    # deactivate-workflow
    deactivate_parser = subparsers.add_parser("deactivate-workflow", help="Deactivate a workflow.")
    deactivate_parser.add_argument("id", help="The ID of the workflow to deactivate.")

    # list-executions
    list_exec_parser = subparsers.add_parser("list-executions", help="List workflow executions.")
    list_exec_parser.add_argument("--workflow-id", help="Filter by workflow ID.")
    list_exec_parser.add_argument("--status", choices=["error", "success", "waiting"], help="Filter by execution status.")
    list_exec_parser.add_argument("--limit", type=int, default=20, help="Maximum number of items to return.")
    list_exec_parser.add_argument("--cursor", help="Pagination cursor.")

    # get-execution
    get_exec_parser = subparsers.add_parser("get-execution", help="Retrieve execution details (including node error data with --include-data).")
    get_exec_parser.add_argument("id", help="The ID of the execution.")
    get_exec_parser.add_argument("--include-data", action="store_true", help="Include full execution data (node inputs/outputs and error details).")

    args = parser.parse_args()

    if args.command == "list-workflows":
        query_params = {}
        if args.name:
            query_params["name"] = args.name
        if args.active:
            query_params["active"] = "true" if args.active == "true" else "false"
        if args.limit:
            query_params["limit"] = args.limit
        if args.cursor:
            query_params["cursor"] = args.cursor

        url = f"{api_url}/workflows"
        if query_params:
            url = f"{url}?{urllib.parse.urlencode(query_params)}"

        status, response = make_request(url, 'GET', headers=headers)
        if status == 200:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"status": status, "error": response}), file=sys.stderr)
            sys.exit(1)

    elif args.command == "get-workflow":
        url = f"{api_url}/workflows/{args.id}"
        if args.exclude_pinned:
            url = f"{url}?excludePinnedData=true"

        status, response = make_request(url, 'GET', headers=headers)
        if status == 200:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"status": status, "error": response}), file=sys.stderr)
            sys.exit(1)

    elif args.command == "create-workflow":
        if not os.path.exists(args.json_file):
            print(json.dumps({"error": f"JSON payload file not found: {args.json_file}"}), file=sys.stderr)
            sys.exit(1)
        with open(args.json_file, 'r', encoding='utf-8') as f:
            try:
                payload = json.load(f)
            except json.JSONDecodeError as e:
                print(json.dumps({"error": f"Invalid JSON format: {str(e)}"}), file=sys.stderr)
                sys.exit(1)

        url = f"{api_url}/workflows"
        status, response = make_request(url, 'POST', data=payload, headers=headers)
        if status == 200 or status == 201:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"status": status, "error": response}), file=sys.stderr)
            sys.exit(1)

    elif args.command == "update-workflow":
        if not os.path.exists(args.json_file):
            print(json.dumps({"error": f"JSON payload file not found: {args.json_file}"}), file=sys.stderr)
            sys.exit(1)
        with open(args.json_file, 'r', encoding='utf-8') as f:
            try:
                payload = json.load(f)
            except json.JSONDecodeError as e:
                print(json.dumps({"error": f"Invalid JSON format: {str(e)}"}), file=sys.stderr)
                sys.exit(1)

        url = f"{api_url}/workflows/{args.id}"
        status, response = make_request(url, 'PUT', data=payload, headers=headers)
        if status == 200:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"status": status, "error": response}), file=sys.stderr)
            sys.exit(1)

    elif args.command == "delete-workflow":
        url = f"{api_url}/workflows/{args.id}"
        status, response = make_request(url, 'DELETE', headers=headers)
        if status == 200:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"status": status, "error": response}), file=sys.stderr)
            sys.exit(1)

    elif args.command == "activate-workflow":
        url = f"{api_url}/workflows/{args.id}/activate"
        status, response = make_request(url, 'POST', data={}, headers=headers)
        if status == 200:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"status": status, "error": response}), file=sys.stderr)
            sys.exit(1)

    elif args.command == "deactivate-workflow":
        url = f"{api_url}/workflows/{args.id}/deactivate"
        status, response = make_request(url, 'POST', data={}, headers=headers)
        if status == 200:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"status": status, "error": response}), file=sys.stderr)
            sys.exit(1)

    elif args.command == "list-executions":
        query_params = {"limit": args.limit}
        if args.workflow_id:
            query_params["workflowId"] = args.workflow_id
        if args.status:
            query_params["status"] = args.status
        if args.cursor:
            query_params["cursor"] = args.cursor

        url = f"{api_url}/executions?{urllib.parse.urlencode(query_params)}"
        status, response = make_request(url, 'GET', headers=headers)
        if status == 200:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"status": status, "error": response}), file=sys.stderr)
            sys.exit(1)

    elif args.command == "get-execution":
        url = f"{api_url}/executions/{args.id}"
        if args.include_data:
            url = f"{url}?includeData=true"

        status, response = make_request(url, 'GET', headers=headers)
        if status == 200:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"status": status, "error": response}), file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
