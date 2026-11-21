# Status

> Written by hand. Only strategic judgements and open rulings. Structure is enforced by the gate, not restated here.

## Phase

Design, plus a nine-pass probe (base at v0.16; no system yet)

## Working on

**Stage 3 open: [`docs/GOAL-screen.md`](GOAL-screen.md) — the Screen.** Four passes: the
mapping before the pixels (pass A, analysis only) / the render / the cost / the handoff
test. Pass A is the real test of the vocabulary: every panel line must name the active
claim that supplies it, and a line with no claim behind it is recorded as a gap, never
filled with prose.

**Handoff:** the goal file is the whole brief; a fresh agent needs it plus the three
entry files. Stage 2 is closed and green, the tree is clean, and pass A starts from it.

Compressing "agent-native OS" from first principles into an executable base. Second round of rulings is on record: the substrate goes L1+L2 (L3 recorded as technical debt), `counts` is human-written with agent proposals, the probe has nine passes, the licence is settled.

## Blocked

Nothing hard. Every open item is deliberately deferred, not stuck.

## Next

0. *(done)* The one-page core: `design/CORE.md`, 88 lines.
1. **Done**: probe passes one to three — install, approval flow, two worlds (D-030…D-035).
2. **Done**: throughput probe (E1). fsync, not the shared log, was the ceiling: 38/s per-commit on this HDD, 3,586/s with group commit; sharding bought nothing. D-037's group-commit prediction held, its "shared log is the suspect" consequence did not.
3. **Done**: storage crash probe (E2). A torn tail made the whole store unreadable; a flipped byte was accepted with the original id; `append()` never fsynced. Contract recorded as D-039.
4. **Done**: the framed log is in `Ledger` — fsync on append, checksum on recovery, tail cut and counted. `probe/demo.py` still passes 8/8.
5. **Done**: concurrency (E3). Without CAS, both writers "succeeded" and the world grew two heads with duplicate positions. With CAS under a per-world lock: exactly one winner, the loser gets a conflict and forks (D-040).
6. **Done**: the write path is closed (pass 7). `append` refuses a root; CAS is in the store; one fsync per commit is 2.2x; group commit cuts `fsync/commit` to 0.16 at eight writers. The next ceiling is the commit path on two cores, not the disk.

7. **Done**: the head is an index (pass 8). A commit reads only the new tail and finds
   the head in a dict. 500 mixed operations, 0 mismatches against brute force; a fresh
   Ledger rebuilds the same heads. Group commit at 32 writers: 255 → 590-617/s.

**Stage 2 is closed: the head is O(1).** The measurement refuted half its premise — the
locked path was re-reading the whole log (24 times per commit at 32 writers), while the
head scan was only 0.3 ms. Both are fixed; the index's real value was cutting lock hold
time, which grew the batch from 9 to 21. `probe/README.md` pass 8 has the evidence.

**Stage 3: the Screen** — taken, see the goal file. The other two candidates stay on
the list, unopened:

1. **The Screen.** ← open; four passes in `docs/GOAL-screen.md`.
2. **The adapter boundary.** One real host through one thin adapter, against a 10-line
   ABI sketch. It is the first test of "any agent lives here" (D-028).
3. **The view index and the log owner.** `visible()` still scans every row, the whole
   log is in memory, and cross-process commits cannot share an fsync. This is the
   scale stage.

The success test: **if one real event cannot be written in four predicates within one screen, the vocabulary is wrong.**

## Open rulings

- **Reference implementation list** (D-021): deferred; review before the first non-probe implementation.
- **Map budget** (D-022): deferred; review once a first map exists.
- **`tick`**: is a root claim with an unchanged tree enough to advance time, or does it need its own verb?
- **`*` scope**: should global be limited to `may`/`counts`, or do sensor facts about the machine also belong above worlds?
- **Trust root** (D-033): only the assumption claim is implemented; measurement is deferred with triggers.
- **v0 install / rollback**: how it lands on the existing four partitions — not designed yet.
- **Genuinely simultaneous conflicts**: two contradictory instructions from the human at the same instant — not designed yet.
- **Performance floors** (D-037): each tier needs a floor or ceiling, or "third" means "unbounded". The baseline now exists (39/s per-commit; ~600/s grouped at 32 writers); the numbers still need the owner's sign-off.
- **Repeated identical `did`s** (D-038): they collapse into one event. Is "it looked twice" part of the audit trail, and does that require a per-author counter?
- **Mid-file corruption** (D-039): recovery stops at the first bad frame. Whether a scrub may resync past it and recover later frames is not decided.
- **Group commit and durability** (D-037/D-039): a writer now waits for the fsync that
  covers its claim. Whether the batch boundary is itself a claim — for audit — is not
  decided.
- **Where a conflict is recorded** (D-040): `did` cannot be global, and the world it failed to advance is the one it must not write to.
- **Failed attempts across a crash** (D-040): surviving one costs a second fsync. Worth it, or is "the world did not move" enough?
- **Cross-process group commit** (D-037/D-040): two processes cannot share an `fsync`
  boundary without a daemon owning the log. Accept per-commit `fsync` outside one
  process, or design the daemon?
- **The whole log in memory.** The probe holds every row; the core cannot. Paging or
  indexing on disk is undesigned.
- **`visible()` is O(n).** The Screen will call it; whether it needs its own index is
  open.

## Health

- Design authority: `design/FOUNDATION.md` v0.16
- Decision log: `docs/DECISIONS.md` D-001 … D-041 (3 supersession chains)
- Implementation: Rust core, Python probe; ABI carries no language types (D-027)
- Agents: external, one ABI + N thin adapters, MCP is an adapter only (D-028)
- Gate: `tools/check.sh` (structure)
- Repository: `/lab`, `main`, public at github.com/YusenZhang0601/tonyos
- Licence: code GPL-3.0-only / docs CC BY-4.0 / name reserved / contributions require a CLA (D-023)
- No system yet; the probe is the only executable thing (`python3 probe/demo.py`)
- Retraction: `did` is an event and cannot be retracted; `is` / `may` / `counts` are
  beliefs and reach a fixpoint, cached per ledger state (D-041)
- Probe: nine passes, seven executable experiments (`demo`, `crash`, `concurrent`,
  `group`, `cost`, `index`, `retract`)
