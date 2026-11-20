# Decision log

Append-only. Every entry has four fields: context → ruling → consequences → relations.
Overturned entries are **never deleted**: they are marked "superseded by D-0xx", and the new entry names what it supersedes (both directions).

---

## D-001 The agent is the owner

- **Context**: existing agent products still have the human as the subject — the human instructs, reviews, cleans up. From first principles, that is "an AI living inside someone else's system".
- **Ruling**: the system's owner is the agent, not the human. The system is its body.
- **Consequences**: interface, permissions and logs are organised around *it*; the Screen shows the agent, not machine metrics.
- **Relations**: no predecessor; reinforced by D-002.

## D-002 The human is the constitution, not the operator

- **Context**: once the subject changes, the human's position must be redefined, or "who is responsible" cannot be answered.
- **Ruling**: the human does not operate, but sets boundaries. Boundaries are written to disk (no-go zones, definitions), not spoken in chat.
- **Consequences**: boundaries must be inspectable, signed and timestamped; accountability asks what was permitted at the time.
- **Relations**: reinforces D-001; depends on D-004.

## D-003 Sandbox allowlist (default deny)

- **Context**: the first version followed the conventional approach: give the agent "an area it may act in".
- **Ruling**: allowlist plus default deny.
- **Consequences**: an allowlist is never complete, and it collides head-on with "it should be able to do anything".
- **Relations**: **superseded by D-004**.

## D-004 No-go zones: denylist, allow by default

- **Context**: D-003's allowlist cannot cover "general purpose"; every new capability required editing the list.
- **Ruling**: the human only draws rings (no-go zones); inside a ring requires approval; outside is allowed by default.
- **Consequences**: safety cannot rest on prior permission, only on three pillars — a hard red line / reversibility / an audit trail. Block-level snapshots are promoted from a feature to a foundation.
- **Relations**: **supersedes D-003**; depends on D-005.

## D-005 Red line = irreversible = send

- **Context**: a red-line definition was needed that would not grow with requirements.
- **Ruling**: draw it by reversibility, not importance. `did` has only three verbs — read / write / send — and `send` is the only one that crosses the boundary.
- **Consequences**: no "irreversible list" to maintain. Enforcement must live in the hand (the executor), not the brain.
- **Relations**: supports D-004.

## D-006 The base: four predicates

- **Context**: a minimal generating set was needed — enough to derive everything, with nothing redundant.
- **Ruling**: `is` / `did` / `may` / `counts`. The criterion is "keep only what cannot be derived"; the four fail in four different ways (wrong / missed / violated / void).
- **Consequences**: every system concept becomes a projection; the vocabulary is closed, so new requirements must be translated — what cannot be translated belongs to a reference implementation.
- **Relations**: absorbs D-007.

## D-007 Drop `will`

- **Context**: an early version made "intent" a fifth predicate.
- **Ruling**: intent is `is(agent, goal)`; declaring is also a `did`. A plan, once spoken, is a fact.
- **Consequences**: there is no separate "intent vs. reality" dataset, so drift disappears structurally.
- **Relations**: absorbed by D-006.

## D-008 Total order plus observer projections

- **Context**: global state and a shared pointer introduce locks, contention and the question of whose truth wins.
- **Ruling**: guarantee only "what happened, in what order"; state is an observer's projection. There is no global "now".
- **Consequences**: no global lock; consistency is required only at the boundaries (no-go zones, audit trail); the only contention left is who may advance a world's reference. **Revised by D-036**: that compare-and-swap is *per world*, not global — a single global reference would be a cache-line hotspot.
- **Relations**: supports D-011.

## D-009 Explicit amendment (mandatory supersession chain)

- **Context**: the worry was silent rule changes producing "shadow rules".
- **Ruling**: any rule change must leave an explicit supersession chain, or the system raises an alarm.
- **Consequences**: too heavy; it imposes process on daily work.
- **Relations**: **superseded by D-010**.

