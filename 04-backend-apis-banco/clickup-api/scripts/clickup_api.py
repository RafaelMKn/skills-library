#!/usr/bin/env python3
import os
import sys
import json
import argparse
import urllib.request
import urllib.parse
from pathlib import Path
from urllib.error import HTTPError, URLError

BASE_URL = "https://api.clickup.com/api/v2"
BASE_URL_V3 = "https://api.clickup.com/api/v3"


def find_and_load_env():
    if os.environ.get("CLICKUP_API_TOKEN"):
        return os.environ.get("CLICKUP_API_TOKEN")

    curr = Path.cwd()
    for directory in [curr, *curr.parents]:
        env_file = directory / ".env"
        if env_file.is_file():
            try:
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("\"'")
                    if k == "CLICKUP_API_TOKEN" and v:
                        return v
            except Exception:
                pass

    return None


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


def load_json_file(path):
    if not os.path.exists(path):
        print(json.dumps({"error": f"JSON payload file not found: {path}"}), file=sys.stderr)
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON format: {str(e)}"}), file=sys.stderr)
            sys.exit(1)


def emit(status, response, ok_statuses=(200, 201)):
    if status in ok_statuses:
        print(json.dumps(response, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({"status": status, "error": response}), file=sys.stderr)
        sys.exit(1)


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="CLI genérica para interagir com a API REST v2 do ClickUp.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-workspaces", help="List authorized workspaces (teams).")

    members_parser = subparsers.add_parser("list-members", help="List members in a workspace (team).")
    members_parser.add_argument("team_id", help="Workspace (team) ID.")

    shared_parser = subparsers.add_parser(
        "list-shared",
        help="List the shared hierarchy (folders/lists/tasks shared with guest/token owner).")
    shared_parser.add_argument("team_id", help="Workspace (team) ID.")

    spaces_parser = subparsers.add_parser("list-spaces", help="List spaces in a workspace.")
    spaces_parser.add_argument("team_id", help="Workspace (team) ID.")
    spaces_parser.add_argument("--archived", choices=["true", "false"], default="false")

    folders_parser = subparsers.add_parser("list-folders", help="List folders in a space.")
    folders_parser.add_argument("space_id", help="Space ID.")
    folders_parser.add_argument("--archived", choices=["true", "false"], default="false")

    lists_parser = subparsers.add_parser("list-lists", help="List lists inside a folder.")
    lists_parser.add_argument("folder_id", help="Folder ID.")
    lists_parser.add_argument("--archived", choices=["true", "false"], default="false")

    folderless_parser = subparsers.add_parser("list-folderless-lists", help="List folderless lists in a space.")
    folderless_parser.add_argument("space_id", help="Space ID.")
    folderless_parser.add_argument("--archived", choices=["true", "false"], default="false")

    fields_parser = subparsers.add_parser("list-custom-fields", help="List custom fields available on a list.")
    fields_parser.add_argument("list_id", help="List ID.")

    tasks_parser = subparsers.add_parser("list-tasks", help="List tasks in a list.")
    tasks_parser.add_argument("list_id", help="List ID.")
    tasks_parser.add_argument("--include-closed", action="store_true")
    tasks_parser.add_argument("--page", type=int, default=0)
    tasks_parser.add_argument("--statuses", action="append", help="Filter by status. Can be passed multiple times.")

    get_task_parser = subparsers.add_parser("get-task", help="Get a single task.")
    get_task_parser.add_argument("task_id", help="Task ID.")

    create_task_parser = subparsers.add_parser("create-task", help="Create a task in a list.")
    create_task_parser.add_argument("list_id", help="List ID.")
    create_task_parser.add_argument("json_file", help="Path to JSON file with task fields (name, description, assignees, status, priority, due_date, ...).")

    update_task_parser = subparsers.add_parser("update-task", help="Update a task.")
    update_task_parser.add_argument("task_id", help="Task ID.")
    update_task_parser.add_argument("json_file", help="Path to JSON file with fields to update.")

    delete_task_parser = subparsers.add_parser("delete-task", help="Delete a task.")
    delete_task_parser.add_argument("task_id", help="Task ID.")

    set_field_parser = subparsers.add_parser(
        "set-custom-field",
        help="Set a custom field on a task (custom fields do NOT go through update-task).",
    )
    set_field_parser.add_argument("task_id", help="Task ID.")
    set_field_parser.add_argument("field_id", help="Custom field UUID.")
    set_field_parser.add_argument(
        "value",
        help="Field value. For labels/multi-select pass the option UUID; for drop_down the option "
             "orderindex; for date the timestamp in ms. Repeat with --json to send a raw JSON value.",
    )
    set_field_parser.add_argument(
        "--json",
        action="store_true",
        help="Parse the value argument as JSON instead of a plain string (use for arrays and numbers).",
    )

    delete_list_parser = subparsers.add_parser("delete-list", help="Delete a list (irreversible).")
    delete_list_parser.add_argument("list_id", help="List ID.")

    list_comments_parser = subparsers.add_parser("list-comments", help="List comments on a task.")
    list_comments_parser.add_argument("task_id", help="Task ID.")

    add_comment_parser = subparsers.add_parser("add-comment", help="Add a comment to a task.")
    add_comment_parser.add_argument("task_id", help="Task ID.")
    add_comment_parser.add_argument("comment_text", help="Comment text.")
    add_comment_parser.add_argument("--notify-all", action="store_true")
    add_comment_parser.add_argument("--assignee", help="User ID to assign the comment to (creates a notification).")

    create_checklist_parser = subparsers.add_parser("create-checklist", help="Create a checklist on a task.")
    create_checklist_parser.add_argument("task_id", help="Task ID.")
    create_checklist_parser.add_argument("name", help="Checklist name.")

    add_checklist_item_parser = subparsers.add_parser("add-checklist-item", help="Add an item to a checklist.")
    add_checklist_item_parser.add_argument("checklist_id", help="Checklist ID.")
    add_checklist_item_parser.add_argument("name", help="Item text.")

    update_checklist_item_parser = subparsers.add_parser(
        "update-checklist-item",
        help="Update a checklist item (mark resolved/unresolved, rename).",
    )
    update_checklist_item_parser.add_argument("checklist_id", help="Checklist ID.")
    update_checklist_item_parser.add_argument("item_id", help="Checklist item ID.")
    update_checklist_item_parser.add_argument("--name", help="New item text.")
    update_checklist_item_parser.add_argument("--resolved", dest="resolved", action="store_true")
    update_checklist_item_parser.add_argument("--unresolved", dest="resolved", action="store_false")
    update_checklist_item_parser.set_defaults(resolved=None)

    delete_checklist_parser = subparsers.add_parser("delete-checklist", help="Delete a checklist.")
    delete_checklist_parser.add_argument("checklist_id", help="Checklist ID.")

    list_tags_parser = subparsers.add_parser("list-tags", help="List tags defined in a space.")
    list_tags_parser.add_argument("space_id", help="Space ID.")

    create_tag_parser = subparsers.add_parser("create-tag", help="Create a tag in a space.")
    create_tag_parser.add_argument("space_id", help="Space ID.")
    create_tag_parser.add_argument("name", help="Tag name.")
    create_tag_parser.add_argument("--fg", default="#000000", help="Foreground color hex.")
    create_tag_parser.add_argument("--bg", default="#ffc53d", help="Background color hex.")

    add_task_tag_parser = subparsers.add_parser("add-task-tag", help="Add a tag to a task (creates the tag in the space if it doesn't exist yet).")
    add_task_tag_parser.add_argument("task_id", help="Task ID.")
    add_task_tag_parser.add_argument("name", help="Tag name.")

    remove_task_tag_parser = subparsers.add_parser("remove-task-tag", help="Remove a tag from a task.")
    remove_task_tag_parser.add_argument("task_id", help="Task ID.")
    remove_task_tag_parser.add_argument("name", help="Tag name.")

    list_webhooks_parser = subparsers.add_parser("list-webhooks", help="List webhooks for a workspace.")
    list_webhooks_parser.add_argument("team_id", help="Workspace (team) ID.")

    create_webhook_parser = subparsers.add_parser("create-webhook", help="Create a webhook for a workspace.")
    create_webhook_parser.add_argument("team_id", help="Workspace (team) ID.")
    create_webhook_parser.add_argument("json_file", help="Path to JSON file with endpoint/events/space_id etc.")

    # --- Docs (API v3) ---
    list_docs_parser = subparsers.add_parser("list-docs", help="Search/list Docs in a workspace (API v3).")
    list_docs_parser.add_argument("workspace_id", help="Workspace (team) ID.")
    list_docs_parser.add_argument("--query", help="Search term matched against doc names.")
    list_docs_parser.add_argument("--limit", type=int, default=50)
    list_docs_parser.add_argument("--next-cursor", help="Cursor for the next page.")

    doc_pages_parser = subparsers.add_parser("list-doc-pages", help="List pages (listing) of a Doc.")
    doc_pages_parser.add_argument("workspace_id", help="Workspace (team) ID.")
    doc_pages_parser.add_argument("doc_id", help="Doc ID.")
    doc_pages_parser.add_argument("--max-page-depth", type=int, default=-1)

    get_page_parser = subparsers.add_parser("get-doc-page", help="Get a single Doc page with content.")
    get_page_parser.add_argument("workspace_id", help="Workspace (team) ID.")
    get_page_parser.add_argument("doc_id", help="Doc ID.")
    get_page_parser.add_argument("page_id", help="Page ID.")
    get_page_parser.add_argument("--content-format", default="text/md", choices=["text/md", "text/plain"])

    args = parser.parse_args()

    api_token = find_and_load_env()
    if not api_token:
        print(json.dumps({
            "error": "CLICKUP_API_TOKEN não encontrado nas variáveis de ambiente ou em arquivos .env.",
            "help": "Defina CLICKUP_API_TOKEN no seu arquivo .env ou como variável de ambiente (formato: pk_...)."
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    headers = {
        'Authorization': api_token,
        'Content-Type': 'application/json'
    }

    if args.command == "list-workspaces":
        status, response = make_request(f"{BASE_URL}/team", 'GET', headers=headers)
        emit(status, response)

    elif args.command == "list-members":
        status, response = make_request(f"{BASE_URL}/team", 'GET', headers=headers)
        if status == 200:
            teams = response.get("teams", [])
            for t in teams:
                if str(t.get("id")) == str(args.team_id):
                    emit(200, {"team_id": args.team_id, "name": t.get("name"), "members": t.get("members", [])})
                    return
            emit(404, {"error": f"Workspace (team) {args.team_id} não encontrado."})
        else:
            emit(status, response)

    elif args.command == "list-shared":
        url = f"{BASE_URL}/team/{args.team_id}/shared"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)

    elif args.command == "list-spaces":
        url = f"{BASE_URL}/team/{args.team_id}/space?{urllib.parse.urlencode({'archived': args.archived})}"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)

    elif args.command == "list-folders":
        url = f"{BASE_URL}/space/{args.space_id}/folder?{urllib.parse.urlencode({'archived': args.archived})}"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)

    elif args.command == "list-lists":
        url = f"{BASE_URL}/folder/{args.folder_id}/list?{urllib.parse.urlencode({'archived': args.archived})}"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)

    elif args.command == "list-folderless-lists":
        url = f"{BASE_URL}/space/{args.space_id}/list?{urllib.parse.urlencode({'archived': args.archived})}"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)

    elif args.command == "list-custom-fields":
        url = f"{BASE_URL}/list/{args.list_id}/field"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)

    elif args.command == "list-tasks":
        query_params = {"page": args.page}
        if args.include_closed:
            query_params["include_closed"] = "true"
        if args.statuses:
            query_params["statuses[]"] = args.statuses
        url = f"{BASE_URL}/list/{args.list_id}/task?{urllib.parse.urlencode(query_params, doseq=True)}"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)

    elif args.command == "get-task":
        url = f"{BASE_URL}/task/{args.task_id}"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)

    elif args.command == "create-task":
        payload = load_json_file(args.json_file)
        url = f"{BASE_URL}/list/{args.list_id}/task"
        status, response = make_request(url, 'POST', data=payload, headers=headers)
        emit(status, response)

    elif args.command == "set-custom-field":
        if args.json:
            try:
                value = json.loads(args.value)
            except ValueError as exc:
                emit(400, {"error": f"--json passado mas o valor não é JSON válido: {exc}"})
                return
        else:
            value = args.value
        payload = {"value": value}
        url = f"{BASE_URL}/task/{args.task_id}/field/{args.field_id}"
        status, response = make_request(url, 'POST', data=payload, headers=headers)
        emit(status, response)

    elif args.command == "update-task":
        payload = load_json_file(args.json_file)
        url = f"{BASE_URL}/task/{args.task_id}"
        status, response = make_request(url, 'PUT', data=payload, headers=headers)
        emit(status, response)

    elif args.command == "delete-task":
        url = f"{BASE_URL}/task/{args.task_id}"
        status, response = make_request(url, 'DELETE', headers=headers)
        emit(status, response)

    elif args.command == "list-comments":
        url = f"{BASE_URL}/task/{args.task_id}/comment"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)

    elif args.command == "add-comment":
        payload = {"comment_text": args.comment_text, "notify_all": bool(args.notify_all)}
        if getattr(args, "assignee", None):
            payload["assignee"] = int(args.assignee)
        url = f"{BASE_URL}/task/{args.task_id}/comment"
        status, response = make_request(url, 'POST', data=payload, headers=headers)
        emit(status, response)

    elif args.command == "delete-list":
        url = f"{BASE_URL}/list/{args.list_id}"
        status, response = make_request(url, 'DELETE', headers=headers)
        emit(status, response)

    elif args.command == "create-checklist":
        payload = {"name": args.name}
        url = f"{BASE_URL}/task/{args.task_id}/checklist"
        status, response = make_request(url, 'POST', data=payload, headers=headers)
        emit(status, response)

    elif args.command == "update-checklist-item":
        payload = {}
        if args.name is not None:
            payload["name"] = args.name
        if args.resolved is not None:
            payload["resolved"] = args.resolved
        if not payload:
            emit(400, {"error": "nada para atualizar: passe --name e/ou --resolved/--unresolved"})
            return
        url = f"{BASE_URL}/checklist/{args.checklist_id}/checklist_item/{args.item_id}"
        status, response = make_request(url, 'PUT', data=payload, headers=headers)
        emit(status, response)

    elif args.command == "add-checklist-item":
        payload = {"name": args.name}
        url = f"{BASE_URL}/checklist/{args.checklist_id}/checklist_item"
        status, response = make_request(url, 'POST', data=payload, headers=headers)
        emit(status, response)

    elif args.command == "delete-checklist":
        url = f"{BASE_URL}/checklist/{args.checklist_id}"
        status, response = make_request(url, 'DELETE', headers=headers)
        emit(status, response)

    elif args.command == "list-tags":
        url = f"{BASE_URL}/space/{args.space_id}/tag"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)

    elif args.command == "create-tag":
        payload = {"tag": {"name": args.name, "tag_fg": args.fg, "tag_bg": args.bg}}
        url = f"{BASE_URL}/space/{args.space_id}/tag"
        status, response = make_request(url, 'POST', data=payload, headers=headers)
        emit(status, response)

    elif args.command == "add-task-tag":
        url = f"{BASE_URL}/task/{args.task_id}/tag/{urllib.parse.quote(args.name)}"
        status, response = make_request(url, 'POST', headers=headers)
        emit(status, response)

    elif args.command == "remove-task-tag":
        url = f"{BASE_URL}/task/{args.task_id}/tag/{urllib.parse.quote(args.name)}"
        status, response = make_request(url, 'DELETE', headers=headers)
        emit(status, response)

    elif args.command == "list-webhooks":
        url = f"{BASE_URL}/team/{args.team_id}/webhook"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)

    elif args.command == "create-webhook":
        payload = load_json_file(args.json_file)
        url = f"{BASE_URL}/team/{args.team_id}/webhook"
        status, response = make_request(url, 'POST', data=payload, headers=headers)
        emit(status, response)

    elif args.command == "list-docs":
        query_params = {"limit": args.limit}
        if args.query:
            query_params["query"] = args.query
        if args.next_cursor:
            query_params["next_cursor"] = args.next_cursor
        url = f"{BASE_URL_V3}/workspaces/{args.workspace_id}/docs?{urllib.parse.urlencode(query_params)}"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)

    elif args.command == "list-doc-pages":
        query_params = {"max_page_depth": args.max_page_depth}
        url = f"{BASE_URL_V3}/workspaces/{args.workspace_id}/docs/{args.doc_id}/pageListing?{urllib.parse.urlencode(query_params)}"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)

    elif args.command == "get-doc-page":
        query_params = {"content_format": args.content_format}
        url = f"{BASE_URL_V3}/workspaces/{args.workspace_id}/docs/{args.doc_id}/pages/{args.page_id}?{urllib.parse.urlencode(query_params)}"
        status, response = make_request(url, 'GET', headers=headers)
        emit(status, response)


if __name__ == "__main__":
    main()
