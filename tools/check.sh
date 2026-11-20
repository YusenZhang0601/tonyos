#!/usr/bin/env bash
# 门禁：结构坏了就红。退出码 0 = 结构没坏。
#
# 检查项（新发现的病，加成检查项，不是加一句提醒）：
#   1. 指针可达     AGENTS.md 里提到的路径必须存在
#   2. 索引未过期   docs/INDEX.tsv 必须与新生成的一致
#   3. 状态层字段   STATUS.md 必须有约定的六个二级标题
#   4. 决策账字段   每条 D-xxx 必须有「关系」段
#   5. 敏感文件     索引里不得出现本机环境文件

set -uo pipefail
cd "$(dirname "$0")/.."

err=0
warn=0
fail() { printf 'ERROR %s\n' "$*"; err=$((err+1)); }
note() { printf 'WARN  %s\n' "$*"; warn=$((warn+1)); }

# 1. 指针可达
while IFS= read -r f; do
  [ -z "$f" ] && continue
  [ -e "$f" ] || fail "断链：$f（AGENTS.md 提到但不存在）"
done < <(grep -oE '`[^`]+\.(md|sh|tsv|txt)`' AGENTS.md 2>/dev/null | tr -d '`' | sort -u)

# 2. 索引未过期
if [ ! -f docs/INDEX.tsv ]; then
  fail "docs/INDEX.tsv 缺失，先跑 tools/index.sh"
else
  tmp="$(mktemp)"
  tools/index.sh "$tmp"
  if ! cmp -s "$tmp" docs/INDEX.tsv; then
    fail "索引过期，跑 tools/index.sh 重新生成"
    diff -U0 docs/INDEX.tsv "$tmp" | grep -E '^[+-][^+-]' | head -6 | sed 's/^/      /'
  fi
  rm -f "$tmp"
fi

# 3. 状态层字段
for k in 阶段 在干什么 卡点 下一步 待裁; do
  grep -qx "## $k" docs/STATUS.md 2>/dev/null || fail "STATUS.md 缺字段：## $k"
done

# 4. 决策账最小四字段（用「关系」段代表）
n=$(grep -c '^## D-' docs/DECISIONS.md 2>/dev/null); [ -z "${n:-}" ] && n=0
m=$(grep -c '^- \*\*关系\*\*' docs/DECISIONS.md 2>/dev/null); [ -z "${m:-}" ] && m=0
[ "$n" = "$m" ] || fail "DECISIONS：$n 条决策，但只有 $m 条写了「关系」"

# 5. 敏感文件不得进索引
if grep -qE 'mihomo|三棵树|screenoff' docs/INDEX.tsv 2>/dev/null; then
  fail "索引里出现本机环境文件，检查 tools/index.sh 的匹配范围"
fi

printf -- '---\n%d error / %d warn\n' "$err" "$warn"
[ "$err" -eq 0 ]
