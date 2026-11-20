"""E3: two agents, one world. What actually happens?

Three outcomes were on the table: one fails, one overwrites, or both survive by
forking. This runs real processes against one file and reports which one happens
— first with no compare-and-swap, then with one.

Run: python3 probe/concurrent.py

A forced interleaving is used (both read the root, then wait) so the race is
reachable on a 2-core machine. That is a demonstration of a reachable schedule,
not a measurement of how often it happens naturally.
"""
import fcntl
import json
import multiprocessing as mp
import os
import shutil
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import Ledger, NotFound          # noqa: E402

W1 = "world:lab"
CTX = mp.get_context("fork")


class Conflict(Exception):
    pass


def commit_at(path, world, files, by, expect=None):
    """Compare-and-swap: only advance `world` if its root is still `expect`.

    For a world with no root, `expect` is the parent viewpoint — that is a fork
    (D-035), not a conflict.
    """
    with open(path + ".lock", "a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        led = Ledger(path)                       # fresh under the lock: no stale seq
        roots = [r for r in led.active()
                 if r["predicate"] == "is" and "root" in r["value"] and r["world"] == world]
        if roots:
            cur = led.current_root(world)
            if expect is not None and cur != expect:
                raise Conflict(f"expected {expect}, current {cur}")
            prev = cur
        else:
            if expect is None:
                raise Conflict(f"{world} has no root and no parent viewpoint")
            prev = expect
        did = led.append(by, "did", {"verb": "write", "view": prev,
                                     "result": {"files": files}},
                         world, by=by, because=[prev])
        return led.append("world", "is", {"root": {"files": files}},
                          world, by=by, because=[did])


def seed(path):
    led = Ledger(path)
    return led.append("world", "is", {"root": {"files": {}}}, W1, by="sensor:fs")


# ------------------------------------------------------------------ naive race
def _naive(args):
    path, barrier, q, name = args
    led = Ledger(path)
    expect = led.current_root(W1)
    barrier.wait()
    time.sleep(0.05)                             # widen the window, deliberately
    did = led.append(f"agent:{name}", "did",
                     {"verb": "write", "view": expect,
                      "result": {"files": {f"/{name}": "x"}}},
                     W1, by=f"agent:{name}", because=[expect])
    root = led.append("world", "is", {"root": {"files": {f"/{name}": "x"}}},
                      W1, by=f"agent:{name}", because=[did])
    q.put((name, expect, root))


def naive_race(path):
    print("--- A · no compare-and-swap: two processes, one world")
    barrier, q = CTX.Barrier(2), CTX.Queue()
    ps = [CTX.Process(target=_naive, args=((path, barrier, q, n),)) for n in ("a", "b")]
    for p in ps:
        p.start()
    results = [q.get(timeout=10) for _ in ps]
    for p in ps:
        p.join()
    led = Ledger(path, writable=False)
    roots = [r for r in led.active()
             if r["predicate"] == "is" and "root" in r["value"] and r["world"] == W1]
    commits = [r for r in roots if r["because"]]
    heads = {led.get(r["because"][0])["value"]["view"] for r in commits}
    seqs = [r["seq"] for r in led.rows]
    print(f"  both processes returned a root   : {len(results) == 2}")
    print(f"  roots in {W1:<12}             : {len(roots)} (1 seed + {len(commits)} commits)")
    print(f"  commits sharing one parent       : {len(heads)} parent(s) for {len(commits)} commits")
    print(f"  duplicate sequence numbers       : {len(seqs) != len(set(seqs))}")
    print(f"  what the screen would show       : {len(commits)} heads, silently")


# -------------------------------------------------------------------- cas race
def _cas(args):
    path, barrier, q, name = args
    led = Ledger(path, writable=False)
    expect = led.current_root(W1)
    barrier.wait()
    time.sleep(0.05)
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
    res = [q.get(timeout=10) for _ in ps]
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
    t = time.perf_counter()
    for i in range(n):
        commit_at(path, W1, {f"/c{i}": "x"}, "agent:c")
    dt = time.perf_counter() - t
    print(f"  {n} commits in {dt:.2f}s          : {n/dt:.1f} commits/s "
          f"({1000*dt/n:.0f} ms each, 2 fsyncs per commit)")
    print("  group commit is not applied yet (D-037 predicted it; E1 measured 35x)")


def main():
    base = tempfile.mkdtemp(dir="/tmp")
    try:
        p1 = os.path.join(base, "naive")
        os.makedirs(p1)
        seed(os.path.join(p1, "claims.log"))
        naive_race(os.path.join(p1, "claims.log"))

        p2 = os.path.join(base, "cas")
        os.makedirs(p2)
        seed(os.path.join(p2, "claims.log"))
        cas_race(os.path.join(p2, "claims.log"))

        cost(os.path.join(p2, "claims.log"))
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    main()
