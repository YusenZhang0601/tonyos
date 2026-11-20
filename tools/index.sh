#!/usr/bin/env bash
# 生成全仓文档索引。
# 用法：tools/index.sh [输出路径]    默认 docs/INDEX.tsv
#
# 索引范围（刻意收窄）：
#   - 根目录与三层内的 *.md / *.txt
#   - tools/ 下的 *.sh
# 排除：lost+found/、.git/、以及无扩展名的本机环境脚本与 *.yaml（含凭据，不进索引）。

set -euo pipefail
cd "$(dirname "$0")/.."

out="${1:-docs/INDEX.tsv}"
mkdir -p "$(dirname "$out")"

{
  printf 'path\tsha12\tlines\tmtime\n'
  {
    find . -maxdepth 3 \( -path ./lost+found -o -path ./.git \) -prune -o \
      -type f \( -name '*.md' -o -name '*.txt' \) -print
    find tools -maxdepth 1 -type f -name '*.sh'
  } | sed 's|^\./||' | sort -u | while IFS= read -r f; do
    [ -f "$f" ] || continue
    printf '%s\t%s\t%s\t%s\n' \
      "$f" \
      "$(sha256sum "$f" | cut -c1-12)" \
      "$(wc -l < "$f" | tr -d ' ')" \
      "$(date -r "$f" +%Y-%m-%d)"
  done
} > "$out"
