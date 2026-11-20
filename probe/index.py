"""C: is the head index a faithful projection, and is it O(1)?

Two questions, two checks:
  1. after 200 mixed operations, the indexed head equals a brute-force scan
  2. a fresh Ledger on the same log derives the same heads (the index is not truth)

Run: python3 probe/index.py
"""
import os
import random
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import Ledger                  # noqa: E402

W1 = "world:lab"


def brute_active(rows):
    """The same one-pass retraction cascade as `active()`, written independently."""
    live = {r["id"]: True for r in rows}
    for r in rows:
        if not live.get(r["id"]):
            continue
        for target in r["replaces"]:
            if live.get(target):
                live[target] = False
    return [r for r in rows if live[r["id"]]]


def brute_head(rows, world):
    head = None
    for r in brute_active(rows):
        if (r["predicate"] == "is" and isinstance(r["value"], dict)
                and "root" in r["value"] and r["world"] == world):
            head = r["id"]
    return head


def main():
    base = tempfile.mkdtemp(dir="/tmp")
    path = os.path.join(base, "claims.log")
    try:
        led = Ledger(path)
        led.bootstrap(W1, {}, by="sensor:fs")
        worlds = [W1]
        roots = {W1: [led.current_root(W1)]}
        rng = random.Random(7)
        mismatches = 0

        for i in range(500):
            op = rng.random()
            if op < 0.55:
                led.commit(W1, {f"/f{i}": "x"}, "agent:a", led.current_root(W1))
                roots[W1].append(led.current_root(W1))
            elif op < 0.70:
                led.tick(W1, "agent:a", led.current_root(W1))
                roots[W1].append(led.current_root(W1))
            elif op < 0.85:
                to = rng.choice(roots[W1])
                led.rollback(W1, to, "human:tony", led.current_root(W1))
                roots[W1].append(led.current_root(W1))
            elif op < 0.95:
                w = f"world:fork{i}"
                led.commit(w, {f"/g{i}": "y"}, "agent:a", led.current_root(W1))
                worlds.append(w)
                roots[w] = [led.current_root(w)]
            else:
                led.append("pkg:x", "is", {"note": i}, W1, by="agent:a")

            for w in worlds:
                if led.current_root(w) != brute_head(led.rows, w):
                    mismatches += 1

        print("--- equivalence, 500 mixed operations")
        print(f"  worlds                          : {len(worlds)}")
        print(f"  claims                          : {len(led.rows)}")
        print(f"  head mismatches vs brute force  : {mismatches}")

        fresh = Ledger(path, writable=False)
        rebuilt = sum(1 for w in worlds if fresh.current_root(w) != led.current_root(w))
        print(f"  rebuild from the log, mismatches: {rebuilt}")

        # A fresh log, pure commits: the index must be O(1) after load.
        p2 = os.path.join(base, "pure.log")
        led2 = Ledger(p2)
        led2.bootstrap(W1, {}, by="sensor:fs")
        before = led2.stats()
        for i in range(50):
            led2.commit(W1, {f"/p{i}": "x"}, "agent:a", led2.current_root(W1))
        after = led2.stats()
        delta = {k: after[k] - before[k] for k in after}
        n = max(delta["commits"], 1)
        print("\n--- after load, 50 pure commits")
        print(f"  full reloads per commit         : {delta['full_loads']/n:.2f}")
        print(f"  row scans per commit            : {delta['scans']/n:.2f}")
        print(f"  rows scanned per commit         : {delta['rows_scanned']/n:.0f}")
        print(f"  bytes read per commit           : {delta['bytes_read']/n:.0f}")
        print(f"  head lookup is a dict read      : {delta['scans'] == 0}")
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    main()
