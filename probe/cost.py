"""A: where does a commit spend its time?

No optimisation here. Counters and timers only: bytes read, full reloads, row scans,
and the seconds spent in each. Run against the same worlds `group.py` uses.

Run: python3 probe/cost.py
"""
import os
import shutil
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import Ledger, Conflict          # noqa: E402

W1 = "world:lab"


def snapshot(stats):
    return dict(stats)


def delta(after, before):
    return {k: after[k] - before[k] for k in after}


def measure(mode, writers, per_writer):
    base = tempfile.mkdtemp(dir="/tmp")
    path = os.path.join(base, "claims.log")
    shared = None
    try:
        if mode == "group":
            shared = Ledger(path, group=True)
            shared.bootstrap(W1, {}, by="sensor:fs")
            ledgers = [shared] * writers
        else:
            Ledger(path).bootstrap(W1, {}, by="sensor:fs")
            ledgers = [Ledger(path) for _ in range(writers)]
        before = [snapshot(l.stats()) for l in ledgers]
        t0 = time.perf_counter()

        def worker(k):
            led = ledgers[k]
            done = 0
            while done < per_writer:
                try:
                    led.commit(W1, {f"/t{k}": "x"}, f"agent:{k}", led.current_root(W1))
                    done += 1
                except Conflict:
                    if mode != "group":
                        led.reload()
        threads = [threading.Thread(target=worker, args=(k,)) for k in range(writers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        wall = time.perf_counter() - t0

        after = [snapshot(l.stats()) for l in ledgers]
        sums = {k: sum(delta(a, b)[k] for a, b in zip(after, before)) for k in after[0]}
        total = writers * per_writer
        n = max(sums["commits"], 1)
        return {
            "total": total,
            "sec": wall,
            "per_s": total / wall,
            "bytes": sums["bytes_read"] / n,
            "loads": sums["full_loads"] / n,
            "scans": sums["scans"] / n,
            "rows": sums["rows_scanned"] / n,
            "load_ms": 1000 * sums["load_s"] / n,
            "scan_ms": 1000 * sums["scan_s"] / n,
            "write_ms": 1000 * sums["write_s"] / n,
            "wall_ms": 1000 * wall / total,
        }
    finally:
        if shared:
            shared.close()
        shutil.rmtree(base, ignore_errors=True)


def main():
    print("--- per commit, after a fresh bootstrap (10 commits per writer)")
    print(f"{'path':<7}{'w':>3}{'total':>7}{'per s':>7}{'read B':>9}{'reload':>8}"
          f"{'scans':>7}{'rows':>8}{'load ms':>9}{'scan ms':>9}{'write ms':>10}{'wall ms':>9}")
    for mode in ("locked", "group"):
        for w, n in ((1, 10), (8, 10), (32, 5)):
            r = measure(mode, w, n)
            print(f"{mode:<7}{w:>3}{r['total']:>7}{r['per_s']:>7.1f}{r['bytes']:>9.0f}"
                  f"{r['loads']:>8.1f}{r['scans']:>7.1f}{r['rows']:>8.0f}"
                  f"{r['load_ms']:>9.2f}{r['scan_ms']:>9.2f}{r['write_ms']:>10.2f}{r['wall_ms']:>9.2f}")

    print("\n--- read this as")
    print("  reload > 0 means the whole log was re-read for that commit.")
    print("  read B is bytes read per commit; compare it with one frame (~250 B).")
    print("  rows is rows scanned per commit; compare it with the log length.")


if __name__ == "__main__":
    main()
