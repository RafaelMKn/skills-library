#!/usr/bin/env bash
# Inventário read-only de uma pasta de projetos: estado git por subpasta.
# Uso: inventario_git.sh [pasta]   (padrão: ~/<workspace>)
# Saída: pasta | repo ou wt->repo-pai | branch | sujos | à frente do upstream | último commit | remoto
set -u
root=${1:-$HOME/<workspace>}
cd "$root" || exit 1
for d in */ .[!.]*/; do
  d=${d%/}; [ -d "$d" ] || continue
  top=$(git -C "$d" rev-parse --show-toplevel 2>/dev/null)
  if [ -n "$top" ] && [ "$top" = "$(realpath "$d")" ]; then
    kind=repo
    [ -f "$d/.git" ] && kind="wt->$(sed 's/gitdir: //' "$d/.git" | sed 's#/.git/worktrees.*##' | xargs basename)"
    br=$(git -C "$d" branch --show-current); [ -z "$br" ] && br="(detached $(git -C "$d" rev-parse --short HEAD))"
    dirty=$(git -C "$d" status --porcelain 2>/dev/null | wc -l)
    ahead=$(git -C "$d" rev-list --count @{u}..HEAD 2>/dev/null || echo sem-upstream)
    last=$(git -C "$d" log -1 --format=%cs 2>/dev/null)
    rem=$(git -C "$d" remote get-url origin 2>/dev/null | sed 's#.*github.com[:/]##')
    printf '%-50s %-26s br=%-32s dirty=%-4s ahead=%-12s last=%s %s\n' "$d" "$kind" "$br" "$dirty" "$ahead" "$last" "$rem"
  elif [ -n "$top" ]; then
    printf '%-50s DENTRO-DE %s\n' "$d" "$top"
  else
    printf '%-50s NAO-GIT (%s)\n' "$d" "$(du -sh "$d" 2>/dev/null | cut -f1)"
  fi
done
echo
echo '# worktrees registrados por repo (inclui os que vivem fora da pasta):'
for d in */; do
  d=${d%/}; [ -d "$d/.git" ] || continue
  n=$(git -C "$d" worktree list | wc -l)
  [ "$n" -gt 1 ] && echo "$d: $((n-1)) worktrees ($(git -C "$d" worktree list | grep -c prunable) prunable)"
done
