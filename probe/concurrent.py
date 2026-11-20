"""E3: two agents, one world. What actually happens?

Part A shows the unsafe path is gone: a root cannot be appended, only committed.
Part B races two real processes through the ledger's compare-and-swap.
Part C measures what correctness costs.

Run: python3 probe/concurrent.py

A forced interleaving is used (both read the head, then wait), so the race is
reachable on a 2-core machine. That demonstrates a reachable schedule, not how
often it happens naturally.
"""
import multiprocessing as mp
import os
import shutil
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import Ledger, Conflict, NotFound     # noqa: E402

W1 = "world:lab"
CTX = mp.get_context("fork")


def commit_at(path, world, files, by, expect):
    return Ledger(path).commit(world, files, by, expect)


def seed(path):
    return Ledger(path).bootstrap(W1, {}, by="sensor:fs")


# ------------------------------------------------------------------ the guard
def guard(path):
    print("--- A · the unsafe way to advance a world")
    led = Ledger(path)
    try:
        led.append("world", "is", {"root": {"files": {}}}, W1, by="agent:x")
        print("  append a root                   : ACCEPTED (the guard is missing)")
    except AssertionError as exc:
        print(f"  append a root                   : refused — {exc}")
    try:
        led.commit(W1, {"/x": "1"}, "agent:x", expect="not-a-viewpoint")
    except (Conflict, NotFound) as exc:
        print(f"  commit with a bad head          : {type(exc).__name__} — {exc}")


# -------------------------------------------------------------------- cas race
def _cas(args):
    path, barrier, q, name = args
    expect = Ledger(path, writable=False).current_root(W1)
    barrier.wait()
    time.sleep(0.05)                             # widen the window, deliberately
    try:
        root = commit_at(path, W1, {f"/{name}": "x"}, f"agent:{name}", expect)
        q.put((name, "ok", expect, root))
    except Conflict as exc:
        q.put((name, "conflict", expect, str(exc)))


def cas_round(path, i):
    barrier, q = CTX.Barrier(2), CTX.Queue()
    ps = [CTX.Process(target=_cas, args=((path, barrier, q, n),)) for n in ("a", "b")]
    for p in ps:
        p.start()
    res = [q.get(timeout=15) for _ in ps]
    for p in ps:
        p.join()
    ok = [r for r in res if r[1] == "ok"]
    lost = [r for r in res if r[1] == "conflict"]
    if len(ok) != 1 or len(lost) != 1:
        return False, res
    loser, expect = lost[0][0], lost[0][2]
    fork = commit_at(path, f"world:fork{i}", {f"/{loser}": "x"}, f"agent:{loser}", expect)
    led = Ledger(path, writable=False)
    fork_view = led.visible(fork)
    ok_tree = [r for r in led.active() if r["id"] == ok[0][3]][0]["value"]["root"]
    return True, (loser, ok_tree, fork, fork_view)


def cas_race(path, rounds=5):
    print("\n--- B · compare-and-swap: exactly one advances, the other is told")
    wins = 0
    for i in range(rounds):
        good, detail = cas_round(path, i)
        if good:
            wins += 1
    print(f"  rounds                          : {rounds}")
    print(f"  exactly one winner per round    : {wins == rounds}")
    loser, ok_tree, fork, fork_view = detail
    led = Ledger(path, writable=False)
    fork_files = led.get(fork)["value"]["root"]["files"]
    sees_parent = any(r["world"] == W1 for r in fork_view)
    sees_winner = ok_tree["files"].get(f"/{loser}") is not None
    print(f"  loser forked instead of dying   : {fork_files == {f'/{loser}': 'x'}}")
    print(f"  fork sees the parent's claims   : {sees_parent}")
    print(f"  fork does not see the winner    : {not sees_winner}")


# -------------------------------------------------------------------- the cost
def cost(path, n=5):
    print("\n--- C · what correctness costs, one world, sequential")
    led = Ledger(path)
    t = time.perf_counter()
    for i in range(n):
        led.commit(W1, {f"/c{i}": "x"}, "agent:c", expect=led.current_root(W1))
    dt = time.perf_counter() - t
    print(f"  {n} commits in {dt:.2f}s          : {n/dt:.1f} commits/s "
          f"({1000*dt/n:.0f} ms each, 1 fsync per commit)")
    print("  group commit is measured separately in probe/group.py (D-037)")


def main():
    base = tempfile.mkdtemp(dir="/tmp")
    try:
        p = os.path.join(base, "claims.log")
        seed(p)
        guard(p)

        p2 = os.path.join(base, "cas.log")
        seed(p2)
        cas_race(p2)

        cost(p2)
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    main()
