"""E4: what does group commit actually buy?

Same world, same commits, two paths:
  locked  — a file lock and one fsync per commit (D-039/D-040)
  group   — one fsync serves every commit that arrived during a 2 ms window

Writers retry on Conflict, as a real agent would. Latency is end-to-end: first
attempt to durable commit, so a retry is charged to the writer that paid it.

Run: python3 probe/group.py
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
DURATION = 1.5


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * p))] if xs else 0.0


def run(mode, writers, duration=DURATION, window=0.002):
    base = tempfile.mkdtemp(dir="/tmp")
    path = os.path.join(base, "claims.log")
    shared = None
    try:
        if mode == "group":
            shared = Ledger(path, group=True, window=window)
            shared.bootstrap(W1, {}, by="sensor:fs")
        else:
            Ledger(path).bootstrap(W1, {}, by="sensor:fs")

        stop = time.perf_counter() + duration
        lats = [[] for _ in range(writers)]
        counts = [0] * writers
        ledgers = [shared] * writers if mode == "group" else [Ledger(path) for _ in range(writers)]

        def worker(k):
            led = ledgers[k]
            while time.perf_counter() < stop:
                t0 = time.perf_counter()
                while True:
                    try:
                        led.commit(W1, {f"/t{k}": "x"}, f"agent:{k}", led.current_root(W1))
                        break
                    except Conflict:
                        if mode != "group":
                            led.reload()
                lats[k].append(time.perf_counter() - t0)
                counts[k] += 1

        threads = [threading.Thread(target=worker, args=(k,)) for k in range(writers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        total = sum(counts)
        fsyncs = shared.fsyncs if shared else sum(l.fsyncs for l in ledgers)
        flat = [x for row in lats for x in row]
        batches, sizes = shared.batch_stats if shared else (0, [])
        avg = sum(sizes) / len(sizes) if sizes else 0
        return total, total / duration, 1000 * pct(flat, 0.50), 1000 * pct(flat, 0.99), \
            fsyncs / max(total, 1), avg
    finally:
        if shared:
            shared.close()
        shutil.rmtree(base, ignore_errors=True)


def main():
    print("--- group commit: same world, 1.5 s per cell")
    print(f"{'path':<8}{'writers':>8}{'commits':>9}{'per s':>8}{'p50 ms':>9}{'p99 ms':>9}{'fsync/commit':>14}{'batch':>7}")
    for mode in ("locked", "group"):
        for w in (1, 2, 4, 8):
            n, rate, p50, p99, fpc, avg = run(mode, w)
            print(f"{mode:<8}{w:>8}{n:>9}{rate:>8.0f}{p50:>9.2f}{p99:>9.2f}{fpc:>14.2f}{avg:>7.1f}")
    print("\n--- window sweep, 8 writers (throughput first, latency second)")
    print(f"{'window':<8}{'commits':>9}{'per s':>8}{'p50 ms':>9}{'p99 ms':>9}{'batch':>7}")
    for ms in (2, 5, 10):
        n, rate, p50, p99, fpc, avg = run("group", 8, window=ms / 1000)
        print(f"{ms:<7}ms{n:>9}{rate:>8.0f}{p50:>9.2f}{p99:>9.2f}{avg:>7.1f}")
    print("\n--- beyond 8 writers: where the batch stops growing (2 ms window)")
    print(f"{'writers':<8}{'commits':>9}{'per s':>8}{'p50 ms':>9}{'p99 ms':>9}{'batch':>7}")
    for w in (8, 16, 32):
        n, rate, p50, p99, fpc, avg = run("group", w)
        print(f"{w:<8}{n:>9}{rate:>8.0f}{p50:>9.2f}{p99:>9.2f}{avg:>7.1f}")

    print("\n  fsync/commit below 1 means the window is doing its job.")
    print("  p99 includes Conflict retries in both paths.")
    print("  a writer waits for its own durability, so a batch is at most `writers`;")
    print("  group commit's gain scales with concurrency, not with one fast writer.")
    print("  when the batch stops growing, the ceiling is the commit path, not the disk.")


if __name__ == "__main__":
    main()
