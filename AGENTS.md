# TonyOS — entry protocol

> This machine (`tonyos-dev`) is the testbed. The project goal: **an agent-native minimal distribution**.
> This file is a map, not a manual. Read it first every session; it holds only structure, boundaries and pointers.

## Current state (≤12 lines)

- Phase: **design**, with a nine-pass probe (Python). No system yet.
- Settled: the thesis (the agent is the owner / the human is the constitution), the base (four predicates), no-go zones, the axiom of reversibility, memory and context rules, events vs beliefs, the license
- Open: reference implementation list, map budget, `tick`, `*` for sensor facts, performance floors
- Not started: the Screen, v0 install/rollback, the real storage engine and boot
- Next: awaiting the owner's choice of the next stage (three candidates in `docs/STATUS.md`)
- Side track: market watch, quarterly — `docs/COMPETITORS.md`, next sweep 2027-02-20

## Read these three

1. This file (structure / boundaries / routing)
2. `design/CORE.md` — **the whole system on one page**
3. `docs/STATUS.md` — where we are, what is blocked, what needs a ruling

Reading only these three should be enough to start work. If it isn't, the writing is too vague.
`design/FOUNDATION.md` is the manual: read it when you need the *why*, not to get started.

## Layout

| Path | What it is | Doc type |
|---|---|---|
| `AGENTS.md` | Entry protocol (this file) | Reference |
| `design/CORE.md` | The whole system on one page | Explanation |
| `design/FOUNDATION.md` | Design authority: the base and all derivations | Explanation |
| `docs/STATUS.md` | Current state and open rulings | Reference |
| `docs/DECISIONS.md` | Decision log (append-only, with supersession chains) | Explanation |
| `docs/JOURNAL.md` | Work log (one line per day) | Reference |
| `docs/COMPETITORS.md` | Market and competitor snapshot (maintained side track) | Reference |
| `docs/INDEX.tsv` | Repository index (generated, do not edit) | Reference |
| `README.txt` | Testbed partitions and boot method (machine facts) | Reference |
| `README.md` | Human-facing introduction | Tutorial |
| `LICENSING.md` | How code, docs and name are licensed | Reference |
| `TRADEMARK.md` | Rules for the name and official builds | Reference |
| `CLA.md` | Contributor License Agreement | Reference |
| `probe/` | The probe: a runnable ledger, and what it broke (`probe/README.md`) | How-to |
| `tools/index.sh` | Generate the index | How-to |
| `tools/check.sh` | The gate | How-to |
| `tools/market.sh` | Market sweep: read-only GitHub snapshot, diffable | How-to |

## How to run

The probe is runnable; the system is not. The gate:

```bash
tools/index.sh     # regenerate docs/INDEX.tsv
tools/check.sh     # gate: broken pointers / stale index / status fields / decision fields
```

Exit code 0 means the structure is intact. If it is red, fix the structure before writing content.

## How to verify

- The gate is green.
- **Handoff check**: reading only the three files above, answer four questions — what are we doing / what is blocking / what is the next concrete step / which file do I read first to do it.

## Do not touch

- `.machine/`: local network environment (mihomo installer, screen-off script, proxy config). **Not part of this project**, contains credentials, already gitignored. Do not modify, index, or load into context.
- `lost+found/`: owned by the filesystem.
- `/dev/sda3` (SLOT-A), `/dev/sda4` (SLOT-B): experiment slots, **left unmounted on purpose**. Record a decision in `docs/DECISIONS.md` before mounting or formatting either one.
- Do not test anything by editing GRUB / efibootmgr, unless using the one-shot bootnext + hard-reboot fallback.
- Do not run local large models on this machine (2 cores / 3.7 GB).

## Where to ask

| Question | Where |
|---|---|
| Why is it designed this way / why four predicates | `design/FOUNDATION.md` |
| When was a decision made, what replaced it | `docs/DECISIONS.md` |
| What should I do now | `docs/STATUS.md` |
| How is this machine partitioned, how does it boot | `README.txt` |
| Where is a file | `docs/INDEX.tsv` |
| Is anyone else doing this / what is the market | `docs/COMPETITORS.md` |

## Hard rules (to break one, first write a DECISION)

1. **Closed vocabulary**: any new requirement must translate into one of `is` / `did` / `may` / `counts`. If it cannot, it belongs in a reference implementation, not in the core.
2. **No new layers**: functionality may only be added as an observer, a claim, or a projection.
3. **Design before code**: anything not settled in FOUNDATION must not be quietly settled in code.
4. **Never delete old text**: mark it superseded and leave a back-pointer.
5. **Every judgement must state what would refute it.** If you cannot, it is a slogan — rejected.
6. **Default: don't load**: except for the map, nothing may enter the context on its own.
7. **Done means evidence.** A completion claim without evidence is a *proposal*, not a result.
   - "it works" → name the command and paste its output.
   - "it's the same" → say what was compared, and how.
   - "I fixed it" → say what was broken and what now passes.
   - Anything not run must be labelled **not verified**. A gap is left open; it is never filled with a guess.
   - A design choice discovered while implementing is **raised**, not applied.

## License (one line)

Code GPL-3.0-only, docs CC BY-4.0, name reserved. Commercial use is free; modifications must be published; using the ideas requires credit.
Details in `LICENSING.md`; contributors read `CLA.md` first.


## Borrowed machines (local only)

Heavy builds may be delegated to **borrowed** machines, because this testbed is
2 cores / 3.7 GB. Their names, addresses and SSH configuration live in a
gitignored local directory and **must never be indexed, quoted or published**.

The rules, because they are borrowed and run other people's work:

1. Confirm the environment first (distribution, toolchain, source path).
2. Check the load. If the machine is busy, wait or choose another.
3. Cap the build (`-j` below the core count) and time-box it.
4. Do not install or upgrade toolchains without asking.
5. Leave nothing running, and clean scratch output afterwards.

A build on a borrowed machine is a build, not a verification: boot and block
device tests happen on this machine.
