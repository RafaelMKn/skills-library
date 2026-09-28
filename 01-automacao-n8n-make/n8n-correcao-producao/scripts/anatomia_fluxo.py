#!/usr/bin/env python3
"""Anatomia de um export de workflow n8n sem despejar o JSON no contexto.

Fluxo de 100+ nos nao cabe no contexto do agente. Este script responde as perguntas
estruturais que importam numa auditoria ou num "o fluxo ja faz X?":

    python3 anatomia_fluxo.py fluxo.json
        Resumo: triggers, componentes conexos, nos orfaos.

    python3 anatomia_fluxo.py fluxo.json --grep follow lembrete reengaj
        Nos cujo JSON inteiro casa com QUALQUER um dos termos (case-insensitive).

    python3 anatomia_fluxo.py fluxo.json --upstream "Enviar texto1"
        Cadeia que alimenta o no -- e como se acha o GATILHO REAL de uma cadeia.

    python3 anatomia_fluxo.py fluxo.json --downstream "Schedule Trigger"
        Cadeia alimentada pelo no.

    python3 anatomia_fluxo.py fluxo.json --node "Enviar texto1"
        Parametros e vizinhos de um no especifico.

O export aceito e tanto o objeto cru do n8n quanto o embrulhado em {"data": {...}}.
"""

import argparse
import json
import sys
from collections import defaultdict, deque

STICKY = "stickyNote"


def carregar(caminho):
    with open(caminho, encoding="utf-8") as fh:
        doc = json.load(fh)
    wf = doc.get("data", doc)
    if "nodes" not in wf:
        sys.exit(f"{caminho}: nao parece um export de workflow (sem 'nodes')")
    return wf


def nos_reais(wf):
    return [n for n in wf["nodes"] if not n.get("type", "").endswith(STICKY)]


def mapas(wf):
    """Devolve (por_nome, saida, entrada, adjacencia_nao_direcionada).

    Conexoes de TODOS os tipos entram (main, ai_tool, ai_languageModel, ai_memory):
    e o que mantem um agente agrupado com as tools dele na analise de componentes.
    """
    por_nome = {n["name"]: n for n in nos_reais(wf)}
    saida = defaultdict(list)
    entrada = defaultdict(list)
    adj = defaultdict(set)
    for origem, tipos in (wf.get("connections") or {}).items():
        if origem not in por_nome:
            continue
        for tipo, ramos in (tipos or {}).items():
            for idx, ramo in enumerate(ramos or []):
                for conexao in ramo or []:
                    destino = conexao.get("node")
                    if destino not in por_nome:
                        continue
                    saida[origem].append((destino, tipo, idx))
                    entrada[destino].append((origem, tipo, idx))
                    adj[origem].add(destino)
                    adj[destino].add(origem)
    return por_nome, saida, entrada, adj


def eh_trigger(no):
    t = no.get("type", "").lower()
    return "trigger" in t or t.endswith(".cron")


def rotulo(no):
    curto = no.get("type", "?").split(".")[-1]
    marca = "  [DISABLED]" if no.get("disabled") else ""
    return f"{no['name']} [{curto}]{marca}"


