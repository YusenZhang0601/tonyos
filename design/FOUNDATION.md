# The Base

> **The single source of design authority.** If an implementation disagrees with this document, this document wins.
> To change it, first record a ruling in `docs/DECISIONS.md`.
> Version: v0.10 · 2026-11-20

### Terminology

**Rule**: a term earns its place by fitting. If no existing term fits, we coin one — and then we owe the reader three things: our definition, the nearest existing concept, and **where ours differs**.

| Term | Our definition | Nearest existing | Where ours differs |
|---|---|---|---|
| **claim** | a statement by a named party (human / agent / sensor); it enters the world only with a justification chain; withdrawal is a retraction, never a deletion | assertion (truth maintenance systems); datom (Datomic); statement (RDF) | TMS maintains *truth* for the system; a claim is *authored* — the author is part of the record — and truth is never maintained, only filtered by projections. Claims are immutable: superseded, never revised |
| **justification** | the `because` field: the claims this one rests on | justification (TMS); provenance | Ours must bottom out at exactly two roots — a human signature or a hardware measurement. TMS requires no such thing |
| **retraction** | the `replaces` field: withdrawal without deletion | retraction (TMS) | Same idea; the original claim is never removed, so the history of opinion survives |
| **counts-as** | stipulating that X counts as Y; only the human may write it; exactly three forms — identity / satisfaction / representation | counts-as (Searle); constitutive rule | Searle describes social reality; this is an OS primitive with a closed form set and a hard authorship restriction. The restriction is the point: an agent must never define what counts as its own success |
| **no-go zone** | a ring the human draws around something; acting inside requires approval; outside is allowed by default | default-allow denylist + decision / enforcement points (XACML); "protected resource" | Standard access control governs *subjects and permissions*; this governs *regions of the world and approvals*. Default-allow is normally advised against — we accept it because reversibility and the audit trail are the backstop, not permissions |
| **red line** | any `did` whose verb is `send`; the only irreversibility the system recognises | non-compensatable action (saga); irreversible effect | A saga asks "can this be compensated inside the transaction?"; ours asks "did this leave our ownership?" The system can undo only what it owns, so the boundary of ownership *is* the boundary of undo |
| **audit trail** | the `did` chain | audit trail; event log | Ours also records what the agent was **permitted to see** at that moment, not only what it did. Accountability needs the field of view, not just the action |
| **the map** | the system's self-portrait: loaded automatically, regenerated on every read, must fit one screen, lists categories and entry points only | catalog; manifest; service registry | Not a cache and not an inventory: a stale map is forbidden, and the map's size is the system's complexity ceiling |
| **the Screen** | the human-facing surface; shows the agent, not the machine | dashboard; HUD | Deliberately not a dashboard. A dashboard reports on the system; the Screen reports on *it* |
| **reference implementation** | a first-party implementation that is always replaceable | reference implementation | Same term, same meaning |
| **seam** | a boundary across which a part may be replaced | seam (Feathers) | Ours is also a versioned contract, not merely a substitution point in code |
| **need-to-know** | an observer sees only what its task requires | need-to-know; compartmentalisation | Enforced structurally by namespace projection, not by evaluating a policy at request time |
| **policy compiler** | turns the full rule set into the fragment one task may see; the fragment becomes part of the authorization | policy compiler (policy-as-code) | Ours compiles *per task* and every compilation is itself recorded, so "what it was allowed to know" is auditable |
| **technical debt** | work deferred by choice, to be paid later | technical debt | Same term, same meaning |

---

## 0. Identity

**One sentence**

> The system's owner is the agent, not the human; the human is the constitution, not the operator.

**The core question**

> How does an agent come to live on a machine, do work, and remain accountable the whole time?

This is not "an AI that helps you work" — it is "**you stop working**". The human does not operate, but sets boundaries; boundaries are written to disk, not spoken in chat.

**What the artefact is**

- What it really produces: **a set of ideas** (a set of constitutive rules).
- What it ships as: **a complete minimal distribution** — others may change and replace anything; as long as the idea holds, it is still the same thing.
- First-party work must be exemplary; third-party work need not be, but it must be able to plug in.

**Non-goals**

- Not a "desktop distro with an agent preinstalled".
- Not an agent framework (binds neither model nor host).
- Not a chat box used as a desktop.
- Not a system monitoring dashboard.

