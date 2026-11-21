# Goal: the Screen

> **Status: open** (2026-11-21). Four passes; pass A is analysis only, no code.
> Previous stage: [`GOAL-head-index.md`](GOAL-head-index.md) — met.

> A bounded stage. When every item below is verified, the stage is over. A new rule is
> raised, not applied.

**Why this stage.** Three reasons, and the third is the real one.

1. It is the first thing a human can use. Everything so far is a probe that only its
   author can read.
2. It is the **handoff packet** (FOUNDATION §6): a new brain's initial context is these
   four panels, not the whole ledger. If the panels cannot carry the handoff, "any agent
   can take over" (D-028) stays a slogan.
3. It is the first place the vocabulary meets a reader who did not write it. The test
   from STATUS: **one real event, four predicates, one screen.**

**What it is not.** Not a dashboard — it shows *the agent*, not the machine's medical
chart. Not a UI toolkit, not a new seam. It is a **projection**: it receives one slice
from `visible()` and formats it. If a panel needs something the slice cannot supply, the
answer is a claim, or the vocabulary is wrong — never a hidden query.

## Definition of done

1. **The mapping precedes the pixels.** For every line of every panel: the active claim
   that supplies it, or `—`. A line with no claim behind it is a **vocabulary gap**:
   recorded as a gap, never filled with prose. Pass A's product is `probe/README.md`
   pass 9, a table, and no code.
2. **One slice, four panels.** `screen(ledger, viewpoint)` calls `visible()` exactly
   once and hands each panel nothing but the slice. A panel that can reach the `Ledger`
   has already broken D-031. **And the slice must be true**: nothing written after the
   viewpoint may appear in it, and the viewpoint itself must be in it (pass 9, S1/S2).
3. **Empty is empty.** No invented status, no "all good" placeholder, no filler that
   reads like content. An empty panel prints `—` and a count.
4. **Plain text, zero dependencies.** `probe/screen.py` writes to stdout, 80 columns,
   UTF-8. No curses, no TUI, no browser. Colour is allowed only if the text still reads
   with it stripped. Reason: FOUNDATION's five gates, and a screenshot must be
   diffable in git.
5. **The one-real-event test.** The `install → rollback → blocked send` fixture from
   `probe/demo.py` renders all four panels from the four predicates alone. If any panel
   needs a fifth predicate or an extra dimension, the stage has found what it was for.
6. **Cost measured, not guessed.** Render time and full scans at 1k / 10k / 100k
   claims. Whether `visible()` needs its own index is **raised**, not fixed.
7. **The handoff test.** An agent that has never seen the ledger gets only the rendered
   text, and must answer correctly: what is it doing / what does it need from me / who is
   it / how does it see me. Its answers are quoted verbatim, wrong ones included.
8. **Nothing old breaks.** `demo` 8/8, `crash` invariants, `concurrent` 5/5, `index` 0
   mismatches, `retract` 4 graphs, gate 0/0, tree clean, pushed.

## Order

- **A. The mapping.** No code. For each of the four panels, list the lines and the claim
  behind each one. Then run the fixture through it and check that every line resolves.
  The gaps found here decide the shape of B; **do not** start B before this table exists.
- **B0. The slice is correct first.** Pass 9 found two defects in `visible()`: global
  claims ignore the viewpoint's position (S1), and a retracted viewpoint is absent from
  its own slice (S2). Both have reproductions in `probe/README.md` pass 9. Fix them under
  evidence — a historical viewpoint must reproduce its own screen — in **one isolated
  commit**, so it can be reverted if the owner rules that `*` is retroactive. No other
  change to the read path.
- **B. The render.** `probe/screen.py`, one function per panel, slice in, lines out. Fixed
  width. Every panel readable with no prior knowledge of the fixture.
- **C. The cost.** Count `visible()` calls and full scans per render; time it at three
  sizes. Report the numbers even if they are bad.
- **D. The handoff test.** Fresh agent, screen text only, four questions, verbatim
  answers. Then pass 10 in `probe/README.md` and the numbers in `docs/STATUS.md`.

Each step leaves the previous green. Do not parallelise.

## Stop and ask the owner

- **Panel 4 ("how it sees you")** — an observation about the human is a belief about a
  person. Whether that is a plain `is` claim, a `counts` claim, or something the ledger
  should not hold at all is a privacy ruling, not an implementation choice.
- **Is the map part of the Screen?** If the Screen must also fit one screen, the map
  budget (D-022, deferred) becomes due now, not later.
- **Retracted history on a panel.** Audit wants it; a work site does not. Ruling needed
  before anyone adds it.
- Any panel that asks for a fifth predicate, a new claim dimension, or a field that is
  not derived from a claim.
- `visible()` needing an index — measure, then ask. Do not add one.
- The width itself, if 80 columns cannot hold the panels.
- Adding any dependency (a TUI, a colour library, a templating engine). Default: no.
- performance floors (the numbers themselves)
- mounting or formatting `/dev/sda3` / `/dev/sda4`
- touching `.machine/` or `编译试验机/`, or putting machine details into git
- another session's uncommitted changes in `/lab`

## Recommended answers (raised, awaiting the owner)

Pass 9 produced six gaps. These are the leader's recommendations, on record so they are
not re-litigated from memory. **None is applied.**

- **G2, "unsatisfied `require`"** — one definition, the hand's: an approval is usable iff
  `spendable()` would return it, `target` and `until` honoured. The Screen must not carry a
  second rule. Panel 2 shows **the act that was blocked and why**, never a standing list of
  requires, because a require never expires. Cost: panel 2 answers "what is stopping it",
  not "what could it want".
- **G1, a verdict for "how far"** — a result is an event: `did {verb: read, target: pkg:htop,
  test: <the counts>, at: <root>, outcome: fail}`. No new predicate, and a verdict tied to a
  root goes visibly stale when the world moves. Cost: the panel shows the last check, not
  the truth.
- **G4, a root has no kind** — no new verb, and no word the projection invented: print the
  mechanism (`root ← replaces X, because Y`), never "rolled back".
- **G5, intention** — a belief, so `is`, subject `agent:main`, concrete world, agent-authored,
  `because` bottoming out at a human signature or a sensor. Retractable, which is correct: a
  plan that changed is not a lie. Cost: §6's vouching turns into a real constraint on the
  agent, not a formality.
- **G6, panel 4** — not yet. Panel 4 prints the human's own acts as the agent holds them
  (their `may`, their `counts`, their approvals) and labels itself "what it has from you".
  Agent-authored beliefs about a person wait for the owner's ruling; the panel is honest in
  the meantime rather than empty.
- **G3, spent approvals** — the Screen is a **work site**; the audit trail is not a panel.
  "You signed one and it was spent at 13" is an as-of query, not a line on the Screen. Cost:
  the four panels are not a complete account of the past, by design.

## Rules

- **Done means evidence**: command and output. Unrun work is labelled *not verified*.
- **A panel may read and format, never compute a conclusion.** Sorting and filtering are
  formatting. "It is probably fine" is a conclusion, and it is not allowed on the Screen.
- **Raise, do not apply** a design choice discovered while implementing.
- Never delete old text; mark it superseded with a back-pointer.
- Small commits, each with the gate green. Pushing is the owner's call per commit.
- This stage is Python; no heavy builds on this machine.
- After three failed attempts at the same problem, stop and report the attempts.