def resumo(wf):
    por_nome, saida, entrada, adj = mapas(wf)
    print(f"{wf.get('name','?')} | id={wf.get('id','?')} | ativo={wf.get('active')} "
          f"| {len(por_nome)} nos executaveis")

    cfg = wf.get("settings") or {}
    if cfg.get("errorWorkflow"):
        print(f"errorWorkflow: {cfg['errorWorkflow']}")
    else:
        print("errorWorkflow: AUSENTE")

    print("\n== TRIGGERS ==")
    triggers = [n for n in por_nome.values() if eh_trigger(n)]
    for n in triggers or []:
        extra = json.dumps(n.get("parameters", {}), ensure_ascii=False)
        print(f"  {rotulo(n)}  {extra[:160]}")
    if not triggers:
        print("  nenhum")

    print("\n== COMPONENTES CONEXOS ==")
    visto, componentes = set(), []
    for nome in por_nome:
        if nome in visto:
            continue
        fila, comp = deque([nome]), []
        while fila:
            atual = fila.popleft()
            if atual in visto:
                continue
            visto.add(atual)
            comp.append(atual)
            fila.extend(adj[atual] - visto)
        componentes.append(comp)
    for i, comp in enumerate(sorted(componentes, key=len, reverse=True), 1):
        trigs = [c for c in comp if eh_trigger(por_nome[c])]
        print(f"  #{i}: {len(comp)} nos | triggers: {trigs or 'NENHUM'}")
        if len(comp) <= 15:
            for c in comp:
                print(f"       - {rotulo(por_nome[c])}")

    print("\n== ORFAOS (sem entrada e sem saida) ==")
    orfaos = [n for nome, n in por_nome.items()
              if not saida.get(nome) and not entrada.get(nome)]
    for n in orfaos:
        print(f"  {rotulo(n)}")
    if not orfaos:
        print("  nenhum")
    if orfaos:
        print("  ^ no de escrita/delete orfao no canvas e risco operacional:"
              " um clique no editor executa contra producao.")


def grep(wf, termos):
    por_nome, _, _, _ = mapas(wf)
    alvos = [t.lower() for t in termos]
    achou = False
    for nome, n in por_nome.items():
        blob = json.dumps(n, ensure_ascii=False).lower()
        casou = [t for t in alvos if t in blob]
        if casou:
            achou = True
            print(f"{rotulo(n)}  <= {casou}")
    if not achou:
        print("nenhum no casou")


def caminhar(wf, inicio, sentido, profundidade):
    por_nome, saida, entrada, _ = mapas(wf)
    if inicio not in por_nome:
        sys.exit(f"no '{inicio}' nao existe neste export")
    vizinhos = entrada if sentido == "upstream" else saida
    seta = "<=" if sentido == "upstream" else "=>"
    fila, visto = deque([(inicio, 0)]), set()
    while fila:
        nome, nivel = fila.popleft()
        if nome in visto or nivel > profundidade:
            continue
        visto.add(nome)
        ligacoes = vizinhos.get(nome, [])
        print("  " * nivel + f"{seta} {rotulo(por_nome[nome])}")
        for outro, tipo, _idx in ligacoes:
            if tipo != "main":
                print("  " * (nivel + 1) + f"   ({tipo}) {outro}")
            fila.append((outro, nivel + 1))


def detalhar(wf, nome):
    por_nome, saida, entrada, _ = mapas(wf)
    n = por_nome.get(nome)
    if not n:
        sys.exit(f"no '{nome}' nao existe neste export")
    print(rotulo(n))
    print(f"type={n.get('type')} typeVersion={n.get('typeVersion')}")
    print(f"onError={n.get('onError')} retryOnFail={n.get('retryOnFail')}")
    print(f"IN : {entrada.get(nome, [])}")
    print(f"OUT: {saida.get(nome, [])}")
    print("\nPARAMETERS:")
    print(json.dumps(n.get("parameters", {}), ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export", help="caminho do JSON exportado do n8n")
    ap.add_argument("--grep", nargs="+", metavar="TERMO")
    ap.add_argument("--upstream", metavar="NO")
    ap.add_argument("--downstream", metavar="NO")
    ap.add_argument("--node", metavar="NO")
    ap.add_argument("--depth", type=int, default=25)
    args = ap.parse_args()

    wf = carregar(args.export)
    if args.grep:
        grep(wf, args.grep)
    elif args.upstream:
        caminhar(wf, args.upstream, "upstream", args.depth)
    elif args.downstream:
        caminhar(wf, args.downstream, "downstream", args.depth)
    elif args.node:
        detalhar(wf, args.node)
    else:
        resumo(wf)


if __name__ == "__main__":
    main()
