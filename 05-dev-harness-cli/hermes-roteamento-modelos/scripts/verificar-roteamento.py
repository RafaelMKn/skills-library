#!/usr/bin/env python3
"""Mostra como o Hermes resolve modelo/esforço/fallback da delegação.

Rodar com o Python do venv do Hermes:
  cd ~/.hermes/hermes-agent && venv/bin/python <skill>/scripts/verificar-roteamento.py claude-sonnet-5-5 gpt-6-luna
"""
import sys

from hermes_cli.config import load_config
from hermes_constants import resolve_reasoning_config
from hermes_cli.fallback_config import scoped_fallback_chain

cfg = load_config() or {}
deleg = cfg.get("delegation") or {}
model_cfg = cfg.get("model") or {}
main_model = model_cfg.get("default") if isinstance(model_cfg, dict) else model_cfg

print("principal:", model_cfg.get("provider") if isinstance(model_cfg, dict) else "?", main_model,
      "->", resolve_reasoning_config(cfg, main_model or ""))
print("delegacao:", {k: deleg.get(k) for k in ("provider", "model", "reasoning_effort")})
pinned = bool(deleg.get("provider") or deleg.get("model") or deleg.get("base_url"))
print("filho fixado:", pinned)
print("fallback do filho:", scoped_fallback_chain(None, deleg.get("fallback_providers"), pinned=pinned,
                                                  owner="delegation"))
print("reasoning_overrides:", (cfg.get("agent") or {}).get("reasoning_overrides"))
for m in sys.argv[1:]:
    print(f"esforco efetivo se {m} virar fallback:", resolve_reasoning_config(cfg, m))
