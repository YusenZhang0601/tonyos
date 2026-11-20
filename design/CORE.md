# The core

> One page. If it does not fit, the core is not clear.
> The full derivation, the tradeoffs and every overturned conclusion live in [`FOUNDATION.md`](FOUNDATION.md).

## 1. Whose machine is this

The agent is the owner. The human is the constitution.
The human does not operate. The human draws boundaries, and boundaries are written to disk.

## 2. The vocabulary is closed

One record type, four predicates:

| `is` | what the world is |
| `did` | what happened |
| `may` | what the human ruled |
| `counts` | what counts as what |

Three verbs for `did`: `read` / `write` / `send`.
Three modes for `may`: `allow` / `require` / `deny`.
Three forms for `counts`: identity / satisfaction / representation.

Nothing else. A requirement that will not translate belongs outside the core.

## 3. Describe, compute, ask

- **describe** → one of the four predicates
- **compute** → a projection (a reference implementation)
- **ask** → the map, which is the catalogue of projections

A projection answers **for a viewpoint** — a root claim that pins the branch, the moment and the tree at once. It never reads the ledger directly; the store hands it one slice, so it cannot consult another world by accident.

A derivation is not explained, it is **reproduced**: `because = [inputs…, hash of the projection's code]`.
A deterministic projection is a derivation. A non-deterministic one — an LLM — is a claim, and must be held to account.

## 4. Boundaries

**Allowed by default.** The human draws rings. Inside a ring requires approval.
The red line is `send`: the only action that leaves your ownership, therefore the only irreversible one.
Enforcement lives in the hand — the executor — never in the agent's good intentions.

**One signature, one act.** Using an approval spends it; the act and the spending are the same claim. Expiry is a position in the ledger, never a wall-clock time.

## 5. Nothing is ever modified

Only a new version plus a pointer swap. So there are no locks, no torn writes, no backups, no restores, no merge conflicts.
Two primitives: **fork** (free) and **prune** (automatic, by reachability).
Everything lands in a **world**; only rules and definitions may be global. There is no global "now", only an observer's projection of one total order.
A claim's name is its content, never its position — so two nodes can agree without coordinating.
"Back to yesterday" is not a restore, it is an as-of query.

**One reference per world, never one for the machine.** Worlds share no state, so they share no pointer. A single global reference is a cache-line hotspot — the lesson RCU taught Linux.

## 6. Memory

Three things, never confused: the **ledger** (may be large) / a **view** (hard budget) / a **digest** (as small as possible).
The value of process equals undecidedness.
**Nothing enters the context on its own.** The map is the single exception, and it must fit one screen.

## 7. Who may change what

| Invariants | nobody |
| No-go zones and definitions | the human only — the agent may propose, a signature makes it real |
| Everything else | any reference implementation, replaceable at will |

## 8. The agent is not ours

One ABI, N thin adapters. **The seam is the adapter boundary.** MCP is an adapter, not the ABI.
Continuity lives in the ledger, so any agent can take over — including one that has never seen this machine.

## 9. What we are allowed to borrow

From a kernel: **processes, memory, devices. Nothing else.**
Target: the only foreign code in the system is `vmlinuz` and hardware firmware.

## 10. What this is not

Not a programming language. Not a sandbox. Not a dashboard. Not an agent framework.

## 11. What comes first

**Principles, then performance, then elegance.** Elegance includes maintainability, so "easier to maintain later" is not a fourth argument.

Inside performance: **concurrency and throughput, then latency, then footprint.** Boot time is latency.

A tradeoff must say which one it gave up: elegance needs no reason / performance needs a number / a principle needs to be recorded as an exception.

## 12. The test

**If one real event cannot be written in four predicates within one screen, the vocabulary is wrong.**
