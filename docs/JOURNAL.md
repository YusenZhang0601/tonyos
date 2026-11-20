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
| 2026-11-20 | First market sweep, recorded in `docs/COMPETITORS.md` as a quarterly side track. Verdict: the combination is unclaimed, every constituent part is taken; only "agent is the owner" and human-only `counts` are unclaimed. Nearest neighbours: Decima, AgentKernel, Microsoft MXC. |
| 2026-11-20 | Sweep made repeatable: `tools/market.sh` (8 saved queries + 13 watched repos, TSV, diffable, exit 1 on any gap). Clean baseline run: 0 errors; counts corrected to one source. |
| 2026-11-20 | Working agreement recorded (D-029, hard rule 7): a completion claim without evidence is a proposal. Prompted by the owner naming the vibe-coding failure mode; three near-misses in this session documented in the entry. |
| 2026-11-20 | Probe second pass: world scope, viewpoint-as-root-claim, commit-as-transition (D-030…D-032). Approval flow verified end to end: denied → signed → sent; rollback moved a pointer and deleted nothing. Two new findings: time cannot advance without the world changing (`tick`), and an approval never expires. |\n| 2026-11-20 | Probe pass three: two worlds and one-shot signatures (D-034, D-035). Eight verifications pass, including fork inheritance, sibling isolation and a parent-only rollback. Found that ancestry derived per-viewpoint disappears after any tick — ancestry belongs to the world. |\n