# Status

> Written by hand. Only strategic judgements and open rulings. Structure is enforced by the gate, not restated here.

## Phase

Design (the base is at v0.10; no code yet)

## Working on

Compressing "agent-native OS" from first principles into an executable base. Second round of rulings is on record: the substrate goes L1+L2 (L3 recorded as technical debt), `counts` is human-written with agent proposals, the probe runs in two steps, the licence is settled.

## Blocked

Nothing hard. Every open item is deliberately deferred, not stuck.

## Next

0. *(optional)* A one-page core: compress FOUNDATION (≈500 lines) into the screen the map is supposed to fit on. If it will not compress, the core is not clear yet.

1. **Done**: probe step one (install a package) — see `probe/README.md`. Four rulings it asks for are listed below.
2. Probe step two: hit the `send` red line with a real approval flow.

The success test: **if one real event cannot be written in four predicates within one screen, the vocabulary is wrong.**

## Open rulings

- **Reference implementation list** (D-021): deferred; review after both probes.
- **Map budget** (D-022): deferred; review once a first map exists.
- **Claim scope** (probe finding 1): every claim needs a `world` field, not a value key.
- **Projection signature** (finding 2): the world must be a required argument, enforced by the API.
- **Batch `did`** (finding 6): one file one claim will not scale; a manifest/aggregate form is needed.
- **First signature** (finding 5): how the root of trust is grounded — the measured boot chain's job.
- **v0 install / rollback**: how it lands on the existing four partitions — not designed yet.
- **Genuinely simultaneous conflicts**: two contradictory instructions from the human at the same instant — not designed yet.

## Health

- Design authority: `design/FOUNDATION.md` v0.10
- Decision log: `docs/DECISIONS.md` D-001 … D-028 (3 supersession chains)
- Implementation: Rust core, Python probe; ABI carries no language types (D-027)
- Agents: external, one ABI + N thin adapters, MCP is an adapter only (D-028)
- Gate: `tools/check.sh` (structure)
- Repository: `/lab`, `main`, public at github.com/YusenZhang0601/tonyos
- Licence: code GPL-3.0-only / docs CC BY-4.0 / name reserved / contributions require a CLA (D-023)
- No code yet, so there is no "test suite" to speak of