---

## 1. The base: four predicates

**Criterion**: a predicate earns its place only if it **cannot be derived from the others**. Store only what cannot be derived.

There is exactly one record type in the system:

```
claim
  id        content hash (the name is the content)
  subject   about whom (world / agent:xx / file:/etc/x / claim:xx)
  predicate one of four (closed)
  value     the value (large things store only a hash)
  by        who asserts it (human / agent / sensor)
  at        a total sequence number + wall clock
  because   [claim id...]   evidence is itself claims; recursion bottoms out
  replaces  [claim id...]   retraction, not deletion
```

| Predicate | Answers | How it fails |
|---|---|---|
| `is` | what the world is | wrong |
| `did` | what happened | missed |
| `may` | what rules the human set | violated |
| `counts` | what counts as what | void (withdrawn / no longer accepted) |

### 1.1 Three closed sub-vocabularies

**`did` has exactly three verbs**

| Verb | Meaning |
|---|---|
| `read` | look; changes nothing |
| `write` | change the local world |
| `send` | change the world outside the local one |

`send` is listed separately because **it is the only action that crosses the boundary, and therefore the only red line**. Irreversible means `send`; `send` means irreversible. exec, move, allocate are all combinations of read and write.

**`may` has exactly three modes**

`allow` / `require` / `deny`

"Needs approval" is `require`, not a fourth attitude. No-go zones = `allow` by default, `require` inside the ring, `deny` at the core of it.

**`counts` has exactly three forms**

| Form | Meaning | Example |
|---|---|---|
| **identity** | this counts as the identity of that | after a brain swap, it counts as the same agent |
| **satisfaction** | these checks count as success | 20 cases within tolerance counts as a successful batch |
| **representation** | this signature counts as approval | a human's signature counts as approval |

A fourth form means a design review, not a patch.

### 1.2 Independence (why none can be dropped)

- `is` cannot express `did`: content has no order and no author.
- `did` cannot express `is`: having happened is not still being so.
- Neither can express `may`: **a fact can be wrong; a rule cannot be "wrong", only violated.**
- None of the three can express `counts`: it neither reports, records, nor permits — it **stipulates what counts as that thing**.

Four different failure modes (wrong / missed / violated / void). That is why four cannot be merged into fewer.

### 1.3 Generation (why four are enough)

Every statement about this machine can only be saying: **what the world is / what happened / what rules the human set / what counts as what.** There is no fifth kind.

### 1.4 Where the recursion bottoms out

The evidence chain ends at exactly two roots that cannot be further proven:

1. **A human signature** (`counts`: a signature counts as approval)
2. **A hardware measurement** (the value produced by a measured boot chain)

These two are built-in root definitions and cannot be produced by an agent. Without them the `because` chain would regress forever.

---

## 2. Everything is a projection

