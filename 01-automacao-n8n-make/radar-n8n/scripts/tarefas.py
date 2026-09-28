#!/usr/bin/env python3
"""Indexa `tarefas/*.md` e cruza com as causas detectadas pelo Radar n8n.

Le o frontmatter de cada tarefa (titulo, estado, criada_em, execucoes[]) e produz um
indice consultavel. Com `--radar <json>`, casa cada fluxo com erro contra as tarefas
abertas usando o ID do workflow, o nome do fluxo e a instancia citados no texto da tarefa.

Uso:
    python3 scripts/tarefas.py --json                       # indice completo em JSON
    python3 scripts/tarefas.py --wip --parado-ha 5          # so o WIP travado
    python3 scripts/tarefas.py --radar /tmp/radar.json      # cruzamento radar x tarefas
"""
from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path

DEFAULT_WORKSPACE = Path(os.environ.get("WORKSPACE_DIR", Path.cwd()))
ESTADOS_ABERTOS = {"aberta", "fazendo"}
# Palavras curtas/comuns que nao servem para casar tarefa com fluxo.
RUIDO = {
    "de", "do", "da", "dos", "das", "e", "o", "a", "os", "as", "em", "no", "na", "um", "uma",
    "para", "por", "com", "sem", "que", "nao", "fluxo", "fluxos", "bug", "erro", "erros",
    "incidente", "infra", "docs", "feat", "the", "workflow", "teste", "v1", "v8", "hn",
}


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


def tokens(texto: str) -> set:
    return {t for t in re.findall(r"[a-z0-9]{3,}", normalizar(texto)) if t not in RUIDO}


def ler_frontmatter(caminho: Path) -> dict:
    """Extrai o frontmatter YAML sem depender de PyYAML (formato conhecido e simples)."""
    texto = caminho.read_text(encoding="utf-8", errors="replace")
    if not texto.startswith("---"):
        return {"arquivo": caminho.name, "titulo": caminho.stem, "estado": "?", "corpo": texto}
    _, fm, corpo = texto.split("---", 2)

    def campo(nome: str) -> str:
        m = re.search(rf"^{nome}:\s*(.*)$", fm, re.M)
        return (m.group(1).strip().strip('"').strip("'") if m else "")

    execucoes = []
    for bloco in re.findall(r"^\s*-\s+harness:.*?(?=^\s*-\s+harness:|\Z)", fm, re.M | re.S):
        def sub(nome: str) -> str:
            m = re.search(rf"{nome}:\s*(.*)", bloco)
            return (m.group(1).strip() if m else "")
        execucoes.append({"harness": sub("harness"), "inicio": sub("inicio"), "fim": sub("fim")})

    return {
        "arquivo": caminho.name,
        "titulo": campo("titulo") or caminho.stem,
        "estado": campo("estado") or "?",
        "criada_em": campo("criada_em"),
        "criterio_de_pronto": campo("criterio_de_pronto"),
        "execucoes": execucoes,
        "corpo": corpo.strip(),
    }


def _data(valor):
    if not valor or valor in ("null", "None"):
        return None
    try:
        d = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            return datetime.combine(date.fromisoformat(valor[:10]), datetime.min.time(),
                                    tzinfo=timezone.utc)
        except ValueError:
            return None


def ultima_atividade(tarefa: dict):
    candidatos = []
    for ex in tarefa.get("execucoes") or []:
        for chave in ("fim", "inicio"):
            d = _data(ex.get(chave))
            if d:
                candidatos.append(d)
    d = _data(tarefa.get("criada_em"))
    if d:
        candidatos.append(d)
    return max(candidatos) if candidatos else None


def indexar(workspace: Path) -> list:
    pasta = workspace / "tarefas"
    tarefas = []
    for caminho in sorted(pasta.glob("*.md")):
        t = ler_frontmatter(caminho)
        ultima = ultima_atividade(t)
        t["ultima_atividade"] = ultima.isoformat() if ultima else None
        t["dias_parada"] = (datetime.now(timezone.utc) - ultima).days if ultima else None
        t["qtd_execucoes"] = len(t.get("execucoes") or [])
        tarefas.append(t)
    return tarefas


