#!/usr/bin/env python3
"""Renderiza o painel HTML do Radar n8n a partir do JSON do radar_n8n.py.

O HTML e feito para o preview inline do Hermes desktop: usa as variaveis de tema
(--foreground, --muted-foreground, --accent, --border, --card) e nao define
background, fonte nem margem proprios.

Uso:
    python3 scripts/gerar_painel.py radar.json --out saude-n8n.html
    python3 scripts/gerar_painel.py radar.json --historico ~/.hermes/radar-n8n/historico.jsonl
"""
from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from pathlib import Path

SEVERIDADE = {
    "credencial-nao-descriptografavel": "critico",
    "credencial-invalida": "critico",
    "erro-de-banco": "critico",
    "dns-nao-resolve": "alto",
    "rede-indisponivel": "alto",
    "erro-no-servico-externo": "alto",
    "rate-limit": "medio",
    "dado-inesperado": "medio",
    "expressao-quebrada": "medio",
    "parsing": "medio",
    "nao-classificado": "baixo",
}
CORES = {"critico": "#ef4444", "alto": "#f59e0b", "medio": "#eab308", "baixo": "#64748b"}


def e(texto) -> str:
    return html.escape(str(texto if texto is not None else ""))


def fmt_data(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%d/%m %H:%M")
    except (ValueError, AttributeError):
        return e(iso)


def barra_serie(historico: list) -> str:
    """Sparkline em SVG da taxa de erro das ultimas coletas."""
    pontos = [h for h in historico if h.get("total")][-14:]
    if len(pontos) < 2:
        return '<p class="vazio">Serie historica aparece a partir da segunda coleta.</p>'
    taxas = [p["total"].get("taxa_erro", 0) for p in pontos]
    teto = max(max(taxas), 1)
    largura, altura, gap = 26, 70, 6
    barras = []
    for i, (p, t) in enumerate(zip(pontos, taxas)):
        h = max(2, int(altura * t / teto))
        x = i * (largura + gap)
        cor = CORES["critico"] if t >= 20 else CORES["alto"] if t >= 5 else "var(--accent)"
        barras.append(
            f'<rect x="{x}" y="{altura - h}" width="{largura}" height="{h}" rx="3" fill="{cor}">'
            f'<title>{fmt_data(p.get("gerado_em",""))} — {t}% de erro</title></rect>'
        )
    w = len(pontos) * (largura + gap)
    return (
        f'<svg viewBox="0 0 {w} {altura + 16}" width="100%" style="max-width:{w}px;height:auto">'
        + "".join(barras)
        + f'<text x="0" y="{altura + 13}" font-size="10" fill="var(--muted-foreground)">'
        + f'{fmt_data(pontos[0].get("gerado_em",""))} → {fmt_data(pontos[-1].get("gerado_em",""))}</text></svg>'
    )


def render(dados: dict, historico: list, cruzamento: dict | None = None) -> str:
    total = dados.get("total", {})
    taxa = total.get("taxa_erro", 0)
    cor_geral = CORES["critico"] if taxa >= 20 else CORES["alto"] if taxa >= 5 else "var(--accent)"
    diff = dados.get("diff", {})

    if dados.get("erro_fatal"):
        return (
            '<div class="radar"><div class="alerta critico"><strong>Radar nao coletou.</strong>'
            f"<br>{e(dados['erro_fatal'])}</div></div>"
        )

    # --- cabecalho -----------------------------------------------------------
    partes = [
        '<div class="radar">',
        '<header class="topo">',
        '<div><h2>Saude n8n</h2>',
        f'<p class="sub">Janela de {e(dados.get("janela_horas"))}h · coletado '
        f'{fmt_data(dados.get("gerado_em", ""))}</p></div>',
        f'<div class="placar"><span class="taxa" style="color:{cor_geral}">{taxa}%</span>'
        f'<span class="sub">{total.get("erros", 0):,} erros / {total.get("execucoes", 0):,} exec</span>'
        "</div></header>",
    ]

    # --- mudancas desde a ultima coleta --------------------------------------
    if not diff.get("primeira_coleta"):
        blocos = []
        for chave, rotulo, cor in (
            ("novos", "novo quebrando", CORES["critico"]),
            ("agravados", "piorou", CORES["alto"]),
            ("melhorados", "melhorou", "var(--accent)"),
            ("resolvidos", "parou de errar", "var(--accent)"),
        ):
            itens = diff.get(chave) or []
            for it in itens[:4]:
                nome = it.get("nome") or it.get("workflow_id")
                antes = it.get("antes", 0)
                agora = it.get("erros", 0)
                blocos.append(
                    f'<li><span class="tag" style="background:{cor}22;color:{cor}">{rotulo}</span> '
                    f'<strong>{e(nome)}</strong> <span class="sub">[{e(it.get("instancia"))}]'
                    f' {antes} → {agora}</span></li>'
                )
        if blocos:
            partes.append('<section><h3>Mudou desde a ultima coleta</h3><ul class="mudancas">'
                          + "".join(blocos) + "</ul></section>")
        else:
            partes.append('<section><h3>Mudou desde a ultima coleta</h3>'
                          '<p class="vazio">Nada mudou de forma relevante.</p></section>')
    else:
        partes.append('<section><h3>Mudou desde a ultima coleta</h3>'
                      '<p class="vazio">Primeira coleta — o diff comeca na proxima.</p></section>')

    # --- placar por instancia -------------------------------------------------
    linhas = []
    for i in dados.get("instancias", []):
        exec_tot = i["erros"] + i["sucessos"]
        tx = round(100 * i["erros"] / exec_tot, 1) if exec_tot else 0.0
        cor = CORES["critico"] if tx >= 20 else CORES["alto"] if tx >= 5 else "var(--accent)"
        estado = f'<span style="color:{CORES["critico"]}">{e(i["falha"])}</span>' if i.get("falha") else \
                 f'<span style="color:{cor};font-weight:600">{tx}%</span>'
        ret = fmt_data(i["retencao_mais_antiga"]) if i.get("retencao_mais_antiga") else "—"
        linhas.append(
            f'<tr><td><strong>{e(i["instancia"])}</strong></td>'
            f'<td class="num">{exec_tot:,}</td><td class="num">{i["erros"]:,}</td>'
            f'<td class="num">{estado}</td><td class="sub">{ret}</td></tr>'
        )
    partes.append(
        '<section><h3>Por instancia</h3><table><thead><tr>'
        "<th>Instancia</th><th class='num'>Exec</th><th class='num'>Erros</th>"
        "<th class='num'>Taxa</th><th>Exec mais antiga retida</th>"
        "</tr></thead><tbody>" + "".join(linhas) + "</tbody></table></section>"
    )

    # --- fluxos sangrando -----------------------------------------------------
    # Vinculo fluxo -> tarefas abertas, indexado por (instancia, workflow_id).
    vinculos = {}
    for item in (cruzamento or {}).get("cruzamento", []):
        vinculos[(item.get("instancia"), item.get("workflow_id"))] = item.get("tarefas") or []

    todos = []
    for i in dados.get("instancias", []):
        for f in i.get("fluxos", []):
            todos.append((i["instancia"], f))
    todos.sort(key=lambda p: -p[1]["erros"])

    if todos:
        cards = []
        for inst, f in todos[:10]:
            causa = f.get("causa", "nao-classificado")
            sev = SEVERIDADE.get(causa, "baixo")
            cor = CORES[sev]
            tot = f["erros"] + f.get("sucessos", 0)
            tx = round(100 * f["erros"] / tot, 1) if tot else 100.0
            morto = ' <span class="tag" style="background:#ef444422;color:#ef4444">100% morto</span>' \
                if f.get("sucessos", 0) == 0 else ""
            # Rastro: essa dor ja virou tarefa? Ha quantos dias esta parada?
            ligadas = vinculos.get((inst, f["workflow_id"]))
            if ligadas is None:
                rastro = ""
            elif not ligadas:
                rastro = ('<div class="rastro sem"><span class="tag" '
                          'style="background:#ef444422;color:#ef4444">sem tarefa</span> '
                          "nenhuma tarefa aberta cobre este fluxo</div>")
            else:
                linhas_t = []
                for t in ligadas[:2]:
                    dias = t.get("dias_parada")
                    idade = f" · parada ha {dias}d" if dias else ""
                    marca = "prova" if t.get("confianca") == "alta" else "indicio"
                    linhas_t.append(
                        f'<div><span class="tag" style="background:var(--accent);opacity:.85;'
                        f'color:var(--card)">{marca}</span> <code>{e(t.get("arquivo"))}</code>'
                        f' <span class="sub">[{e(t.get("estado"))}{idade}]</span></div>'
                    )
                rastro = '<div class="rastro">' + "".join(linhas_t) + "</div>"
            cards.append(
                f'<article class="fluxo" style="border-left-color:{cor}">'
                f'<div class="fluxo-topo"><strong>{e(f.get("nome") or f["workflow_id"])}</strong>'
                f'<span class="cont" style="color:{cor}">{f["erros"]:,} erros</span></div>'
                f'<div class="sub">{e(inst)} · <code>{e(f["workflow_id"])}</code> · {tx}% de falha'
                + (f' · no <code>{e(f["no"])}</code>' if f.get("no") else "") + morto + "</div>"
                f'<div class="causa"><span class="tag" style="background:{cor}22;color:{cor}">'
                f'{e(causa)}</span> {e(f.get("acao", ""))}</div>'
                f'<pre>{e((f.get("mensagem") or "")[:240])}</pre>{rastro}</article>'
            )
        partes.append("<section><h3>Fluxos sangrando</h3>" + "".join(cards) + "</section>")
    else:
        partes.append('<section><h3>Fluxos sangrando</h3>'
                      '<p class="vazio">Nenhum erro na janela. Tudo verde.</p></section>')

    # --- serie historica ------------------------------------------------------
    partes.append("<section><h3>Taxa de erro — ultimas coletas</h3>"
                  + barra_serie(historico) + "</section>")

    # --- WIP travado ----------------------------------------------------------
    if cruzamento:
        estados = cruzamento.get("por_estado", {})
        travadas = sorted(
            [t for t in cruzamento.get("tarefas", [])
             if t.get("estado") in ("aberta", "fazendo") and (t.get("dias_parada") or 0) >= 5],
            key=lambda t: -(t.get("dias_parada") or 0),
        )
        if travadas:
            itens = "".join(
                f'<li><span>{e(t.get("titulo"))[:70]}</span>'
                f'<span class="sub" style="white-space:nowrap">{e(t.get("estado"))} · '
                f'{t.get("dias_parada")}d parada</span></li>'
                for t in travadas[:6]
            )
            resumo = " · ".join(f"{v} {k}" for k, v in sorted(estados.items()))
            partes.append(
                f'<section><h3>Tarefas travadas ({len(travadas)} de {resumo})</h3>'
                f'<ul class="wip">{itens}</ul></section>'
            )

    partes.append("</div>")

    estilo = """
<style>
  .radar { display:flex; flex-direction:column; gap:20px; max-width:760px; color:var(--foreground); }
  .radar h2 { margin:0; font-size:20px; }
  .radar h3 { margin:0 0 8px; font-size:13px; text-transform:uppercase;
              letter-spacing:.06em; color:var(--muted-foreground); }
  .topo { display:flex; justify-content:space-between; align-items:flex-start; gap:16px;
          border-bottom:1px solid var(--border); padding-bottom:12px; }
  .placar { text-align:right; display:flex; flex-direction:column; }
  .taxa { font-size:30px; font-weight:700; line-height:1; }
  .sub { color:var(--muted-foreground); font-size:12px; margin:2px 0 0; }
  .vazio { color:var(--muted-foreground); font-size:13px; margin:0; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th { text-align:left; font-weight:600; font-size:11px; text-transform:uppercase;
       color:var(--muted-foreground); border-bottom:1px solid var(--border); padding:6px 8px; }
  td { padding:7px 8px; border-bottom:1px solid var(--border); }
  .num { text-align:right; }
  .fluxo { border:1px solid var(--border); border-left-width:3px; border-radius:6px;
           padding:10px 12px; margin-bottom:8px; background:var(--card); }
  .fluxo-topo { display:flex; justify-content:space-between; gap:12px; align-items:baseline; }
  .cont { font-variant-numeric:tabular-nums; font-weight:600; font-size:13px; white-space:nowrap; }
  .causa { font-size:12px; margin-top:6px; color:var(--muted-foreground); }
  .tag { display:inline-block; padding:1px 7px; border-radius:99px; font-size:11px;
         font-weight:600; margin-right:4px; }
  .radar pre { margin:6px 0 0; padding:6px 8px; border-radius:4px; font-size:11px;
               white-space:pre-wrap; word-break:break-word; color:var(--muted-foreground);
               border:1px solid var(--border); }
  .radar code { font-size:11px; }
  .mudancas { list-style:none; padding:0; margin:0; font-size:13px; }
  .mudancas li { padding:4px 0; border-bottom:1px solid var(--border); }
  .rastro { margin-top:7px; padding-top:6px; border-top:1px dashed var(--border);
            font-size:11px; color:var(--muted-foreground); }
  .rastro div { padding:1px 0; }
  .rastro.sem { color:#ef4444; }
  .wip { list-style:none; padding:0; margin:0; font-size:13px; }
  .wip li { display:flex; justify-content:space-between; gap:12px; padding:5px 0;
            border-bottom:1px solid var(--border); }
  .alerta.critico { border:1px solid #ef4444; border-radius:6px; padding:12px; font-size:13px; }
</style>
"""
    return estilo + "".join(partes)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json_in", help="JSON produzido por radar_n8n.py")
    ap.add_argument("--out", required=True, help="caminho do HTML de saida")
    ap.add_argument("--historico", help="historico.jsonl para a serie temporal")
    ap.add_argument("--tarefas", help="JSON do tarefas.py --radar, para o rastro de tarefas")
    args = ap.parse_args()

    dados = json.loads(Path(args.json_in).expanduser().read_text(encoding="utf-8"))
    historico = []
    if args.historico:
        p = Path(args.historico).expanduser()
        if p.is_file():
            for linha in p.read_text(encoding="utf-8").splitlines():
                linha = linha.strip()
                if linha:
                    try:
                        historico.append(json.loads(linha))
                    except json.JSONDecodeError:
                        continue

    cruzamento = None
    if args.tarefas:
        p = Path(args.tarefas).expanduser()
        if p.is_file():
            try:
                cruzamento = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                cruzamento = None

    destino = Path(args.out).expanduser()
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(render(dados, historico, cruzamento), encoding="utf-8")
    print(f"Painel gravado em {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
