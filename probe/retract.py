"""D-041: events are not retractable; beliefs are, to a fixpoint.

The oracle here is independent of `active()`: it enumerates every subset of claims
and keeps the ones that satisfy "a claim is active iff no active claim retracts
it". For an acyclic graph there is exactly one such set. This is how the first
version of the index test missed the bug — it reimplemented the same one-pass
cascade and agreed with itself.

Run: python3 probe/retract.py
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import Ledger, Conflict          # noqa: E402

W = "world:lab"
HUMAN = "human:tony"


def consistent_sets(rows):
    """Every subset S where x is in S exactly when no member of S retracts x."""
    ids = [r["id"] for r in rows]
    index = {cid: i for i, cid in enumerate(ids)}
    retracts = [{index[t] for t in r["replaces"] if t in index} for r in rows]
    n = len(rows)
    out = []
    for mask in range(1 << n):
        ok = True
        for i in range(n):
            active = bool(mask >> i & 1)
            retracted = any((mask >> j & 1) and i in retracts[j] for j in range(n))
            if active == retracted:
                ok = False
                break
        if ok:
            out.append({ids[i] for i in range(n) if mask >> i & 1})
    return out


def build(spec):
    path = os.path.join(tempfile.mkdtemp(dir="/tmp"), "claims.log")
    led = Ledger(path)
    ids = []
    for i, repl in enumerate(spec):
        ids.append(led.append("x", "counts", {"form": "representation", "v": i},
                              "*", by=HUMAN,
                              replaces=[ids[j] for j in repl]))
    return led, ids


def case(name, spec):
    led, ids = build(spec)
    got = {r["id"] for r in led.active()}
    sets = consistent_sets(led.rows)
    unique = sets[0] if len(sets) == 1 else None
    print(f"  {name:<28} active={len(got)}  consistent sets={len(sets)}  "
          f"match={got == unique if unique is not None else 'n/a'}")
    if unique is not None and got != unique:
        print("    MISMATCH", got, unique)
    return led, got, sets


def main():
    print("--- the fixpoint, against an independent subset oracle")
    case("a <- b", [[], [0]])
    case("a <- b <- c", [[], [0], [1]])
    case("a <- b <- c <- d", [[], [0], [1], [2]])
    case("a <- b, a <- c, b <- d", [[], [0], [0], [1]])

    print("  a retraction cycle cannot be built through the API: a retraction may")
    print("  only name a claim that already exists, so the graph is acyclic. The")
    print("  cycle branch in active() is defensive, not reachable.")

    print("\n--- events cannot be retracted")
    led, _ = build([[]])
    did = led.append("agent:x", "did", {"verb": "read", "target": "/x"},
                     W, by="agent:x")
    try:
        led.append("x", "counts", {"form": "representation", "v": 9}, "*",
                   by=HUMAN, replaces=[did])
        print("  retract a did                 : ACCEPTED (bad)")
    except AssertionError as exc:
        print(f"  retract a did                 : refused — {exc}")

    print("\n--- a spent approval cannot come back")
    led, _ = build([[]])
    approval = led.append("agent:main", "counts",
                          {"form": "representation", "approves": "send"}, "*",
                          by=HUMAN)
    send = led.append("agent:main", "did", {"verb": "send", "target": "mail"},
                      W, by="agent:main", replaces=[approval])
    live = {r["id"] for r in led.active()}
    print(f"  approval active after send    : {approval in live}")
    print(f"  send active                   : {send in live}")
    try:
        led.append("x", "counts", {"form": "representation", "v": 9}, "*",
                   by=HUMAN, replaces=[send])
        print("  retract the send              : ACCEPTED (bad)")
    except AssertionError as exc:
        print(f"  retract the send              : refused — {exc}")
    print(f"  approval active after refusal : {approval in {r['id'] for r in led.active()}}")


if __name__ == "__main__":
    main()