## D-010 Surface conflicts, do not require approval

- **Context**: an immutable, append-only ledger already makes silent edits impossible — D-009 was duplicated machinery.
- **Ruling**: no process required. Only visibility required. When two active rules contradict each other, mark the conflict "undecided" and surface it on the Screen.
- **Consequences**: zero cost in normal operation; it only asks the human when a real conflict appears.
- **Relations**: **supersedes D-009**.

## D-011 Memory ≠ storage: default don't load

- **Context**: letting all history into the context bloats it, pollutes judgement, and is the entry point for prompt injection.
- **Ruling**: split ledger / view / digest; the value of process equals undecidedness; forgetting leaves one trace; **nothing may enter the context on its own**.
- **Consequences**: history is a library, not the air; injection fails structurally — not by filtering, but because the pipe does not exist.
- **Relations**: depends on D-008.

## D-012 The map is the self-report's default view, and the only auto-loaded exception

- **Context**: with default-don't-load, the agent still needs to know what it may ask for, or it can ask nothing.
- **Ruling**: do not open a new seam; the map belongs to the self-report. The map loads automatically, nothing else may. The map must fit on one screen and must not be cached (it is a projection, not a cache).
- **Consequences**: the map's size becomes a hard ceiling on system complexity; a stale map is forbidden because it produces reasonable-looking but wrong conclusions.
- **Relations**: depends on D-011.

## D-013 Fix the substrate requirements first, then choose

- **Context**: choosing Linux or non-Linux directly degenerates into picking first and finding reasons after.
- **Ruling**: write the seven substrate requirements first (isolation bounds / measured boot / snapshots / namespaces / clock / display path / minimal boot), then derive.
- **Consequences**: selection becomes arithmetic rather than a stance. Later revised by D-016 and D-018 (seven became six, and the choice was made).
- **Relations**: revised by D-016 / D-018.

## D-014 The seam layer: deferred

- **Context**: v0.5 deleted the whole "six seams" section (it looked redundant with the four predicates), which left a gap — "everything is replaceable" had no explicit attachment point.
- **Ruling**: neither restore nor re-count. Wait until the probe shows which boundaries are actually replaced.
- **Consequences**: replaceability currently lacks an explicit anchor. This is a known gap, not an oversight.
- **Relations**: related to D-006. **Closed by D-028**: the seam is the adapter boundary, so no new abstraction needs inventing.

## D-015 `/lab` joins git: secrets isolated to `.machine/`

