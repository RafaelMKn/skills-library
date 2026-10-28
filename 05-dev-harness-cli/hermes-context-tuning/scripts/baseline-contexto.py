#!/usr/bin/env python3
"""Baseline de contexto/custo da instalacao local do Hermes.

Le $HERMES_HOME/state.db em modo somente-leitura e reporta:
  - custo por modelo, separando actual (dinheiro) de estimated (tabela de precos)
  - contexto medio lido por chamada de API  -> a metrica que explica lentidao
  - taxa de cache hit e frequencia real de compressao
  - composicao do historico por role e por ferramenta

Uso:
    python3 baseline-contexto.py             # relatorio no stdout
    python3 baseline-contexto.py --save      # grava JSON carimbado em HERMES_HOME
    python3 baseline-contexto.py --db /caminho/para/state.db

Usa o sqlite3 da stdlib de proposito: o binario `sqlite3` pode nao estar instalado,
e a URI file:...?mode=ro garante leitura sem tocar numa sessao viva.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sqlite3
import sys


def default_db() -> str:
    home = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
    return os.path.join(home, "state.db")


def connect(path: str) -> sqlite3.Connection:
    if not os.path.exists(path):
        sys.exit(f"state.db nao encontrado em {path} (use --db)")
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def table_exists(cur: sqlite3.Cursor, name: str) -> bool:
    row = cur.execute(
        "select 1 from sqlite_master where type='table' and name=?", (name,)
    ).fetchone()
    return row is not None


def fmt(n) -> str:
    return f"{n or 0:,}"


def collect(cur: sqlite3.Cursor) -> dict:
    out: dict = {}

    if not table_exists(cur, "session_model_usage"):
        sys.exit("tabela session_model_usage ausente — versao de Hermes incompativel")

    totals = cur.execute(
        """select sum(api_call_count), sum(input_tokens), sum(output_tokens),
                  sum(cache_read_tokens), sum(estimated_cost_usd), sum(actual_cost_usd)
           from session_model_usage"""
    ).fetchone()
    calls, inp, outp, cache_rd, est, act = (v or 0 for v in totals)

    comp = (
        cur.execute(
            "select sum(api_call_count) from session_model_usage where task like 'compress%'"
        ).fetchone()[0]
        or 0
    )

    out["api_calls_total"] = calls
    out["input_tokens"] = inp
    out["output_tokens"] = outp
    out["cache_read_tokens"] = cache_rd
    out["contexto_medio_por_call_tokens"] = round((cache_rd + inp) / calls) if calls else 0
    out["cache_hit_pct"] = round(cache_rd / (cache_rd + inp) * 100, 2) if (cache_rd + inp) else 0.0
    out["compressoes_disparadas"] = comp
    out["compressao_pct_das_calls"] = round(comp / calls * 100, 3) if calls else 0.0
    out["custo_actual_usd"] = round(act, 2)
    out["custo_estimated_usd"] = round(est, 2)

    out["por_modelo"] = [
        {
            "modelo": m,
            "provider": p,
            "billing_mode": bm,
            "calls": c,
            "cache_read": cr,
            "actual_usd": round(a or 0, 4),
            "estimated_usd": round(e or 0, 4),
        }
        for m, p, bm, c, cr, a, e in cur.execute(
            """select model, billing_provider, billing_mode, sum(api_call_count),
                      sum(cache_read_tokens), sum(actual_cost_usd), sum(estimated_cost_usd)
               from session_model_usage
               group by model, billing_provider, billing_mode
               order by sum(api_call_count) desc limit 15"""
        ).fetchall()
    ]

    if table_exists(cur, "messages"):
        out["msg_por_role"] = {
            r: {"n": n, "chars": t or 0}
            for r, n, t in cur.execute(
                "select role, count(*), sum(length(content)) from messages group by role"
            ).fetchall()
        }
        out["top_tools_por_chars"] = {
            (tn or "?"): {"n": n, "chars": t or 0, "media": round((t or 0) / n) if n else 0}
            for tn, n, t in cur.execute(
                """select tool_name, count(*), sum(length(content))
                   from messages where role='tool'
                   group by tool_name order by 3 desc limit 10"""
            ).fetchall()
        }

    if table_exists(cur, "system_prompts"):
        sizes = sorted(
            len(p or "") for (p,) in cur.execute("select prompt from system_prompts")
        )
        if sizes:
            out["system_prompt_chars"] = {
                "n": len(sizes),
                "menor": sizes[0],
                "mediana": sizes[len(sizes) // 2],
                "maior": sizes[-1],
            }

    return out


def report(d: dict) -> None:
    print("=" * 66)
    print("BASELINE DE CONTEXTO — Hermes local")
    print("=" * 66)
    print(f"  chamadas de API            : {fmt(d['api_calls_total'])}")
    print(f"  CONTEXTO MEDIO POR CHAMADA : {fmt(d['contexto_medio_por_call_tokens'])} tokens  <-- metrica central")
    print(f"  cache hit                  : {d['cache_hit_pct']}%")
    print(f"  compressoes disparadas     : {d['compressoes_disparadas']} ({d['compressao_pct_das_calls']}% das chamadas)")
    print()
    print(f"  custo ACTUAL (dinheiro)    : ${d['custo_actual_usd']}")
    print(f"  custo ESTIMATED (teorico)  : ${d['custo_estimated_usd']}")
    if d["custo_actual_usd"] == 0 and d["custo_estimated_usd"] > 0:
        print("  >> actual=0: tudo em OAuth/assinatura. NAO reporte estimated como gasto.")
    print()

    sp = d.get("system_prompt_chars")
    if sp:
        print(f"  system prompt (mediana)    : {fmt(sp['mediana'])} chars (~{sp['mediana']//4} tok)")

    roles = d.get("msg_por_role") or {}
    if roles:
        tot = sum(v["chars"] for v in roles.values()) or 1
        print("\n  --- composicao do historico ---")
        for r, v in sorted(roles.items(), key=lambda kv: -kv[1]["chars"]):
            print(f"    {r:<10} n={v['n']:>6}  {fmt(v['chars']):>14} chars ({v['chars']/tot*100:5.1f}%)")

    tools = d.get("top_tools_por_chars") or {}
    if tools:
        print("\n  --- maiores consumidores (tool results) ---")
        for tn, v in tools.items():
            print(f"    {tn:<22} n={v['n']:>5}  {fmt(v['chars']):>12} chars  media={fmt(v['media'])}")

    print("\n  --- por modelo ---")
    for m in d["por_modelo"]:
        print(
            f"    {m['modelo']:<26} {m['provider']:<14} calls={m['calls']:>5} "
            f"actual=${m['actual_usd']:<9} est=${m['estimated_usd']}"
        )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=default_db())
    ap.add_argument("--save", action="store_true", help="grava JSON carimbado em HERMES_HOME")
    ap.add_argument("--marco", default="", help="rotulo do momento (ex.: 'pre-ajuste')")
    a = ap.parse_args()

    con = connect(a.db)
    data = collect(con.cursor())
    data["gerado_em"] = _dt.datetime.now().isoformat(timespec="seconds")
    data["marco"] = a.marco

    report(data)

    if a.save:
        home = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
        stamp = _dt.date.today().isoformat()
        path = os.path.join(home, f"baseline-contexto-{stamp}.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        print(f"\n>> gravado: {path}")


if __name__ == "__main__":
    main()
