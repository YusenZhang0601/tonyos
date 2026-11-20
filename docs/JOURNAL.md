# Work log

One line per day. Only what actually happened, never plans.

| Date | What happened |
|---|---|
| 2026-11-20 | Interview settled the thesis and the base: the agent is the owner, the human is the constitution, no-go zones (denylist), four predicates (is/did/may/counts), default don't load. Project skeleton and gate created. |
| 2026-11-20 | Seven rulings: secrets isolated to `.machine/` + git init; substrate L1+L2 (L3 as technical debt); `counts` human-written with agent proposals; probe in two steps (install → send, fake world). Seams / implementation list / map budget deferred with review triggers. |
| 2026-11-20 | Licence settled (D-023): GPL-3.0-only + CC BY-4.0 docs + reserved name + CLA. Licence revenue given up in exchange for standard formation. Repository made public. |
| 2026-11-20 | Repository translated to English; coined terms aligned with established vocabulary; later reverted `claim` (see D-025). |
| 2026-11-20 | `claim` restored. Terminology table now requires definition + nearest existing concept + delta for every term (D-025), and the gate rejects any term row without its delta. |
| 2026-11-20 | Confirmed the system is an ABI, not a language (D-026). Derivations live in projections and are trusted by content-addressing the projection's code; the map becomes the catalogue of queryable projections. |
| 2026-11-20 | Implementation settled: Rust core, Python probe, ABI carries no language types (D-027). Agents are external: one ABI + N thin adapters, the seam is the adapter boundary, MCP is an adapter not the ABI, and agent identity as capability token closes the append-authority gap (D-028). |
| 2026-11-20 | Probe written and run (304 lines, Python). Fifteen claims expressed install → rollback → blocked send on one screen; justification chain bottoms out at human/sensor; rollback is pointer-only and byte-identical. Six findings recorded in `probe/README.md`, four of which need rulings. |
