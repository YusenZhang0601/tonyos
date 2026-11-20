# Goal: close the write path

> A bounded stage, not a direction. When every item below is verified, the stage is
> over. If a new rule is needed, it is raised, not applied.

**Why this stage.** Every later layer — the Screen, v0 install, the adapters — writes
through this path. It is the system's only hot path (FOUNDATION §8.2). Today it has
three defects: two `fsync`s per commit, no group commit, and compare-and-swap exists
only in `probe/concurrent.py` — the ordinary `commit()` is still unsafe. Closing this
now means every later feature inherits a correct, fast path instead of a broken one.

**Baselines to beat or explain** (measured, this HDD):
- 15.5 commits/s with CAS, two `fsync`s per commit (E3)
- 102 commits/s per-commit `fsync`, 3,586/s with group commit, raw appends only (E1)
- 65 ms mean per commit, 2 `fsync`s

## Definition of done

1. **One write path.** `Ledger.commit(world, files, by, expect)` is the only way to
   advance a world. No public API appends a root without a head check. `demo.py` uses
   it; the unsafe path is deleted, not deprecated.
2. **One fsync per commit.** Both frames are written, then one `fsync`. The number of
   `fsync` calls per commit is shown, not asserted.
3. **Group commit.** `probe/group.py` reports commits/s, p50 and p99 for 1 / 2 / 4 / 8
   writers, plus the number of `fsync`s per commit under load. The wait window is
   bounded; a writer must not wait forever.
4. **Invariants survive the change.** `demo.py` 8/8; `crash.py` keeps every cut-point
   invariant; `concurrent.py` still produces exactly one winner per round, and the
   loser forks; a corrupt frame is still refused.
5. **The numbers are compared** with the baselines above, and the report says what was
   gained, what was spent, and which tier (throughput / latency / footprint) paid.
6. **State is clean.** `tools/check.sh` 0/0, working tree clean, pushed.

## Order

Each step must leave the previous one green. Do not parallelise.

- **A. CAS into the store.** Move the compare-and-swap into `Ledger`; make it the only
  path that advances a world. Replace the unsafe call sites in `demo.py` and
  `concurrent.py`. A conflict raises; it is never silent.
- **B. One fsync per commit.** Write the `did` and the root, then `fsync` once. Decide
  and state what an orphan `did` means; if it becomes impossible, say how.
- **C. Group commit.** One `fsync` serves every commit that arrived during the window.
  Bound the wait. Measure.
- **D. Re-run everything.** Record pass 7 in `probe/README.md`: the table, the
  before/after, and what is still untested.

## Stop and ask the owner

Do not guess on these:

- performance floors (the numbers themselves)
- where a conflict is recorded (`did` cannot be global; the world it failed to advance
  is the one it must not write to)
- whether a failed attempt must survive a crash — it costs the second `fsync`
- anything that changes the vocabulary, adds a predicate, or adds a layer
- mounting or formatting `/dev/sda3` / `/dev/sda4`
- touching `.machine/` or `编译试验机/`, or putting machine details into git
- another session's uncommitted changes in `/lab`

## Rules

- **Done means evidence**: the command and its output. Unrun work is labelled
  *not verified*.
- **Raise, do not apply** a design choice discovered while implementing.
- **Never delete old text**; mark it superseded with a back-pointer.
- Small commits, each with the gate green, each pushed.
- No heavy builds on this machine. This stage is Python; keep it Python.
- After three failed attempts at the same problem, stop and report the attempts.
