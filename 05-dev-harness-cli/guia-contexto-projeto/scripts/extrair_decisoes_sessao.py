#!/usr/bin/env python3
"""Lista pergunta -> resposta dos clarify de uma sessão Hermes (somente leitura).

Uso: python3 extrair_decisoes_sessao.py <session_id> [<session_id> ...]
As respostas do usuário a formulários clarify ficam em mensagens role='tool',
tool_name='clarify', que a busca de sessões não mostra por padrão.
"""
import datetime
import json
import os
import sqlite3
import sys

DB = os.path.expanduser('~/.hermes/state.db')


def main(ids):
    con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    for sid in ids:
        print(f'===== {sid}')
        seen = set()
        rows = con.execute(
            "select id, timestamp, content from messages "
            "where session_id=? and role='tool' and tool_name='clarify' order by id",
            (sid,),
        )
        for mid, ts, content in rows:
            try:
                data = json.loads(content)
            except (TypeError, ValueError):
                continue
            for r in data.get('responses', []):
                key = (r.get('question'), r.get('user_response'))
                if key in seen:
                    continue
                seen.add(key)
                when = datetime.datetime.fromtimestamp(ts).strftime('%d/%m %H:%M')
                q = (r.get('question') or '').replace('\n', ' ')[:300]
                print(f'[{mid} {when}] Q: {q}\n   -> {r.get("status")}: {r.get("user_response")}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