- **Context**: three local files (a 0600 proxy config, an installer, a screen-off script) belong to the machine, contain credentials, and stood in the way of git.
- **Ruling**: move them into `/lab/.machine/` and gitignore the whole directory; repository root = project root.
- **Consequences**: secrets are physically separated; index, gate and context never cover that directory. First commit awaited a git identity (since resolved).
- **Relations**: supports D-011 (default don't load).

## D-016 Substrate route: L1 + L2, L3 recorded as technical debt

- **Context**: first principles demand building everything, but drivers cannot be conjured.
- **Ruling**: L1 — a trimmed kernel configured for this machine — plus L2 — zero distribution (we are PID 1; no systemd/udev; no general-purpose filesystem mounts; no glibc). L3 (kernel demoted to a driver domain) is not done now.
- **Consequences**: **this is an engineering compromise, not a concession in principle.** When able, L3 must be done fully; this entry must never be read as "abandoned permanently".
- **Relations**: revises D-013.

## D-017 Purity is about the call surface, not the build surface

- **Context**: it is tempting to treat "a smaller kernel build" as "purity".
- **Ruling**: compiled in but never called is the same as absent. The real discipline: **the kernel gives us processes, memory and devices only** — no `/proc` as a source of fact, no inode as identity, no dependency on systemd.
- **Consequences**: the gate should check what is called, not how large the image is.
- **Relations**: supports D-016.

## D-018 Block-level snapshots are no longer a substrate requirement

- **Context**: item three of the original seven mistook someone else's mechanism for our own requirement.
- **Ruling**: immutability lives in our own storage, not in the filesystem. Outside the ledger only `vmlinuz` and our code exist, and A/B slots are enough for those.
- **Consequences**: seven requirements become six. What is needed is **a log that never overwrites**, not a filesystem snapshot.
- **Relations**: **revises D-013**.

## D-019 `counts` is human-written; the agent may propose

- **Context**: human-only is too heavy (every criterion needs a human); agent-writable means it always succeeds.
- **Ruling**: drafting and effect are separate. The agent may submit a `counts` claim marked as a proposal, which has no effect; a human signature makes it effective.
- **Consequences**: the human reviews rather than writes from scratch; the proposal is itself a claim and stays auditable.
- **Relations**: refines D-006 / D-007.

## D-020 Probe: install a package, then send an email, both in a fake world

- **Context**: a minimal closed loop is needed, without dirtying the machine (a real install changes apt state).
- **Ruling**: two steps. First "install a package", running read → write → reference advance → rollback. Then "send an email", hitting the `send` red line and the signature flow. Both in a fake world under `/lab/probe/world/`: real claims, no real actions.
- **Consequences**: the first runnable artefact is a ledger plus two projections ("what it is doing" / "what it needs from you").
- **Relations**: no predecessor.

## D-021 Reference implementation list: deferred

- **Context**: building all 8–10 pieces in-house delays the first boot by months, colliding with "use your eyes to veto the direction early".
- **Ruling**: do not fix the count yet. Let the probe reveal what is genuinely required.
- **Consequences**: no committed component count; outward wording uses "reference implementation", never "core component".
- **Relations**: related to D-016; review trigger: after both probes (install, send).

## D-022 Map budget: deferred

- **Context**: whether "one screen" is the human reading or the agent reading decides who sets the limit.
- **Ruling**: no number yet. The inclination is that the human sets it (the human is the constitution), but first see how long the map actually is.
- **Consequences**: no hard ceiling yet; the gate does not check map size.
- **Relations**: related to D-012; review trigger: once the probe produces a first map.

## D-023 License: GPL-3.0-only + CLA + trademark + CC BY-4.0

- **Context**: the goals are simultaneously "become the standard / the orthodox one" and "someone eventually buys me". The earlier inclination was to block commercial use (PolyForm NC / BSL), but that collides directly with standard formation — **charging prevents adoption**.
- **Ruling**: code GPL-3.0-only (commercial use free; modifications must be published); docs CC BY-4.0 (credit is the only obligation); the name "TonyOS" is reserved (`TRADEMARK.md`); outside contributions require a CLA with a relicensing grant (`CLA.md`). Chose `-only` over `-or-later` to keep the decision about future licence versions.
- **Consequences**: all licence revenue is given up. The moat moves to the trademark, official builds, and the position of reference implementation. The CLA preserves the options of dual licensing and of "selling the position"; it can later be relaxed to DCO as a goodwill move. **A licence cannot be retracted for published versions.**
- **Relations**: supersedes the earlier "block commercial use" inclination (never formalised); follows the Linus route — GPL, no fees, control through copyleft and trademark rather than price.

## D-024 Vocabulary aligned with established terminology

- **Context**: several coined terms had exact equivalents in the literature (truth maintenance systems, saga/compensation, CQRS, XACML, policy-as-code), forcing every reader to translate mentally.
- **Ruling**: use the standard term for the *mechanism*; keep the image for the *concept* where no standard term exists.
  - adopted: `audit trail`; `reference implementation`; `technical debt`; `need-to-know`; `policy compiler`; `non-compensatable action`; `policy enforcement point`.
  - kept: `counts-as`, `no-go zone`, `the map`, `the Screen`, `seam`.
- **Consequences**: the public vocabulary changed at v0.7. The Chinese originals remain in git history (commit `f8d5d38`).
- **Relations**: **superseded by D-025** — the adopted renames survive, `claim` does not.

## D-025 Coin a term when it fits better, and document the delta

- **Context**: "prefer the standard term" is a good default but a bad absolute. Standard terms carry assumptions. `assertion` (TMS) denotes a node whose truth the system maintains; ours are authored, contestable, and immutable. Forcing our concept into that word imports a model we do not have.
- **Ruling**: a term earns its place by fitting. If no existing term fits, coin one — and then you owe the reader three things: **our definition, the nearest existing concept, and where ours differs.** The register is the terminology table at the top of `FOUNDATION.md`, and every coined term must be entered there. `claim` is restored.
- **Consequences**: the vocabulary may be idiosyncratic, but never unexplained. Adds a gate check: every row of the terminology table must carry all four columns, so a term cannot be introduced without its delta.
- **Relations**: **supersedes D-024**.

## D-026 No language: descriptions fit the predicates, computation lives in projections

- **Context**: after closing the vocabulary, the obvious next question was whether this is a programming language, and whether derivation needs a rule layer (Datalog-style) to stay trustworthy.
- **Ruling**: the system provides an ABI and a protocol, not a language. A language would require an open, user-extensible grammar, which contradicts closed vocabulary; it would be the largest possible new layer; and it would be the least replaceable thing in a system built on replaceability. Derivations live in projections, made trustworthy by **pinning the projection's code hash in the claim's justification** — reproducible like a build, not declarative like Datalog.
- **Consequences**:
  - decision procedure: describe → one of four predicates; compute → a projection (a reference implementation).
  - the boundary that must not blur: deterministic projection = derivation (re-runnable); non-deterministic projection (an LLM) = a claim by an agent (accountable, not re-runnable).
  - the map becomes the **catalogue of queryable projections** — "what can be asked" is a cataloguing question, not a grammar question.
  - accepted cost: users cannot extend derivation by writing rules; they extend it by writing projections, which are replaceable units.
- **Relations**: refines D-006; supplies the missing half of D-012 (the map's contents).

## D-027 Implementation: Rust core, Python probe

- **Context**: the core must satisfy four things at once — memory safety at the enforcement point, ten-year longevity, small static binaries, and stock on a 2-core machine.
- **Ruling**: the probe is written in **Python** (its purpose is to be contradicted quickly, not to be elegant). The core is written in **Rust** (longevity and memory safety outrank compile speed). **No language's types may appear in the ABI** — fixed-format serialisation only, so the language remains replaceable.
- **Consequences**: heavy builds may have to move to the workstation, colliding with the existing "no heavy builds on this machine" preference; resolve when the core starts. "Can the language be changed?" becomes the first test of whether the ABI is genuinely implementation-neutral.
- **Relations**: depends on D-016 (L1+L2); supports D-026 (no language in the vocabulary).

## D-028 Agents are external: one ABI, N thin adapters

- **Context**: building our own agent is unrealistic, and users will want whichever agent they already like. The system must be agnostic to the source of intelligence.
- **Ruling**: do not build agents. Solve M×N with one ABI plus N thin adapters. **The seam is the adapter boundary** (closing D-014). **MCP is an adapter, not the ABI** — the same discipline that keeps kernel abstractions out of the core. Each adapter session issues a capability token, so `by` becomes an authenticated identity rather than a self-description — this is also the answer to the previously unrecorded gap: **who may append to the ledger**.
- **Consequences**: adapters must contain no logic, or they become privileged components. Continuity lives in the ledger, so any agent can take over. Multi-vendor support is not a feature but the point: *any agent lives better here*.
- **Relations**: **closes D-014**; resolves the append-authority gap noted in the 2026-11-20 retrospective; supports D-008 (per-observer projection).

## D-029 Done means evidence; plausibility is not proof

- **Context**: the owner named the failure mode directly — the AI produces what was asked for, the output *looks* finished, nothing is verified, and someone inherits the mess ("管杀不管埋"). It is the pattern that spread with vibe coding, and it is cheap to fall into because a model optimises for plausible, not for true. This session came close three times: a whole-repository translation verified only mechanically (no human read the English), two design choices applied during the probe without a ruling, and 28 decisions taken against zero run results.
- **Ruling**: a completion claim must carry evidence — the command run and where its output is. Anything not run is labelled **not verified**. A gap is left open rather than filled with a guess. A design choice found while implementing is raised, not applied.
- **Consequences**: work is slower, and reports will sometimes end in "not verified". Accepted deliberately: the product is accountability, so the method that builds it cannot be "it looks right".
- **Relations**: refines D-002 (the human signs); structurally the same rule as D-019 — an agent's claim only becomes real when it carries something outside itself.

## D-030 Every claim carries a world; norms may be global

- **Context**: the probe could not tell which branch a claim belonged to. Recalling a derivation after a rollback was ambiguous, and the alternative — "a fork that deletes the red line and then sends" — is a legal exploit.
- **Ruling**: every claim carries `world`. `may` and `counts` may use `*` (global); `is` and `did` must land in a concrete world. The rule is mechanical — read the predicate, not the intention.
- **Consequences**: norms cannot be rolled back by an agent; facts are always attributable to a branch. Hardware facts are re-asserted per world, which is redundant but never ambiguous.
- **Relations**: derived from probe finding 1; depends on D-006.

## D-031 A viewpoint is a root claim; slicing belongs to the store

- **Context**: the first projection took the ledger and assumed "now", then reported `installed` after the rollback. An earlier attempt to fix this by making the world an API argument did not work: the projection would still read a claim from another world and merely stamp it with the right name.
- **Ruling**: a viewpoint **is** a root claim — it pins the branch (`subject`), the moment (`seq`) and the tree (`value`) in one immutable identifier. The store produces the slice visible at that viewpoint; a projection receives the slice, never the ledger, so it cannot read another world by accident. Multi-world projections must name several viewpoints explicitly.
- **Consequences**: "the same question, two viewpoints, two opposite answers, both correct" is now the probe's proof. Scope resolution is one implementation in one place rather than a discipline repeated in every projection.
- **Relations**: derived from probe finding 2.

## D-032 A commit is one `did` plus one root; files never appear

- **Context**: per-file claims would take hundreds of records for one install, and a "batch" field would invent vocabulary to fix a problem that was really only about the screen.
- **Ruling**: a commit is one `did` and one `is(world, root)`. The `did` records the verb, the viewpoint it started from (`at`, which doubles as the compare-and-swap precondition) and the result tree; the root records the tree. "Where it came from" appears exactly once. Files never appear at all; diffs are projections.
- **Consequences**: granularity is the committer's judgement, recorded on the ledger. "Half-installed" stops existing. Per-file provenance weakens: the ledger answers *who* and *what diff*, not *which byte, when*.
- **Relations**: derived from probe finding 6; supersedes the "batch form" proposal in probe/README (first pass).

## D-033 Trust root: split authorization from integrity, and mark the missing half

- **Context**: the first signature approved itself. That is a circle: a system cannot ground itself. Two different guarantees are usually conflated here — *who said yes* and *is this machine what it claims*.
- **Ruling**: authorization is grounded in a human signature (possible today, out of band); integrity is grounded in a measured boot (not available on this machine). The absent half is written down as an **assumption claim authored by the human**, never dressed up as evidence.
- **Consequences**: any chain ending in the assumption carries that label; the Screen can show "root: assumed (unmeasured)"; when measurement arrives, old conclusions keep their label rather than being retroactively upgraded.
- **Relations**: derived from probe finding 5. **Deferred beyond the assumption claim** — triggers: the first third-party agent (identity first), and any external release (integrity).

## D-034 An approval is spent by using it; expiry is a ledger position

- **Context**: after the first approval, `send` was allowed forever — nothing bounded a signature. The probe showed `needs=[]` even after a rollback.
- **Ruling**: one signature authorises one act. The `did` that performs the act also retracts the signature it consumed, so the act and the spending are a single claim. An approval may carry `until`, expressed as a **ledger position**, never as a wall time. A target may be named, so a signature for one recipient cannot be spent on another.
- **Consequences**: no counters, no decrement, no revocation sweep. "Who used this signature and when" is answered by the send itself. Expiry is checkable without trusting a clock.
- **Relations**: derived from probe finding B; depends on D-019 (a signature is what makes a proposal real).

## D-035 A fork is a commit whose view points into another world; ancestry belongs to the world

- **Context**: the probe needed a second world. The first implementation walked ancestry from each viewpoint's own `because`.
- **Ruling**: forking needs no new vocabulary — it is a `did` in the new world whose `view` names a viewpoint in the old one, followed by a root claim. Ancestry is derived **once per world**, from the world's first root, not per viewpoint.
- **Consequences**: the child sees the parent's claims up to the fork point and never after; a rollback in the parent leaves the child untouched; a sibling never sees the other's work. The bug that forced this rule failed *silently* — after any `tick`, the fork's lineage vanished and the child quietly stopped seeing its parent, with no error and a plausible-looking screen.
- **Relations**: derived from probe pass 3; depends on D-031 (viewpoint) and D-032 (commit).

## D-036 First principles, then performance, then elegance

- **Context**: the owner set the ordering explicitly, after the RCU story: elegance is not a goal in itself, and it is not the tie-breaker. The failure mode is real and old — the single clean invariant that looks beautiful and quietly destroys multicore throughput.
- **Ruling**: **first principles first; performance second; elegance third** — as a system-wide guiding order, not a rule about any one module. Elegance already includes readability, maintainability and consistency, so "it will be easier to maintain later" is not a fourth tier. Operationally, every design tradeoff must state **which of the three it gave up**: elegance (allowed, no reason needed) / performance (allowed, but it must carry a number) / first principles (not allowed, except as an explicitly recorded exception).
- **Consequences**: the first application is §4.3 — one global reference and one global compare-and-swap becomes **one reference per world**. Contention then exists only inside a world, and worlds are already isolated by design. This changes no axiom: nothing is still ever modified, and the system is still reversible; only a piece of tidiness was given up.
- **Relations**: revises FOUNDATION §4.3; same root as D-017 — both say *align with the machine's real behaviour, not with how the diagram looks*.

## D-037 Performance order: concurrency and throughput, then latency, then footprint

- **Context**: D-036 put performance above elegance but never said *which* performance. "All-round good" is a wish, not a budget: when two designs trade off, something must break the tie. The owner set the internal order explicitly.
- **Ruling**: when designs trade off, prefer **concurrency and throughput** first, **latency** second, **resource footprint** third. Boot time counts as latency. As with D-036, a tradeoff must name the tier it spent: spending footprint needs no argument, spending latency needs a number, spending throughput needs an explicit exception.
- **Consequences** (derived, each to be tested rather than assumed):
  - Any **global serialisation point on the write path** is now the first suspect, not a footnote. The probe's global `seq` is the named suspect.
  - Per-commit `fsync` bounds throughput at the device; this ordering therefore **predicts group commit** — spend latency, buy throughput. That is the ordering working as intended, not a regression.
  - On one block device, software must not serialise what the device would allow. The target is **no self-inflicted serialisation**, not "unlimited concurrency": two cores cannot demonstrate 64-core scaling, only the absence of a lock convoy.
  - Footprint is third, not free. Each tier still needs a floor or ceiling, or "third" silently becomes "unbounded" on a 3.7 GB machine.
- **Measured** (probe E1, 2026-11-20): the first consequence above was **wrong at the I/O layer**. Sharding the log raised throughput from 102/s to 113/s at eight writers — noise. The device, not the shared file, was the ceiling. Group commit confirmed the prediction: 3,586/s, 35x, and it did not even spend latency at this load. The suspicion moves to CPU-side contention, which this experiment could not see.
- **Falsifier**: if on this machine `fsync` is not the throughput ceiling, group commit buys nothing and the predicted consequence is wrong. Measure before building it.
- **Relations**: refines D-036; makes the global-order question (FOUNDATION §4.3, probe question 6) urgent rather than open-ended.

## D-038 Identity is content, not position; no new global singleton without a replacement path

- **Context**: the owner intends TonyOS to run on clusters, with hundreds of thousands of agents. Held against that ambition, the scalable parts are real — no shared mutable state, immutable claims, per-world references, no global "now" — but the implementation had accidental singletons. The sharpest: `id = hash(... seq, ts ...)` made a claim's name depend on its position, so the same assertion on two nodes produced two ids. Content-addressing in name only, and unmergeable.
- **Ruling**: three things.
  1. **A claim's identity is its content** — subject, predicate, value, world, by, because, replaces. Position (`seq`) and observation time (`ts`) belong to the container, never to the name.
  2. **No new global singleton enters the core without a recorded replacement path for a multi-node deployment.** A singleton that cannot name its replacement is a defect, not a deferred detail.
  3. **`signature` ≠ `capability`.** A human signature authorises one act (D-034). Delegation is a pre-signed batch of one-shot grants, so it scales to many agents without a quota counter and without amending D-034.
- **Consequences**: identical claims collapse — re-asserting the same thing is not a new event. That is a consequence, **not yet a ruling**: repeated identical `did`s may need a per-author counter, because "it looked twice" is arguably part of the audit trail. Cross-node merge becomes possible in principle; the claim store is now a set as much as a log, and order is supplied by the container.
- **Falsifier**: if two nodes can produce identical content with different meaning, content-only identity is wrong. Repeated identical `did`s are the first candidate.
- **Relations**: refines D-030, D-031 and D-032; constrains D-028 and every future scale decision.

## D-039 A commit is durable at fsync; recovery keeps the longest valid prefix

- **Context**: E2. `append()` never called `fsync`, so "committed" meant "in the page cache". One torn byte made `Ledger()` raise and lose the **entire** store, not just the tail. A flipped byte inside a value was accepted with the original id: the id was computed on write and never checked again.
- **Ruling**:
  1. **Durability**: a claim is committed when the `fsync` covering it returns. Before that it may vanish, and vanishing must mean it never happened.
  2. **Framing**: `magic | length | crc32`. Recovery returns the longest prefix of complete, checksum-valid frames; the partial tail is cut, and the cut is recorded (forgetting leaves a trace, §5.2).
  3. **Stop and report**: the first invalid frame halts recovery. Silently skipping it is forbidden — a lost tail must be visible.
  4. **Identity is derived and asserted on write.** Re-verifying identities is a scrub, not the normal read path.
  5. **A checksum is not a signature.** An agent can rewrite a frame and recompute its CRC. Adversarial integrity remains the trust root (D-033).
- **Consequences**: +10 bytes per record (5.7% on ~175-byte claims). A corrupt frame costs the tail after it unless a scrub resyncs; accepted, because silent loss is worse. The probe's failure was a **reader policy**, not the JSONL format: a lenient reader recovered the same prefix. The checksum is the part JSONL could not supply.
- **Falsifier**: a torn sector whose CRC still matches, or a filesystem that persists a later frame but not an earlier one. Either breaks "prefix" as a guarantee; neither has been tested.
- **Relations**: implements D-032, D-038 and §4.7 rule 2; depends on D-033 for adversarial integrity.
