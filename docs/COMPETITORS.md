# Market and competitors

> A **projection of observations**, not authority. Design authority stays in `FOUNDATION.md`.
> Never auto-loaded. Read it when the question is "is anyone else doing this".
> Snapshot method: GitHub API + arXiv + vendor release notes, by hand.
> **Last sweep: 2026-11-20 · Next sweep: 2027-02-20 (quarterly, or on a trigger)**

## How to keep this alive

A sweep is four steps and must leave a row in the sweep log. Do not rewrite old rows:
mark them superseded, the same way a claim is retracted.

1. Run `tools/market.sh --out <file>` and `diff` it against the previous sweep. Exit 0
   means complete; any gap is printed as `# ERROR`, and a gap is left open.
2. For every watchlist item, read the delta in stars, `pushed`, license and archived.
3. Record **deltas only**. A star count that did not move is not news.
4. If a trigger fired, update the verdict and say **what refuted the old one**.

Saved queries (copy verbatim, or let the script run them):

```
topic:agent-os
"agent-native operating system"
"AI operating system" agents
"agent OS" kernel
append-only ledger agent memory
"agent is the owner"
nixos agent
agent sandbox policy
```

Sources beyond GitHub: arXiv (`agent operating system`, `agentic OS`, `trust-native`),
vendor release notes (Microsoft, Anthropic, Apple), and the projects' own `VISION.md`
or thesis documents — not their READMEs alone.

## The verdict (one screen)

**Nobody does the combination. Every constituent part is already taken.**

The two sentences still unclaimed on GitHub (verified 2026-11-20):

1. **The agent is the owner of the machine; the human writes only the constitution.**
2. **The agent may not define its own success** (`counts` is human-authored).

Everything else — a log, projections, capability enforcement, approval gates, sandboxes,
an agent-first shell — exists today, in production or in papers. We must cite them,
not rediscover them.

What is genuinely ours is the **fusion**: one closed vocabulary that describes the whole
machine, a ledger that is the machine's state, and a distribution small enough that the
only foreign code is `vmlinuz`.

Two things this sweep says we must **not** sell as differentiation:

- "safer agents" — commoditised (MXC is free, OS-level, GA, cross-platform)
- "memory / ledger for agents" — a crowded category (Letta, AgentBook, stateledger, XTDB)

## Scale of the field (2026-11-20)

| Query | Repos |
|---|---|
| `topic:agent-os` | 270 |
| `"agent-native operating system"` | 28 |
| `"AI operating system" agents` | 659 |
| `"agent OS" kernel` | 64 |
| `append-only ledger agent memory` | 33 |
| **`"agent is the owner"`** | **1** (this project) |

Star counts are noisy: the field is full of one-person, vision-first repositories
created in 2026. Attention is high; retention is not demonstrated.

## The five camps

| Camp | Representatives (★, 2026-11-20) | What "OS" means to them |
|---|---|---|
| **A. Control plane** | CompanyOS 20.8k · holaOS 11.4k · ouroboros 6.4k · Compozy 2.9k · BoringOS 42 | a workbench that steers many agent sessions, above Linux |
| **B. Runtime kernel** | AIOS 6.6k · AgentKernel (paper) · ARK 43 · CivicOS · ProbOS | LLM as CPU, context as RAM — scheduling and memory |
| **C. Machine / distro** | Herald-OS 661 · stereOS 506 · Veda 113 · agentOS 61 · aOS · agent-os (NixOS) · Agentix · Avibe 645 | Linux plus an agent surface, or a rewrite from the kernel up |
| **D. Ledger / memory** | Letta 25.5k · Decima 1 · AgentBook 46 · stateledger 1 · veritas 0 | agent state, beliefs, session continuity |
| **E. Vendor substrate** | microsoft/mxc 3.2k · Claude Cowork · E2B | OS-level isolation and approval, cross-platform |

Camps A and B use "OS" metaphorically: they are a control plane **above** Linux.
Only Veda (own UEFI loader + microkernel) and agentOS (seL4) actually build a machine.
Camp D only does state, and never touches the machine.

**Nobody welds the ledger to the machine.** That is the position.

## The closest six

| Project | What it has | What it does not have |
|---|---|---|
| **Judge-M/Decima** (1★, Python) | "the whole OS is four verbs over one append-only log; state is a fold; authority is a held object"; capabilities; approval inbox; provenance; 1262 tests | four verbs are **actions** (ASSERT/RETRACT/INVOKE/ATTEST), not **descriptions**; no `may`/`counts` split; no `send` red line; explicitly refuses to write a kernel ("Linux is the adopted kernel"); **the human is the operator and the agent is subordinate**; "deliberately enormous" |
| **AgentKernel** (arXiv 2609.29647) | "trust-native agent OS": Identity / Perception / Cognition / Execution, mandatory non-bypassable services; prompt injection, memory poisoning, tool misuse | a paper, not a distribution; no ledger-as-state; no ownership inversion; no `counts` — security is the goal, not accountability |
| **microsoft/mxc** (3.2k★, MIT, GA 2026-10) | policy-driven execution containers (files/network/UI), Rust/.NET/Node SDKs, "OS-level agent containment" | the hand only: no ownership chain, no "what counts as done", no record of what the agent was permitted to see |
| **Herald-OS** (661★) | agent as the interface, permission system, approval cards, `herald-os rollback` | Fedora Silverblue/bootc + Electron underneath; no ledger, no policy compiler, no ABI |
| **stereOS** (506★) | NixOS + `agent` user + restricted PATH + `agentd`/`stereosd` | governance by Unix user instead of a permission model; Nix modules instead of claims |
| **Veda** (113★, GPL-3.0) | Rust from UEFI to apps, voice agent in the system, "asks before anything that is hard to undo" | one sentence, not a red line; no ledger; no `may`/`counts` |

