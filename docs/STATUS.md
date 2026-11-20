# Status

> Written by hand. Only strategic judgements and open rulings. Structure is enforced by the gate, not restated here.

## Phase

Design, plus a three-pass probe (base at v0.13; no system yet)

## Working on

Compressing "agent-native OS" from first principles into an executable base. Second round of rulings is on record: the substrate goes L1+L2 (L3 recorded as technical debt), `counts` is human-written with agent proposals, the probe runs in two steps, the licence is settled.

## Blocked

Nothing hard. Every open item is deliberately deferred, not stuck.

## Next

0. *(done)* The one-page core: `design/CORE.md`, 88 lines.
1. **Done**: probe passes one to three — install, approval flow, two worlds (D-030…D-035).
2. **Done**: throughput probe (E1). fsync, not the shared log, was the ceiling: 38/s per-commit on this HDD, 3,586/s with group commit; sharding bought nothing. D-037's group-commit prediction held, its "shared log is the suspect" consequence did not.
3. **Done**: storage crash probe (E2). A torn tail made the whole store unreadable; a flipped byte was accepted with the original id; `append()` never fsynced. Contract recorded as D-039.
4. **Done**: the framed log is in `Ledger` — fsync on append, checksum on recovery, tail cut and counted. `probe/demo.py` still passes 8/8.
5. **Done**: concurrency (E3). Without CAS, both writers "succeeded" and the world grew two heads with duplicate positions. With CAS under a per-world lock: exactly one winner, the loser gets a conflict and forks (D-040).
6. **Next**: the cost of correctness — one `fsync` per commit instead of two, then group commit. After that, the Screen.

The success test: **if one real event cannot be written in four predicates within one screen, the vocabulary is wrong.**

## Open rulings

- **Reference implementation list** (D-021): deferred; review after the throughput probe.
- **Map budget** (D-022): deferred; review once a first map exists.
- **`tick`**: is a root claim with an unchanged tree enough to advance time, or does it need its own verb?
- **`*` scope**: should global be limited to `may`/`counts`, or do sensor facts about the machine also belong above worlds?
- **Trust root** (D-033): only the assumption claim is implemented; measurement is deferred with triggers.
- **v0 install / rollback**: how it lands on the existing four partitions — not designed yet.
- **Genuinely simultaneous conflicts**: two contradictory instructions from the human at the same instant — not designed yet.
- **Performance floors** (D-037): each tier needs a floor or ceiling, or "third" means "unbounded". The baseline now exists (38/s per-commit, 3,586/s grouped); the numbers still need the owner's sign-off.
- **Repeated identical `did`s** (D-038): they collapse into one event. Is "it looked twice" part of the audit trail, and does that require a per-author counter?
- **Mid-file corruption** (D-039): recovery stops at the first bad frame. Whether a scrub may resync past it and recover later frames is not decided.
- **Group commit and durability** (D-037/D-039): one fsync covers many claims, so "committed" becomes a batch boundary. How that is reported to a waiting writer is not yet specified.
- **Where a conflict is recorded** (D-040): `did` cannot be global, and the world it failed to advance is the one it must not write to.
- **Failed attempts across a crash** (D-040): surviving one costs a second fsync. Worth it, or is "the world did not move" enough?

## Health

- Design authority: `design/FOUNDATION.md` v0.15
- Decision log: `docs/DECISIONS.md` D-001 … D-040 (3 supersession chains)
- Implementation: Rust core, Python probe; ABI carries no language types (D-027)
- Agents: external, one ABI + N thin adapters, MCP is an adapter only (D-028)
- Gate: `tools/check.sh` (structure)
- Repository: `/lab`, `main`, public at github.com/YusenZhang0601/tonyos
- Licence: code GPL-3.0-only / docs CC BY-4.0 / name reserved / contributions require a CLA (D-023)
- No system yet; the probe is the only executable thing (`python3 probe/demo.py`)
