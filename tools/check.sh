#!/usr/bin/env bash
# The gate: structure broken means red. Exit 0 means the structure is intact.
#
# Checks (every newly found defect becomes a check, never a reminder):
#   1. pointers      every path mentioned in AGENTS.md must exist
#   2. index freshness  docs/INDEX.tsv must match a fresh generation
#   3. status fields    STATUS.md must carry the agreed section headings
#   4. decision fields  every D-xxx entry must have a Relations line
#   5. secrets          no local-environment file may appear in the index

set -uo pipefail
cd "$(dirname "$0")/.."

err=0
warn=0
fail() { printf 'ERROR %s\n' "$*"; err=$((err+1)); }
note() { printf 'WARN  %s\n' "$*"; warn=$((warn+1)); }

# 1. pointers
while IFS= read -r f; do
  [ -z "$f" ] && continue
  [ -e "$f" ] || fail "broken pointer: $f (mentioned in AGENTS.md, does not exist)"
done < <(grep -oE '`[^`]+\.(md|sh|tsv|txt)`' AGENTS.md 2>/dev/null | tr -d '`' | sort -u)

# 2. index freshness
if [ ! -f docs/INDEX.tsv ]; then
  fail "docs/INDEX.tsv missing; run tools/index.sh"
else
  tmp="$(mktemp)"
  tools/index.sh "$tmp"
  if ! cmp -s "$tmp" docs/INDEX.tsv; then
    fail "index is stale; run tools/index.sh"
    diff -U0 docs/INDEX.tsv "$tmp" | grep -E '^[+-][^+-]' | head -6 | sed 's/^/      /'
  fi
  rm -f "$tmp"
fi

# 3. status fields
for k in "Phase" "Working on" "Blocked" "Next" "Open rulings"; do
  grep -qx "## $k" docs/STATUS.md 2>/dev/null || fail "STATUS.md missing section: ## $k"
done

# 4. decision fields (the Relations line stands for the four-field minimum)
n=$(grep -c '^## D-' docs/DECISIONS.md 2>/dev/null); [ -z "${n:-}" ] && n=0
m=$(grep -c '^- \*\*Relations\*\*' docs/DECISIONS.md 2>/dev/null); [ -z "${m:-}" ] && m=0
[ "$n" = "$m" ] || fail "DECISIONS: $n decisions, but only $m have a Relations line"

# 5. the index may only contain project paths (catches local env files by construction)
if [ -f docs/INDEX.tsv ]; then
  bad=$(tail -n +2 docs/INDEX.tsv | cut -f1 | grep -vE \
    '^(AGENTS\.md|README\.(md|txt)|LICENSING\.md|TRADEMARK\.md|CLA\.md|CONTRIBUTORS\.md|design/[^/]+\.md|docs/[^/]+\.(md|tsv)|probe/[^/]+\.(md|py)|tools/[^/]+\.sh)$' || true)
  if [ -n "$bad" ]; then
    fail "index contains non-project paths:"
    printf '%s\n' "$bad" | sed 's/^/      /'
  fi
fi

# 6. every coined term must carry its delta (four columns in the terminology table)
if [ -f design/FOUNDATION.md ]; then
  bad=$(awk -F'|' '
    /^\| Term \| Our definition \|/ {t=1; next}
    t && /^\|/ { if (NF != 6) print NR": "NF-2" cells: "$2 }
    t && !/^\|/ {t=0}
  ' design/FOUNDATION.md)
  if [ -n "$bad" ]; then
    fail "terminology table rows missing columns (need: term / definition / nearest / delta):"
    printf '%s\n' "$bad" | sed 's/^/      /'
  fi
fi

printf -- '---\n%d error / %d warn\n' "$err" "$warn"
[ "$err" -eq 0 ]
