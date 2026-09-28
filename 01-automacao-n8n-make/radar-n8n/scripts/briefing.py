#!/usr/bin/env python3
"""Junta os ultimos relatorios dos crons num painel HTML unico.

Os jobs rodam com `deliver: local`: a saida fica em ~/.hermes/cron/output/<job_id>/<data>.md
e nao e entregue em nenhum canal. Este script le o mais recente de cada job e monta
`rotinas/briefing.html` para leitura no preview do Hermes desktop.

Uso:
    python3 scripts/briefing.py                       # gera rotinas/briefing.html
    python3 scripts/briefing.py --out /tmp/b.html     # outro destino
    python3 scripts/briefing.py --texto               # imprime em texto no stdout
"""
from __future__ import annotations

import argparse
import html
import os
import re
from datetime import datetime
from pathlib import Path

CRON_OUT = Path.home() / ".hermes" / "cron" / "output"
DEFAULT_OUT = Path(os.environ.get("WORKSPACE_DIR", Path.cwd())) / "rotinas" / "briefing.html"

# job_id -> (rotulo, quando roda)
JOBS = {
    "95435a8849ea": ("Resumo ClickUp", "dias uteis 09:00"),
    "40cacf09afcd": ("Radar n8n", "dias uteis 10:00"),
    "12672bcdbc5a": ("Revisao de WIP", "segunda 09:00"),
}


def extrair_resposta(caminho: Path) -> str:
    """O .md do cron guarda prompt + resposta; so a resposta interessa."""
    texto = caminho.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^## Response\s*$", texto, re.M)
    return texto[m.end():].strip() if m else texto.strip()


def markdown_simples(md: str) -> str:
    """Conversao minima: nada de dependencia externa para 4 construcoes de markdown."""
    saida, em_lista = [], False
    for linha in md.splitlines():
        crua = linha.rstrip()
        if not crua.strip():
            if em_lista:
                saida.append("</ul>")
                em_lista = False
            continue
        texto = html.escape(crua.strip())
        texto = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", texto)
        texto = re.sub(r"`(.+?)`", r"<code>\1</code>", texto)
        texto = re.sub(r"\*(?!\*)(.+?)(?<!\*)\*", r"<em>\1</em>", texto)
        if texto.startswith("- ") or texto.startswith("* "):
            if not em_lista:
                saida.append("<ul>")
                em_lista = True
            saida.append(f"<li>{texto[2:]}</li>")
            continue
        if em_lista:
            saida.append("</ul>")
            em_lista = False
        m = re.match(r"^(#{1,4})\s+(.*)$", texto)
        if m:
            saida.append(f"<h4>{m.group(2)}</h4>")
        elif re.match(r"^\d+\.\s", texto):
            saida.append(f'<p class="num">{texto}</p>')
        else:
            saida.append(f"<p>{texto}</p>")
    if em_lista:
        saida.append("</ul>")
    return "\n".join(saida)


def ultimo_relatorio(job_id: str):
    pasta = CRON_OUT / job_id
    if not pasta.is_dir():
        return None
    arquivos = sorted(pasta.glob("*.md"))
    if not arquivos:
        return None
    caminho = arquivos[-1]
    try:
        quando = datetime.strptime(caminho.stem, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        quando = datetime.fromtimestamp(caminho.stat().st_mtime)
    return {"caminho": caminho, "quando": quando, "corpo": extrair_resposta(caminho)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--texto", action="store_true", help="imprime em texto puro no stdout")
    args = ap.parse_args()

    coletados = []
    for job_id, (rotulo, quando) in JOBS.items():
        rel = ultimo_relatorio(job_id)
        if rel:
            coletados.append((rotulo, quando, rel))
    coletados.sort(key=lambda c: c[2]["quando"], reverse=True)

    if args.texto:
        if not coletados:
            print("Nenhum relatorio de cron ainda. Rode: hermes cron run <job_id>")
            return 0
        for rotulo, _, rel in coletados:
            print(f"\n{'=' * 70}\n{rotulo} — {rel['quando'].strftime('%d/%m %H:%M')}\n{'=' * 70}")
            print(rel["corpo"])
        return 0

    agora = datetime.now()
    secoes = []
    for rotulo, quando_roda, rel in coletados:
        idade = (agora - rel["quando"]).days
        selo = "hoje" if idade == 0 else ("ontem" if idade == 1 else f"ha {idade} dias")
        cor = "var(--accent)" if idade <= 1 else "#f59e0b"
        secoes.append(
            f'<section class="bloco"><header class="bh">'
            f"<h3>{html.escape(rotulo)}</h3>"
            f'<span class="quando" style="color:{cor}">{rel["quando"].strftime("%d/%m %H:%M")}'
            f" · {selo}</span></header>"
            f'<div class="sub">roda {html.escape(quando_roda)}</div>'
            f'<div class="corpo">{markdown_simples(rel["corpo"])}</div></section>'
        )

    if not secoes:
        secoes.append('<p class="vazio">Nenhum relatorio ainda. '
                      "Rode <code>hermes cron run &lt;job_id&gt;</code>.</p>")

    corpo = f"""<style>
  .brief {{ display:flex; flex-direction:column; gap:18px; max-width:780px; color:var(--foreground); }}
  .brief h2 {{ margin:0; font-size:20px; }}
  .brief h3 {{ margin:0; font-size:15px; }}
  .brief h4 {{ margin:12px 0 4px; font-size:13px; }}
  .topo {{ border-bottom:1px solid var(--border); padding-bottom:10px; }}
  .bloco {{ border:1px solid var(--border); border-radius:8px; padding:12px 14px;
            background:var(--card); }}
  .bh {{ display:flex; justify-content:space-between; align-items:baseline; gap:12px; }}
  .quando {{ font-size:12px; font-weight:600; white-space:nowrap; }}
  .sub {{ color:var(--muted-foreground); font-size:11px; margin-top:2px; }}
  .corpo {{ font-size:13px; line-height:1.55; margin-top:8px; }}
  .corpo p {{ margin:6px 0; }}
  .corpo ul {{ margin:6px 0; padding-left:18px; }}
  .corpo li {{ margin:3px 0; }}
  .corpo code {{ font-size:11.5px; }}
  .num {{ margin:3px 0; }}
  .vazio {{ color:var(--muted-foreground); font-size:13px; }}
</style>
<div class="brief">
  <header class="topo"><h2>Briefing</h2>
  <div class="sub">ultimos relatorios das rotinas · gerado {agora.strftime('%d/%m %H:%M')}</div>
  </header>
  {''.join(secoes)}
</div>"""

    destino = Path(args.out).expanduser()
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(corpo, encoding="utf-8")
    print(f"Briefing gravado em {destino} — {len(coletados)} relatorio(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