Small and sharp, worth watching:

- **dillondevoe/agent-os** — NixOS, no desktop, boot into a local model, a "sealed" variant that DROPs outbound by default.
- **Agentix** — NixOS `plan → sandbox → propose → verify → human apply/rebuild`.
- **stateledger / veritas** — evidence kept apart from conclusions, retraction with a reason, no in-place edits. This is our claim model, stopped at the memory layer.

## The six claims, audited

| Claim | Status | Nearest evidence |
|---|---|---|
| agent owns, human constitutes | **unclaimed** | every project defaults to human-as-user/operator/captain; exact-phrase search hits only this repo |
| four predicates, closed | **partial** | Decima's four verbs; stateledger's evidence/conclusion split; TMS justifications — but nobody argues *why four*, and nobody separates `may` from `counts` |
| everything is a projection | **partial** | Datomic/XTDB/Datahike as-of; Nix derivations; Urbit's event log — each only inside its own domain |
| minimal distro, only `vmlinuz` foreign | **unclaimed** | seL4 agentOS still hosts Linux; MirageOS is a unikernel, not an agent OS; nobody uses minimality as a gate |
| immutability as a coordinate | **partial** | Nix generations, XTDB time travel, Urbit — never applied to the whole machine's claim space |
| one ABI, N adapters, MCP is only an adapter | **unclaimed and against the current** | MCP became the de facto standard (donated to the Linux Foundation); critics argue CLI is better; nobody does M×N at the OS layer |

**What is actually open: two full claims and a half** — ownership inversion, human-only
`counts`, and minimality as a checkable property. The other four are prior art; cite them.

## The three shots we will take

1. **"Isn't this NixOS + an agent + SQLite?"**
   A Nix generation versions *system configuration*; it is not a ledger of *what happened*.
   It cannot express `may` or `counts`, and it cannot record which rules the agent was
   allowed to see at the moment it acted.
2. **"Decima already did four verbs over one log."**
   Their verbs are speech acts; ours are ontological. They have no human-only `counts`,
   so their agent can certify its own success. They chose Linux as the kernel; we did not.
3. **"MXC already owns the enforcement point, and it is free."**
   MXC is a hand without a memory. Containment prevents; it does not account. It cannot
   answer "was this counted as done, and by whom".

## Watchlist

| ID | Watch | Why | Trigger to act |
|---|---|---|---|
| M-01 | Decima | nearest narrative; will compete for the same search terms | >500★, an OS image, or a release claiming a distribution |
| M-02 | AgentKernel | owns "trust-native agent OS" academically | code release, or anyone citing it as prior art for our position |
| M-03 | microsoft/mxc | OS-level containment, commoditised | it gains an audit log, an agent identity standard, or a ledger |
| M-04 | Claude Cowork / Apple / Google agent surfaces | the default consumer surface | a local-first "agent owns the machine" framing, or an open ABI |
| M-05 | NixOS-adjacent (Agentix, dillondevoe, stereOS) | the cheap answer to our pitch | any of them adds a claim ledger or human signature |
| M-06 | AIOS / AOS / AaOS papers | definitional capture of the term | a paper defines ownership, constitution, or a closed vocabulary |
| M-07 | seL4 agentOS / Veda | the minimal-substrate route | an agent-native distribution on a verified microkernel |
| M-08 | stateledger / veritas / AgentBook | the claim layer, already built | one generalises from memory to system state |
| M-09 | MCP / Linux Foundation | the ABI question | MCP gains permission or audit semantics strong enough to replace an ABI |
| M-10 | vendor-owned agent identities | "the agent has its own account/device" | a vendor ships an agent-owned device or OS account model |

## Open items this sweep raised

Not rulings. They need the owner.

- **O-1 Naming.** GitHub has 22 repos matching `tonyos`, including a hobby kernel named
  `TonyOS`. Search and trademark presence are weak; the cost of renaming rises with time.
- **O-2 Positioning page.** One page, three differences, explicit citations of Decima,
  AgentKernel, MXC. Without it we are the 271st `agent-os`.
- **O-3 L2 timing.** Do not start PID 1 before the L1 + ledger demo exists, or the first
  objection ("why not NixOS") cannot be answered.

## What would refute this verdict

- A project that combines **ownership inversion + a closed vocabulary + a machine-level
  distribution**. None found; GitHub search is lexical, so a non-English or unindexed
  project could exist.
- Evidence that undernaming is fatal: if the 270 `agent-os` repos show no retention at all,
  the category may be noise rather than a market, and "being the 271st" is not a risk.
- Evidence that the ledger is unnecessary: if MXC-style containment plus vendor identity
  turns out to be sufficient for accountability, our central bet is wrong.

## Sweep log (append-only)

| Date | What changed | Verdict impact |
|---|---|---|
| 2026-11-20 | First sweep. 270 `agent-os` repos; Decima, AgentKernel, MXC found as nearest neighbours; exact phrase "agent is the owner" returns only this repo. | Baseline established. |
| 2026-11-20 | Sweep automated: `tools/market.sh` (8 queries + 13 repos, exit 0). Baseline counts re-taken from one clean run; quoted-phrase count corrected from 54 to 28. | Protocol is executable; numbers now single-source. |