| Concept | How it is derived |
|---|---|
| state | the newest non-replaced claims about a subject |
| audit trail | the chain of `did` |
| no-go zones | the `deny` / `require` set of `may` (default `allow`) |
| red line | any `did` whose verb is `send` |
| need-to-know | an observer can only read claims whose subject is in its own namespace |
| hallucination | a claim with no `because` chain is excluded at projection time |
| undo | append a `replaces`; history does not move |
| forgetting | claims unreachable from the current projection are reclaimed automatically |
| identity / continuity | `counts` (identity) |
| approval | `counts` (representation) |
| success / done | `counts` (satisfaction) plus evidence — **computed, not announced by the agent** |
| plan / intent | `is` (the agent's goal) / `did` (declaring is also a fact) |
| dependency / ownership / alias / location | computed by projections, never stored |
| "current" | a `counts` claim naming which reference counts as current |

**The cost**: many things cannot be said. What cannot be said has to live outside the core, as a separate implementation — which is exactly the point of the layering.

---

## 2.5 Derivation: reproducible, not declarative

**This system does not provide a programming language.** The vocabulary describes; it does not compute. That is deliberate, and it has a price, so the price is paid explicitly here.

### The decision procedure

> **To describe the world → it must fit one of the four predicates.**
> **To compute → it goes into a projection, which is a replaceable implementation, not the core.**

### Can projections derive?

Yes. A projection is a function from claims to a view, and it may join, recurse and aggregate. The question was never whether it *can* compute; it is **why anyone should believe the result**.

The answer is not a rule language. It is pinning the code:

```
because = [input claims..., hash of the projection's code]
```

A projection's code is itself a content-addressed blob. So a derived claim is **reproducible**: the same inputs plus the same code give the same result, and any change to the code changes the hash and invalidates the old derivation.

> **A derivation does not need to be explainable; it needs to be reproducible.**

Reproducibility requires exactly three things: a pure function, content-addressed inputs, content-addressed code. That is a **build system**, not a language. Nix and Bazel have done this for decades without a language layer.

### The cut that must not be blurred

| | What it is | How it is trusted |
|---|---|---|
| **deterministic projection** | a derivation | recompute it |
| **non-deterministic projection** (an LLM) | **a claim by an agent**, not a derivation | it needs evidence others can check |

Both are claims. One can be re-run; the other can only be held to account. **Blur this line and accountability collapses**, because you will start treating a model's output as a derivation.

### What is actually given up

Only this: users cannot add rules to extend derivation.

That does not need a language to fix. It needs a catalogue, and the catalogue already exists:

> **The map is the catalogue of queryable projections.**

Whether the agent can ask "what are the ancestors of this path" depends on whether that projection exists — a cataloguing question, not a grammar question.

So the loop closes: the vocabulary only describes (closed); projections do the computing (replaceable, trusted through content addressing); the map says which questions can be asked.

### This is the most Unix-shaped part of the design

Unix has no query language. It has **small programs plus a directory** (`/bin`). What you can ask depends on what is installed.

The same structure here, with "program" replaced by "projection" and "directory" by "the map".

---

## 3. No-go zones

### 3.1 The model

Not "draw an area where it may act", but **the human draws a ring around something: acting on what is inside requires approval, and without approval it is absolutely not allowed.**

| | Sandbox / allowlist | No-go zones / denylist (adopted) |
|---|---|---|
| Default | deny | allow |
| What the human writes | what is permitted | **what is forbidden** |
| Cost | never enough | must be backstopped by reversibility and audit trail |

### 3.2 The three pillars of safety

With allow-by-default, safety can only rest on three things:

1. **The red line is hard** — hitting it means stop, not "let's discuss".
2. **Reversible** — act freely outside the ring, but every action can be taken back.
3. **Recorded** — when it cannot be taken back, at least it can be traced.

Corollary: **block-level snapshots are promoted from a feature to a foundation.** Starting with A/B slots plus a rescue host is not caution; it is a requirement of this model.

### 3.3 How the red line is drawn: by reversibility, not by importance

> The red line is not "the important things", it is **"the things you cannot take back"**.

Any `did` whose verb is `send` is the red line. No separate "irreversible list" needs maintaining.

### 3.4 Need-to-know = a policy compiler

- The agent does not see the whole set of no-go zones, only the part relevant to the current task.
- "Relevant" cannot be decided by the agent itself; compilation happens outside its control — but this is **an internal mechanism of the no-go zone seam, not a new layer**.
- Audit trail must record *which lines it was shown*: accountability asks what it was permitted to know.
- It cannot see the map's red lines, but it can hit the fence: hitting it means stop, then request.

### 3.5 Enforcement lives in the hand, not the brain

The red line cannot live in the agent's good intentions. It must live at the **action exit** (the executor). This is a hard constraint on code structure.

---

## 4. Reversibility

### 4.1 The axiom

> **Nothing is ever modified; there is only a new version plus a pointer swap.**

Once this holds, these all disappear: locks, half-written state, torn writes, backups, restores, dirty reads, merge conflicts — because nothing is ever changed in place.

### 4.2 Only two primitives remain

- **fork**: open a new world (O(1), free)
- **prune**: drop a stretch of history (automatic, see 4.4)

Snapshots / backups / transactions / rollbacks — four concepts disappear together.

### 4.3 Total order plus observer projections

- The only thing that must be agreed on is **what happened, in what order**.
- State is **an observer's projection**: the world it sees is the prefix of events it has consumed.
- **There is no global "now"**, only each observer's own. Consistency is required only at the boundaries (no-go zones, audit trail).
- There is exactly one point of contention: who may advance the reference. The whole system needs **one atomic operation: a compare-and-swap on a reference.**

### 4.4 Memory = reachability

Anything nobody references is reclaimed automatically. The only thing you decide is what you still point at — and what you still point at is what you still care about.

**Forgetting is automatic, and semantically correct: unreachable means forgotten.**

### 4.5 Time as a coordinate

History is never deleted, so "the state at noon yesterday" is not something to restore but **a reference that still exists**:

> **"Go back to yesterday" is not a restore, it is an as-of query.**

Reversibility turns from an operation into a coordinate system: the past never disappeared, it is merely unreferenced for now.

### 4.6 Processes do not need to be undone

A process is not state; it is a reader of the world. It dies, and the world remains for the next reader.

> **You do not undo processes; you undo the world.**

Memory does not participate in reversibility; continuity lives in the ledger, not in RAM.

### 4.7 Three hard rules

1. **Every action happens inside a fork; the reference advances only on commit.** Otherwise "crashed halfway through" cannot be expressed (an unadvanced reference means it never happened).
2. **If the ledger cannot be written, everything stops.** Otherwise the system acts without recording.
3. **Changing the vocabulary is a `counts` claim: "counts as the same system".** The same move handles brain swaps, generations and vocabulary changes.

---

## 5. Memory, views and context

### 5.1 Three different things

| | What it is | How big |
|---|---|---|
| **the ledger** | everything that happened | may be large; reclaimed by reachability |
| **a view** | what one observer sees right now | **has a hard budget**; exceeding it is a design error |
| **a digest** | the minimum needed to rebuild a judgement | as small as possible; the raw material for views |

### 5.2 What to keep

> **The value of process equals undecidedness.** Once there is a conclusion, the process can be compressed into an evidence digest; only while undecided is the process worth keeping.

- **Keep forever**: conclusions, decisions, rule changes, signatures, causal boundaries.
- **Keep for a window**: process (every attempt, every reading) — by policy window; freeze on incident.
- **Discardable**: duplicate observations, recomputable derivations, raw streams already covered by a digest.

**Forgetting leaves a trace too**: one trace per reclamation (range, time, reason). It costs nothing but makes it possible to say what was forgotten and on what grounds.

### 5.3 Default: don't load

> **Nothing may enter the context on its own.** Everything that enters must have been selected.

- History is a library, not the air.
- There is no "restore the context" operation — because nothing was ever ambient.
- Every `read` is itself a `did`, so what it read is auditable.

**This is a security property, not only a performance one.** Ambient context is the only entry point for prompt injection: text in files, web pages and logs walks into the context by itself. Default-don't-load means content must be explicitly read, so injection fails structurally — not by filtering, but because the pipe does not exist.

### 5.4 The map: the single auto-loaded exception

- **The map is the self-report's default view.** It does not open a new seam.
- It loads automatically, and **nothing else may**. One exception is auditable: "what else is crawling into the context?" — only the map.
- One source, two readers: the human reads the Screen, the agent queries the index.
- **The map must fit on one screen. If it does not, the system is too big.** This is the best available measure of "exemplary".
- The map lists **categories and entry points**, never instances ("there is a /lab store", not "there are 37,412 files").
- **The map is not cached**: regenerated from the current ledger, or updated incrementally by sequence number. A stale map is worse than no map — it leads to reasonable-looking conclusions that are wrong.

**The complete shape of the self-report**: one screen of map + retrieval on demand + every read leaves a trace.

---

## 6. The Screen

Four panels, none optional:

1. **What it is doing** — how far, where it is stuck (a work site, not monitoring)
2. **What it needs from you** — the things only a human can decide (= unsatisfied `require`)
3. **Who it is** — what it has, what it is holding, what it intends
4. **How it sees you** — its observations about the human

It is not a monitoring dashboard: it shows *the agent*, not the machine's medical chart.
It is also the **handoff packet**: a new brain's initial context is these four panels, not the whole ledger.

**Who vouches for the self-report?** Claims without a `because` chain cannot enter the projection; `counts` stipulates what counts as evidence.

---

## 7. Layering

| Thing | Written by | Changeable |
|---|---|---|
| **Invariants** (four predicates + three pillars) | us, hard-coded | no |
| **No-go zones / definitions** (`may` / `counts`) | the human | the human yes, the agent no |
| **Reference implementations** (all implementations) | us | anyone |

**First-party work is a "reference implementation", not a "privileged component"**: it must answer "if you delete it, how does someone else fill the gap?" If it cannot, it is not a reference implementation.

A distribution = a set of reference implementations + a set of seams + a few invariants + a set of no-go zones.

**Rules need no approval, only visibility; conflicts are not resolved automatically, only surfaced automatically.** (An immutable ledger already makes silent edits impossible; when two active rules contradict each other, mark the conflict "undecided" and surface it on the Screen.)

**Who writes `counts`**: the human writes; the agent may propose. Drafting and taking effect are separate — the agent may submit a `counts` claim marked as a proposal, which has no effect until a human signs it. The proposal is itself a claim and remains auditable.

---

## 7.5 Agents are external

**We do not build agents.** This is not a concession; it is the historical pattern: Unix won by running other people's programs, the web by running other people's pages. An agent OS that runs only its own agent is a walled garden.

So the shape is the classic M×N problem, solved the classic way:

```
N agent hosts (Claude Code, Codex, Cursor, Gemini CLI, your own scripts)
M capabilities (append a claim, query, execute, request approval)

        -> one ABI + N thin adapters
```

> **The seam is the adapter boundary.**

This closes D-014: the seam layer is not a new abstraction to invent, it is the place where adapters attach.

### Two rules that must hold now

**1. MCP is an adapter, not the ABI.**
MCP is the de-facto standard and supports every major host, so an MCP adapter is the cheapest way in. But MCP is still evolving; adopting its model as our ABI would let someone else's abstractions leak into the core — the same discipline as "the kernel gives us processes, memory, devices, nothing else". **Our ABI is ours; MCP is one adapter around it.**

**2. Agent identity is the answer to append authority.**
Each adapter session issues a capability token. The `by` field stops being a self-description and becomes an authenticated identity. A foreign agent is untrusted by default and is granted rights item by item.

### The consequences

- Adapters must contain **no logic**. Logic in an adapter turns it into a privileged component, which breaks replaceability.
- Continuity lives in the ledger, not in the agent — so **any** agent can pick up the work, including one that has never seen this machine.
- Multi-vendor support is not a feature; it is the point. The pitch is not "our agent is better" but **"any agent lives better here"**: memory, history, boundaries, a world that can be rolled back.

---

## 8. Engineering discipline

1. **No new layers.** Functionality may only be added as an observer, a claim, or a projection. A mess is not too much code; it is unclear boundaries.
2. **Exactly one hot path**: action → audit trail → projection. A second path means a second truth.
3. **Measure from week one**: end-to-end action latency. "Extreme performance" that is not measured is folklore. A 2-core machine is the whetstone.

**The five gates of "exemplary" (for reference implementations)**: readable on one screen / zero external dependencies / explicit memory and latency bounds / replaceable without hurting others / no configuration files.

**The tradeoff**: exemplary applies only to reference implementations; the periphery is allowed to be ugly. That is what replaceability is really for — it means you do not have to get every part right.

---

## 9. The substrate

### 9.1 The substrate is not "an operating system", it is "a pile of things we cannot physically build"

We can write software; we cannot conjure page tables, interrupts, drivers, the hardware basis of isolation (MMU, rings, virtualisation), the physical source of time, the root of trust at boot, or devices.

Everything else — storage format, scheduling policy, permission model, projections, interface — **is our own algorithm**.

So the question is not "Linux or not Linux", it is: **which foreign abstractions must be kept outside the door.**

### 9.2 We need exactly six things

1. Run our code, with isolation and resource bounds
2. A block device that persists and allows random reads
3. A monotonic clock
4. The shortest path to display and input
5. A measured boot chain from firmware to our first line of code
6. A hardware interface with no surplus abstraction

(The former seventh item, block-level snapshots, is withdrawn — see 9.4.)

### 9.3 Discipline matters more than selection

> **The kernel gives us three things only: processes, memory, devices. Nothing else.**

No filesystem semantics of our own, no systemd, no reading `/proc` as a source of fact, no inode as identity.

**Purity depends on the call surface, not the build surface.** Compiled in but never called is the same as absent.

### 9.4 No block-level snapshots

Because immutability lives in **our own storage**, not in the filesystem. Installed packages, `/etc`, service configuration are all claims pointing at blobs, regenerable at any time. Outside the ledger, only two things genuinely exist: `vmlinuz` and our own code. They are tiny; A/B slots suffice.

> What we need is not a snapshot, but **a log that never overwrites**.

### 9.5 The route: L1 + L2

- **L1** — a trimmed kernel: a config built for this machine's hardware, keeping processes / memory / block devices / network / display / input.
- **L2** — zero distribution: we are PID 1; no systemd, no udev; no mounting general-purpose filesystems; no glibc (musl or direct syscalls); storage talks to the block device directly.
- **L3** — the kernel demoted to a driver domain, our OS running outside it: **not now, recorded as technical debt.**

> **L3 is an engineering compromise, not a concession in principle. When we are able, it must be done fully.**

### 9.6 The measure

> **The system should contain exactly two pieces of other people's code: `vmlinuz`, and hardware firmware.**
> Everything `find / -type f` returns should be ours.

This can be checked by a gate; until it holds, record what is still borrowed as a burn-down list rather than relying on memory.

### 9.7 Implementation language and platform

| Layer | Now | Later |
|---|---|---|
| Platform | x86_64 (this AIO) | arm64; the ABI stays neutral in byte order and pointer width |
| Boot | UEFI + UKI, no initrd or a minimal one; A/B slots plus the rescue host | unchanged |
| Isolation | namespaces + cgroups (L2); **the executor is a userspace process** | L3: the kernel demoted to a driver domain |
| Core language | **Rust** | — |
| Probe language | **Python** | — |

The executor is an ordinary userspace process, not a kernel module: it must change often and be replaceable, and anything put into the kernel never comes back out.

**One hard rule, more important than the choice of language:**

> **No language's types may appear in the ABI.**

Serialise with a fixed format (CBOR or a fixed binary layout); never put `#[repr(C)]` structs on the wire. Only then is "changing the language" possible — and whether the language can be changed is the first real test of whether the ABI is implementation-neutral at all.

Rust was chosen for longevity and for memory safety at the enforcement point. Cost accepted: compiling Rust on this 2-core machine is painful, so heavy builds may move to the workstation — which collides with the existing "no heavy builds on this machine" preference and must be resolved when the core starts.

---

## 10. Test cases: ten already passed

| # | Scenario | Result |
|---|---|---|
| 1 | Two agents write the same file at once | ✔ locks vanish; contention becomes "who may advance the reference" |
| 2 | Crash halfway through a write | ✔ actions run inside a fork; an unadvanced reference means nothing happened |
| 3 | An agent calls a sub-agent | ✔ the chain of responsibility is traceable via `because` |
| 4 | An email arrives from outside | ✔ the gateway records `did(read)`; but you can never know if the other side deleted something |
| 5 | A daily mandatory backup | ✔ `may require` plus time; overdue is computed from the absence of a matching `did` |
| 6 | Two humans give opposite instructions | ⚠ expressible, but *how to prioritise* is not in the vocabulary |
| 7 | Upgrading the system / changing the vocabulary | ✔ via `counts`: "counts as the same system" |
| 8 | Who may read which stretch of the ledger | ⚠ expressible; real privacy needs encryption |
| 9 | Disk full, the ledger cannot be written | ✔ hard rule: stop everything |
| 10 | Moving to a new machine a year later | ✔ migration is a read, not a move |

**The boundary the ten cases reveal:**

> **The four predicates are a language, not a policy.**

They let you **write down** anything; they cannot make **decisions** for you: whose rule wins, what runs first, how to encrypt, how to recover. Those are policy, belonging to reference implementations and to the human.

**Writing something down is not the same as solving it.**

---

## 11. Open questions

1. **The seam layer** — deferred (D-014). Wait until the probe shows which boundaries are actually replaced.
2. **The reference implementation list** — deferred (D-021).
3. **The map budget** — how many bytes "one screen" is — deferred (D-022).
4. **`counts` vocabulary governance** — whether "human writes, agent proposes" is enough to prevent bloat; verify in the prototype (D-019).
5. **v0 install / rollback** — how it lands on the existing four-partition layout.
6. **The human is not a monolith** — rules succeed each other in time; genuinely simultaneous conflicts are undesigned.
7. **The measured boot chain is absent during the probe**: the only true root of the `because` chain is the human signature. The missing hardware measurement must be marked explicitly as an **assumption**, never dressed up as evidence.
