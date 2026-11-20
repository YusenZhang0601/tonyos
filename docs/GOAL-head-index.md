# Goal: make the head O(1)

> **Status: met** (2026-11-21). Evidence: `probe/README.md` pass 8, `probe/index.py`
> and `probe/cost.py`.
> The next stage is not opened here; see the three candidates in `docs/STATUS.md`.

> A bounded stage. When every item below is verified, the stage is over. A new rule is
> raised, not applied.

**Why this stage.** Pass 7's ceiling is not the disk: throughput flattens at ~250/s
while `fsync/commit` is already 0.16. Two suspects, and they must be measured before
either is "fixed":

1. `_exclusive` calls `_load()` on **every** commit, so each commit re-reads and
   re-parses the whole log. If true, cost is O(log size) per commit.
2. `current_root()` and the head check call `active()`, which scans every row.

The fix is the same for both: read only what is new, and keep the head as an index.
The index is a **projection** — rebuilt from the log, never a second truth.

## Definition of done

1. **Evidence of the cause, before the fix.** Counters for bytes read and full scans
   per commit. At steady state a commit must read O(one frame), not O(the log).
2. **Incremental tail.** `_exclusive` reads only bytes appended since the last
   observed offset, under the lock; a torn tail is still cut and counted.
3. **O(1) head.** `current_root` and the head check do not scan. A new root sets the
   head; a retraction that targets a root (a rollback) is correct; a rollback of a
   rollback matches the brute-force result.
4. **The index is rebuildable.** Open a fresh `Ledger` on the same log: identical
   heads. Deleting the index changes nothing; the log is the only truth.
5. **Randomised equivalence.** 500 mixed operations (commit / tick / rollback / fork)
   against a brute-force head function: 0 mismatches.
6. **Old probes stay green.** `demo` 8/8, `crash` invariants, `concurrent` 5/5, gate 0/0.
7. **Numbers.** Re-run `probe/group.py`; compare 1 / 8 / 32 writers with pass 7
   (39 / 182–195 / 255 per s, batch 8–9). Say what moved and what did not.
8. **State is clean.** Gate 0/0, working tree clean, pushed.

## Order

- **A. Measure first.** Add counters (bytes read, rows scanned, full reloads) to the
  current code. Run `group.py` at 1/8/32 and show where the time goes. Do not optimise
  before this output exists.
- **B. Incremental tail.** Replace the full `_load` in `_exclusive` with a tail read
  from the last offset. Keep truncation under the lock. Verify `crash.py` still cuts
  and counts.
- **C. Head index.** Per-world head, updated on append, rebuilt on open. Retraction of
  a root recomputes that world (rare); tickets that retract counts do not.
- **D. Equivalence + numbers.** Randomised test against brute force, rebuild test,
  `group.py`, pass 8 in `probe/README.md`.

Each step leaves the previous green. Do not parallelise.

## Stop and ask the owner

- performance floors (the numbers themselves)
- whether `visible()` also needs an index — it is still O(n), and the Screen will use it
- any change to the on-disk format
- keeping the whole log in memory: the probe does, the core cannot. Paging is out of
  scope and needs a decision.
- mounting or formatting `/dev/sda3` / `/dev/sda4`
- touching `.machine/` or `编译试验机/`, or putting machine details into git
- another session's uncommitted changes in `/lab`

## Rules

- **Done means evidence**: command and output. Unrun work is labelled *not verified*.
- **Measure before optimising.** A suspected cause is not a cause.
- **Raise, do not apply** a design choice discovered while implementing.
- Never delete old text; mark it superseded with a back-pointer.
- Small commits, each with the gate green, each pushed.
- This stage is Python; no heavy builds on this machine.
- After three failed attempts at the same problem, stop and report the attempts.