def cruzar_com_radar(tarefas: list, radar: dict) -> list:
    """Casa fluxo com erro x tarefa aberta. ID do workflow e prova; nome e heuristica."""
    abertas = [t for t in tarefas if t.get("estado") in ESTADOS_ABERTOS]

    # Frequencia de cada termo entre TODOS os fluxos: termo que aparece em muitos fluxos
    # ("lead", "crm", "clickup") nao identifica ninguem.
    freq_token = {}
    for inst in radar.get("instancias", []):
        for fluxo in inst.get("fluxos", []):
            for tok in tokens(fluxo.get("nome") or ""):
                freq_token[tok] = freq_token.get(tok, 0) + 1

    achados = []
    for inst in radar.get("instancias", []):
        for fluxo in inst.get("fluxos", []):
            wid = str(fluxo.get("workflow_id") or "")
            nome = fluxo.get("nome") or ""
            toks_fluxo = tokens(nome)
            casadas = []
            for t in abertas:
                texto = f"{t['titulo']} {t.get('corpo','')}"
                texto_norm = normalizar(texto)
                # 1) ID do workflow citado na tarefa: prova direta.
                if wid and len(wid) >= 8 and wid.lower() in texto_norm:
                    casadas.append({"arquivo": t["arquivo"], "titulo": t["titulo"],
                                    "estado": t["estado"], "dias_parada": t["dias_parada"],
                                    "confianca": "alta", "motivo": f"cita o ID {wid}"})
                    continue
                # 2) Nome do fluxo aparece inteiro na tarefa.
                if nome and len(nome) >= 8 and normalizar(nome) in texto_norm:
                    casadas.append({"arquivo": t["arquivo"], "titulo": t["titulo"],
                                    "estado": t["estado"], "dias_parada": t["dias_parada"],
                                    "confianca": "alta", "motivo": "cita o nome do fluxo"})
                    continue
                # 3) Sobreposicao de termos distintivos + instancia mencionada.
                comuns = toks_fluxo & tokens(texto)
                inst_citada = normalizar(inst["instancia"]) in texto_norm
                # Termo distintivo = raro no conjunto de fluxos. Dois termos genericos
                # ("lead", "crm") casam meio workspace e so geram ruido.
                distintivos = {c for c in comuns if freq_token.get(c, 0) <= 2}
                if len(distintivos) >= 2 and inst_citada:
                    casadas.append({"arquivo": t["arquivo"], "titulo": t["titulo"],
                                    "estado": t["estado"], "dias_parada": t["dias_parada"],
                                    "confianca": "media",
                                    "motivo": f"termos em comum: {', '.join(sorted(distintivos)[:4])}"})
            if fluxo.get("erros"):
                achados.append({
                    "instancia": inst["instancia"], "workflow_id": wid, "nome": nome,
                    "erros": fluxo["erros"], "causa": fluxo.get("causa"),
                    "tarefas": sorted(casadas, key=lambda c: c["confianca"] != "alta")[:3],
                })
    return achados


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    ap.add_argument("--json", action="store_true", help="indice completo em JSON")
    ap.add_argument("--wip", action="store_true", help="so tarefas aberta/fazendo")
    ap.add_argument("--parado-ha", type=int, help="filtra por dias sem atividade (com --wip)")
    ap.add_argument("--radar", help="JSON do radar_n8n.py para cruzar com as tarefas")
    ap.add_argument("--out", help="grava a saida JSON aqui")
    args = ap.parse_args()

    workspace = Path(args.workspace).expanduser()
    if not (workspace / "tarefas").is_dir():
        print(json.dumps({"erro": f"{workspace / 'tarefas'} nao existe"}, ensure_ascii=False))
        return 1

    tarefas = indexar(workspace)
    saida = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "total": len(tarefas),
        "por_estado": {},
    }
    for t in tarefas:
        saida["por_estado"][t["estado"]] = saida["por_estado"].get(t["estado"], 0) + 1

    selecionadas = tarefas
    if args.wip:
        selecionadas = [t for t in tarefas if t.get("estado") in ESTADOS_ABERTOS]
        if args.parado_ha is not None:
            selecionadas = [t for t in selecionadas
                            if (t.get("dias_parada") or 0) >= args.parado_ha]
        selecionadas.sort(key=lambda t: -(t.get("dias_parada") or 0))

    saida["tarefas"] = [
        {k: v for k, v in t.items() if k != "corpo"} for t in selecionadas
    ]

    if args.radar:
        radar = json.loads(Path(args.radar).expanduser().read_text(encoding="utf-8"))
        saida["cruzamento"] = cruzar_com_radar(tarefas, radar)

    texto = json.dumps(saida, ensure_ascii=False, indent=2)
    if args.out:
        destino = Path(args.out).expanduser()
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
        print(f"Indice gravado em {destino} — {len(selecionadas)} tarefa(s)")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
