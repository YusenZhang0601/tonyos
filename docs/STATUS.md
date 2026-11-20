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
2. **Next**: a throughput probe. The question is no longer only "who wins a conflict" but **does commit throughput scale with the number of independent writers**, with one global log versus one log per world (D-037).

The success test: **if one real event cannot be written in four predicates within one screen, the vocabulary is wrong.**

## Open rulings

- **Reference implementation list** (D-021): deferred; review after the throughput probe.
- **Map budget** (D-022): deferred; review once a first map exists.
- **`tick`**: is a root claim with an unchanged tree enough to advance time, or does it need its own verb?
- **`*` scope**: should global be limited to `may`/`counts`, or do sensor facts about the machine also belong above worlds?
- **Trust root** (D-033): only the assumption claim is implemented; measurement is deferred with triggers.
- **v0 install / rollback**: how it lands on the existing four partitions — not designed yet.
- **Genuinely simultaneous conflicts**: two contradictory instructions from the human at the same instant — not designed yet.
- **Performance floors** (D-037): each tier needs a floor or ceiling, or "third" means "unbounded". Numbers wait for a baseline measurement; the rule that they must exist does not.

## Health

- Design authority: `design/FOUNDATION.md` v0.14
- Decision log: `docs/DECISIONS.md` D-001 … D-037 (3 supersession chains)
- Implementation: Rust core, Python probe; ABI carries no language types (D-027)
- Agents: external, one ABI + N thin adapters, MCP is an adapter only (D-028)
- Gate: `tools/check.sh` (structure)
- Repository: `/lab`, `main`, public at github.com/YusenZhang0601/tonyos
- Licence: code GPL-3.0-only / docs CC BY-4.0 / name reserved / contributions require a CLA (D-023)
- No system yet; the probe is the only executable thing (`python3 probe/demo.py`)
