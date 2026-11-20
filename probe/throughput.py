"""E1: what is the throughput ceiling — the shared log, or fsync?

D-037 says throughput outranks latency and predicts group commit. This either
confirms that prediction or kills it. It also tests D-038: the same claim must
get the same id in two independent stores.

Run: python3 probe/throughput.py

What this can prove: software does or does not serialise what the device allows.
What it cannot prove: cluster scaling (2 cores), power-loss durability (fsync is
not a power cut), or anything about a real block device (this is ext4 on a file).
"""
import json
import os
import shutil
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import Ledger                      # noqa: E402

DURATION = 1.2
PAD = 110


def record(i, world):
    return (json.dumps({"seq": i, "subject": "bench", "predicate": "did",
                        "world": world, "by": "agent:bench",
                        "value": {"pad": "x" * PAD}}, sort_keys=True) + "\n").encode()


class Group:
    """One fsync serves every write that arrived while it was running."""

    def __init__(self, path, interval=0.005):
        self.fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        self.cv = threading.Condition()
        self.pending = 0
        self.flushed = 0
        self.stop = False
        self.interval = interval
        self.thread = threading.Thread(target=self._flush, daemon=True)
        self.thread.start()

    def _flush(self):
        while not self.stop:
            with self.cv:
                if self.pending == self.flushed:
                    self.cv.wait(self.interval)
                    continue
                target = self.pending
            os.fsync(self.fd)
            with self.cv:
                self.flushed = target
                self.cv.notify_all()

    def wait(self):
        with self.cv:
            self.pending += 1
            ticket = self.pending
            self.cv.notify()
            while self.flushed < ticket:
                self.cv.wait()

    def close(self):
        self.stop = True
        with self.cv:
            self.cv.notify_all()
        self.thread.join()
        os.fsync(self.fd)
        os.close(self.fd)


def run(mode, writers, workdir):
    counts = [0] * writers
    lat = [[] for _ in range(writers)]
    barrier = threading.Barrier(writers + 1)

    shared_fd = os.open(os.path.join(workdir, "shared.log"),
                        os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    group = Group(os.path.join(workdir, "group.log")) if mode == "group" else None

    def worker(k):
        fd = shared_fd if mode in ("shared+fsync", "group", "nofsync") else \
            os.open(os.path.join(workdir, f"w{k}.log"),
                    os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        barrier.wait()
        i = 0
        while time.perf_counter() < deadline:
            t0 = time.perf_counter()
            os.write(fd, record(i, f"world:{k}"))
            if mode in ("shared+fsync", "shard+fsync"):
                os.fsync(fd)
            elif mode == "group":
                group.wait()
            lat[k].append(time.perf_counter() - t0)
            i += 1
        counts[k] = i
        if fd != shared_fd:
            os.close(fd)

    deadline = time.perf_counter() + DURATION
    threads = [threading.Thread(target=worker, args=(k,)) for k in range(writers)]
    for t in threads:
        t.start()
    barrier.wait()
    for t in threads:
        t.join()
    if group:
        group.close()
    os.close(shared_fd)

    samples = sorted(x for row in lat for x in row)
    total = sum(counts)
    return {
        "ops": total,
        "ops_s": total / DURATION,
        "mean_ms": 1000 * sum(samples) / len(samples) if samples else 0,
        "p99_ms": 1000 * samples[int(len(samples) * 0.99)] if samples else 0,
    }


def identity_check():
    """D-038: the same claim, two independent stores, one name."""
    a = tempfile.mkdtemp(dir="/tmp")
    b = tempfile.mkdtemp(dir="/tmp")
    try:
        la, lb = Ledger(os.path.join(a, "x.jsonl")), Ledger(os.path.join(b, "x.jsonl"))
        kw = dict(subject="host", predicate="is", value={"arch": "x86_64"},
                  world="world:lab", by="sensor:cpu")
        ia = la.append(**kw)
        ib = lb.append(**kw)
        again = la.append(**kw)
        print("\n--- D-038: identity is content, not position")
        print(f"  node A id          : {ia}")
        print(f"  node B id          : {ib}")
        print(f"  same across nodes  : {ia == ib}")
        print(f"  re-assert collapses: {again == ia and len(la.rows) == 1}"
              f" (duplicates={la.duplicates})")
    finally:
        shutil.rmtree(a, ignore_errors=True)
        shutil.rmtree(b, ignore_errors=True)


def main():
    identity_check()
    print("\n--- throughput: 4 layouts x 1/2/4/8 writers, %.1fs each" % DURATION)
    print(f"{'layout':<14}{'writers':>8}{'ops':>7}{'ops/sec':>9}{'mean ms':>9}{'p99 ms':>8}")
    for mode in ("shared+fsync", "shard+fsync", "group", "nofsync"):
        for writers in (1, 2, 4, 8):
            d = tempfile.mkdtemp(dir="/tmp")
            try:
                r = run(mode, writers, d)
            finally:
                shutil.rmtree(d, ignore_errors=True)
            print(f"{mode:<14}{writers:>8}{r['ops']:>7}{r['ops_s']:>9.0f}"
                  f"{r['mean_ms']:>9.2f}{r['p99_ms']:>8.2f}")

    print("\n--- what to read from this")
    print("  if shared+fsync does not scale with writers, the shared log is not the")
    print("  ceiling -- the device is. If group >> shared+fsync, D-037's prediction holds.")


if __name__ == "__main__":
    main()
