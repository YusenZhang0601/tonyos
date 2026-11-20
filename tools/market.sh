#!/usr/bin/env bash
# Market sweep: read-only snapshot of the competitor field.
#
# Usage: tools/market.sh [--out FILE]
#
# Reads public GitHub data only (no writes, no local environment, no .machine/).
# No token required. Export GITHUB_TOKEN to raise the API rate limits.
# Output is TSV with '#' comment lines, so two sweeps diff cleanly:
#
#   tools/market.sh --out market-2026-11-20.tsv
#   tools/market.sh --out market-2027-02-20.tsv
#   diff market-2026-11-20.tsv market-2027-02-20.tsv
#
# Exit 0 only if every request succeeded; a gap is printed, never guessed.

set -uo pipefail
cd "$(dirname "$0")/.."
exec python3 - "$@" <<'PY'
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
PAUSE = 2.5 if TOKEN else 7.0          # unauthenticated search: 10 requests / minute
PER_QUERY = 8

# The saved queries from docs/COMPETITORS.md, in protocol order.
SEARCHES = [
    "topic:agent-os",
    '"agent-native operating system"',
    '"AI operating system" agents',
    '"agent OS" kernel',
    "append-only ledger agent memory",
    '"agent is the owner"',
    "nixos agent",
    "agent sandbox policy",
]

# Watchlist M-01..M-10 plus one camp-A baseline. Fixed order keeps diffs stable.
WATCH = [
    "Judge-M/Decima",
    "microsoft/mxc",
    "iamlukethedev/Herald-OS",
    "papercomputeco/stereOS",
    "dillondevoe/agent-os",
    "Beach-Bum/Agentix",
    "vahmoh/Veda",
    "jordanhubbard/agentos",
    "gangjig/stateledger",
    "Iam-Raghava/veritas",
    "NovasPlace/CSM",
    "agiresearch/AIOS",
    "kortix-ai/CompanyOS",
]


def clean(value, limit=100):
    text = " ".join(str(value or "").split())
    return text.replace("\t", " ")[:limit]


def get(url):
    request = urllib.request.Request(url, headers={
        "User-Agent": "tonyos-market-sweep",
        "Accept": "application/vnd.github+json",
    })
    if TOKEN:
        request.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, "", json.load(response)
    except urllib.error.HTTPError as error:
        try:
            detail = json.load(error).get("message", "")
        except Exception:
            detail = ""
        return error.code, detail, None
    except Exception as error:
        return 0, str(error), None


def parse_args(argv):
    out = None
    i = 0
    while i < len(argv):
        if argv[i] == "--help":
            print(__doc__ or "usage: tools/market.sh [--out FILE]")
            sys.exit(0)
        if argv[i] == "--out" and i + 1 < len(argv):
            out = argv[i + 1]
            i += 2
            continue
        print(f"unknown argument: {argv[i]}", file=sys.stderr)
        sys.exit(2)
    return out


def main():
    out_path = parse_args(sys.argv[1:])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"# market sweep {now}",
        f"# source api.github.com {'(token)' if TOKEN else '(unauthenticated)'}",
        "# section: search",
        "query\ttotal\trank\tname\tstars\tpushed\tdescription",
    ]
    errors = 0

    for index, query in enumerate(SEARCHES):
        if index:
            time.sleep(PAUSE)
        url = ("https://api.github.com/search/repositories?"
               + urllib.parse.urlencode({
                   "q": query, "sort": "stars", "order": "desc", "per_page": PER_QUERY,
               }))
        status, detail, payload = get(url)
        if status != 200 or payload is None:
            errors += 1
            lines.append(f"# ERROR search {status} {detail} :: {query}")
            print(f"ERROR search {status} {detail}: {query}", file=sys.stderr)
            continue
        for rank, item in enumerate(payload.get("items", []), start=1):
            lines.append("\t".join([
                clean(query), str(payload.get("total_count", "")), str(rank),
                item.get("full_name", ""), str(item.get("stargazers_count", "")),
                clean(item.get("pushed_at", ""), 10), clean(item.get("description")),
            ]))

    lines.append("# section: watch")
    lines.append("name\tstars\tpushed\tcreated\tlicense\tarchived\tdescription")
    for full_name in WATCH:
        status, detail, payload = get(f"https://api.github.com/repos/{full_name}")
        if status != 200 or payload is None:
            errors += 1
            lines.append(f"# ERROR repo {status} {detail} :: {full_name}")
            print(f"ERROR repo {status} {detail}: {full_name}", file=sys.stderr)
            continue
        license_id = (payload.get("license") or {}).get("spdx_id", "")
        lines.append("\t".join([
            full_name, str(payload.get("stargazers_count", "")),
            clean(payload.get("pushed_at", ""), 10), clean(payload.get("created_at", ""), 10),
            license_id or "-", "yes" if payload.get("archived") else "no",
            clean(payload.get("description")),
        ]))

    lines.append(f"# queries {len(SEARCHES)}  watch {len(WATCH)}  errors {errors}")
    text = "\n".join(lines) + "\n"

    if out_path:
        with open(out_path, "w", encoding="utf-8") as handle:
            handle.write(text)
        print(f"wrote {out_path} ({len(lines)} lines, {errors} errors)", file=sys.stderr)
    else:
        sys.stdout.write(text)

    return 1 if errors else 0


sys.exit(main())
PY
