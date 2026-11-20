#!/usr/bin/env bash
# Generate the repository index.
# Usage: tools/index.sh [output]    default: docs/INDEX.tsv
#
# Scope (deliberately narrow):
#   - *.md / *.txt within the root and three levels down
#   - *.sh under tools/
# Excluded: lost+found/, .git/, .machine/ (local environment, contains credentials)

set -euo pipefail
cd "$(dirname "$0")/.."

out="${1:-docs/INDEX.tsv}"
mkdir -p "$(dirname "$out")"

{
  printf 'path\tsha12\tlines\tmtime\n'
  {
    find . -maxdepth 3 \( -path ./lost+found -o -path ./.git -o -path ./.machine \) -prune -o \
      -type f \( -name '*.md' -o -name '*.txt' \) -print
    find tools -maxdepth 1 -type f -name '*.sh'
  } | sed 's|^\./||' | sort -u | while IFS= read -r f; do
    [ -f "$f" ] || continue
    # Anything gitignored is local, not part of the repository. Indexing it would
    # put a path in a tracked file that a clone does not have.
    if git check-ignore -q "$f"; then continue; fi
    printf '%s\t%s\t%s\t%s\n' \
      "$f" \
      "$(sha256sum "$f" | cut -c1-12)" \
      "$(wc -l < "$f" | tr -d ' ')" \
      "$(date -r "$f" +%Y-%m-%d)"
  done
} > "$out"
