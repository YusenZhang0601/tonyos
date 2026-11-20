# TonyOS

> An agent-native minimal operating system: **the agent is the owner, the human is the constitution.**

Not "a desktop with an AI installed". An attempt to start over from first principles: if the subject of a machine is an agent, then processes, files, permissions, logs and the screen should all be redefined from scratch.

## What this is

**Design stage. There is no code yet.**

What is already settled matters more than code:

- **Four predicates** — `is` / `did` / `may` / `counts`. That is the entire vocabulary of the system; everything else is a projection.
- **No-go zones** — not a sandbox allowlist. The human draws a ring; inside it requires approval; outside it is allowed by default.
- **The axiom of reversibility** — there is no "modify", only "a new version plus a pointer swap". Undo and restore are words that should not exist.
- **Default: don't load** — history is a library, not the air. Nothing may enter the agent's context on its own.

The full derivation is in [`design/FOUNDATION.md`](design/FOUNDATION.md). Every tradeoff — and every conclusion that was later overturned — is on record in [`docs/DECISIONS.md`](docs/DECISIONS.md).

## Why it is public

If this is worth existing, it should become the **reference** that others are measured against. Charging for it would prevent exactly that.

Code is GPL-3.0: free for commercial use, but modifications must be published — nobody can take it into a closed fork and split the ecosystem.
Documentation is CC BY-4.0: take the ideas, just credit them.
The name is reserved (see [`TRADEMARK.md`](TRADEMARK.md)): the code is free, the name is not.

Details in [`LICENSING.md`](LICENSING.md).

## Where to start

If you have five minutes:

1. [`design/FOUNDATION.md`](design/FOUNDATION.md) — section 1 (the four predicates) and section 3 (no-go zones)
2. [`docs/STATUS.md`](docs/STATUS.md) — where things stand

If you want to contribute: read [`CLA.md`](CLA.md) first.

## The testbed

This project grows on a real machine: a 700 GB data partition, a rescue host, and two empty experiment slots — so the system can be broken and rolled back at will.
Machine facts are in [`README.txt`](README.txt).

## License

| Subject | License |
|---|---|
| Code | GPL-3.0-only |
| Documentation | CC BY-4.0 |
| The name "TonyOS" | Reserved |
