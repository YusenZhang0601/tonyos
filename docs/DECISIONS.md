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
- **Consequences**: no global lock; consistency is required only at the boundaries (no-go zones, audit trail); the only contention left is who may advance the reference (a single compare-and-swap).
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
- **Relations**: related to D-006; review trigger: once the "install a package" probe produces a ledger.

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
- **Ruling**: drafting and effect are separate. The agent may submit a `counts` assertion marked as a proposal, which has no effect; a human signature makes it effective.
- **Consequences**: the human reviews rather than writes from scratch; the proposal is itself an assertion and stays auditable.
- **Relations**: refines D-006 / D-007.

## D-020 Probe: install a package, then send an email, both in a fake world

- **Context**: a minimal closed loop is needed, without dirtying the machine (a real install changes apt state).
- **Ruling**: two steps. First "install a package", running read → write → reference advance → rollback. Then "send an email", hitting the `send` red line and the signature flow. Both in a fake world under `/lab/probe/world/`: real assertions, no real actions.
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
  - code: `assertion` / `justification` / `retraction`; `audit trail`; `reference implementation`; `technical debt`; `need-to-know`; `policy compiler`; `non-compensatable action`; `policy enforcement point`.
  - kept: `counts-as`, `no-go zone`, `the map`, `the Screen`, `seam`.
- **Consequences**: the public vocabulary changes at v0.7. The Chinese originals remain in git history (commit `f8d5d38`), so nothing is lost.
- **Relations**: refines D-006.
