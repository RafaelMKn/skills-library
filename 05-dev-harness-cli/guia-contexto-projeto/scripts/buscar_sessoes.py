#!/usr/bin/env python3
"""Acha sessões Hermes por termo/cwd e exporta uma sessão rotulada (somente leitura).

Uso:
  buscar_sessoes.py <termo> [<termo> ...]       lista sessões cujo cwd ou mensagens contêm o termo
  buscar_sessoes.py --dump <session_id> <saida.md>  exporta user/assistant/clarify, sem duplicatas
"""
import datetime
import os
import sqlite3
import sys

DB = os.path.expanduser('~/.hermes/state.db')


def fmt(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%d/%m %H:%M') if ts else '-'


def con():
    return sqlite3.connect(f'file:{DB}?mode=ro', uri=True)


def buscar(termos):
    c = con()
    achadas = {}
    for t in termos:
        like = f'%{t}%'
        for sid, ts, title, cwd in c.execute(
                'select id, started_at, title, cwd from sessions where cwd like ?', (like,)):
            achadas.setdefault(sid, [ts, title, cwd, 0])
        for sid, ts, title, cwd, n in c.execute(
                'select s.id, s.started_at, s.title, s.cwd, count(*) from messages m '
                'join sessions s on s.id = m.session_id where m.content like ? group by s.id', (like,)):
            achadas.setdefault(sid, [ts, title, cwd, 0])[3] += n
    for sid, (ts, title, cwd, n) in sorted(achadas.items(), key=lambda kv: kv[1][0] or 0):
        print(f'{sid}\t{fmt(ts)}\t{n} msgs\t{title}\t{cwd}')


def dump(sid, saida):
    c = con()
    vistos = set()
    with open(saida, 'w') as out:
        for mid, role, ts, content, tool in c.execute(
                'select id, role, timestamp, content, tool_name from messages '
                'where session_id=? order by id', (sid,)):
            if not content or (role == 'tool' and tool != 'clarify'):
                continue
            rotulo = 'clarify (respostas do usuário)' if role == 'tool' else role
            chave = (role, content[:300])
            if chave in vistos:
                continue
            vistos.add(chave)
            out.write(f'\n## [{mid}] {rotulo} {fmt(ts)}\n{content}\n')
    print(saida)


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == '--dump':
        dump(a[1], a[2])
    elif a and a[0] != '--dump':
        buscar(a)
    else:
        sys.exit(__doc__)
