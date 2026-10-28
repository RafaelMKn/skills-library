#!/usr/bin/env python3
"""Compara as skills instaladas em ~/.hermes/skills com as citadas em references/mapa.md.

Saída: 'OK' quando bate; senão lista NAO MAPEADA (instalada e ausente do mapa) e
ORFA NO MAPA (citada no mapa e não instalada). Somente stdlib.
"""
import os
import re
import sys
from pathlib import Path

HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
SKILLS = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else HOME / "skills"
MAPA = Path(__file__).resolve().parent.parent / "references" / "mapa.md"
IGNORAR = {"estagiario"}


def nome_da_skill(p: Path):
    txt = p.read_text(encoding="utf-8", errors="replace")
    if not txt.startswith("---"):
        return None
    m = re.search(r"^name:\s*['\"]?([\w.-]+)", txt, re.M)
    return m.group(1) if m else None


instaladas = set()
for p in SKILLS.rglob("SKILL.md"):
    if any(part.startswith(".") for part in p.relative_to(SKILLS).parts):
        continue
    n = nome_da_skill(p)
    if n and n not in IGNORAR:
        instaladas.add(n)

mapeadas = set(re.findall(r"^\| `([\w.-]+)` \|", MAPA.read_text(encoding="utf-8"), re.M))

faltando = sorted(instaladas - mapeadas)
orfas = sorted(mapeadas - instaladas)
print(f"instaladas={len(instaladas)} mapeadas={len(mapeadas)}")
for n in faltando:
    print(f"NAO MAPEADA: {n}")
for n in orfas:
    print(f"ORFA NO MAPA: {n}")
if not faltando and not orfas:
    print("OK")
