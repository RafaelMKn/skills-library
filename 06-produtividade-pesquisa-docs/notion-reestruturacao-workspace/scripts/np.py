"""Notion REST via `composio proxy`. Uso: import np; np.call('users/me').
Conta: env NOTION_ACCOUNT (alias ou word_id de `composio connections list --toolkit notion`)."""
import json, os, subprocess, tempfile

ENV = dict(os.environ)
ENV.pop("COMPOSIO_API_KEY", None)  # exportada quebra a CLI
ENV["PATH"] = os.path.expanduser("~/.local/bin") + ":" + ENV.get("PATH", "")
ACCOUNT = os.environ.get("NOTION_ACCOUNT", "<conta>")
VERSION = "2025-09-03"


def call(path, method="GET", body=None, version=VERSION):
    url = path if path.startswith("http") else "https://api.notion.com/v1/" + path.lstrip("/")
    cmd = ["composio", "proxy", url, "--toolkit", "notion", "--account", ACCOUNT,
           "-X", method, "-H", f"Notion-Version: {version}", "-H", "Content-Type: application/json"]
    if body is not None:
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(body, f); f.close()
        cmd += ["-d", "@" + f.name]
    out = subprocess.run(cmd, capture_output=True, text=True, env=ENV, timeout=120).stdout
    d = json.loads(out[out.find("{"):])
    if isinstance(d, dict) and "data" in d and "status" in d and isinstance(d.get("data"), (dict, list)):
        d = d["data"]
    if isinstance(d, dict) and d.get("storedInFile"):
        return json.load(open(d["outputFilePath"]))
    return d


def search_all(kind=None):
    res, cur = [], None
    while True:
        body = {"page_size": 100}
        if kind:
            body["filter"] = {"property": "object", "value": kind}
        if cur:
            body["start_cursor"] = cur
        d = call("search", "POST", body)
        res += d.get("results", [])
        if not d.get("has_more"):
            return res
        cur = d["next_cursor"]


def title_of(o):
    if o.get("object") in ("data_source", "database"):
        return "".join(t.get("plain_text", "") for t in o.get("title", []))
    for p in o.get("properties", {}).values():
        if p.get("type") == "title":
            return "".join(t.get("plain_text", "") for t in p["title"])
    return ""
