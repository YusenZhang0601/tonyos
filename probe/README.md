# The probe

Two passes so far. **Its job is to be wrong**, so the design stops being self-validating.

```bash
python3 probe/demo.py
```

Three files: `ledger.py` (claims, worlds, viewpoints, retraction), `world.py` (content-addressed files), `demo.py` (the scenario). State goes to `probe/world/`, gitignored.

**Scope, frozen**: install a package into a fake world → attempt a `send` with no signature → get a signature → send → roll back. No real syscalls, no package manager, no concurrency, **no second world**.

## First pass: six findings

1. A claim had no `world` — history from different branches was indistinguishable.
2. A projection that assumes "now" answered `installed` **after the rollback**.
3. `is` drifted into self-contradiction (`installed` + `proved: false`) without a shape rule.
4. A blocked `send` left **no trace** unless failure is a `did` with an `outcome`.
5. The first signature signed itself — a circle where a root should be.
6. One file, one claim: three files took fifteen claims.

## Second pass: the fixes, and what the fix broke

Applied: **world on every claim** (norms may be `*`, facts may not) · **viewpoint = a root claim** · **a commit is one `did` + one root**, with "where it came from" recorded once.

```
  1  counts *        human:tony  {"form": "representation", "approves": "bootstrap"}
  2  counts *        machine     {"form": "satisfaction", "assumption": true, "integrity": "unmeasured"}
  3  is     world    host        {"arch": "x86_64"}
  4  is     world    world       {"root": {"files": {}}}
  5  may    *        agent:main  {"mode": "allow", "verb": "read"}
  6  may    *        agent:main  {"mode": "allow", "verb": "write"}
  7  may    *        agent:main  {"mode": "require", "verb": "send"}
  8  counts *        human:tony  {"form": "satisfaction", "scope": "pkg:htop", ...}
  9  did    world    agent:main  {"verb": "read", "target": "/usr/share/doc", "view": …}
 10  did    world    agent:main  {"verb": "write", "result": {"files": {...}}, "view": …}
 11  is     world    world       {"root": {"files": {…3 files…}}}
 12  is     world    pkg:htop    {"installed": true, "at": …}          ← projection
 13  did    world    agent:main  {"verb": "send", "outcome": "denied"}  ← red line held
 14  counts *        human:tony  {"form": "representation", "approves": …}
 15  is     world    world       {"root": {…same files…}}               ← tick
 16  did    world    agent:main  {"verb": "send", "outcome": "done"}
 17  is     world    human:tony  {"root": {"files": {}}}                ← rollback
```

Sixteen claims after the bootstrap, one screen.

### What is now proven

- **The same question, two viewpoints, two opposite answers, both correct.**
  `installed_at(v1) = True`, `installed_at(v3) = False`. The projection cannot lie about "now" because there is no "now" to lie about — and it never sees the ledger, only a slice.
- **One commit for three files, and for three hundred.** Files never enter the ledger.
- **The red line held, then yielded to a signature**: `denied` at v1, `done` at v2, and the `done` claim carries the approval in its `because`.
- **Rollback moved a pointer and deleted nothing.** All claims remain; history is not rewritten.

### What the second pass broke

**A · Time cannot advance without the world changing.**
A viewpoint is a root claim, so it only moves when a claim is written. But the approval was written *after* v1 — and v1 could not see it. The second `send` was blocked for a reason no one intended: **the viewpoint had no way to say "same world, later moment"**. Fixed with a `tick`: a root claim asserting the same tree. A viewpoint is a position in time as much as in space, and the model had only given it a position in space.

**B · An approval never expires.**
One signature made `send` permanently allowed: at v3 the screen shows `needs=[]`. Nothing in the vocabulary bounds an approval — no scope, no count, no deadline. **A single signature is currently a permanent one.** This is a finding, not yet fixed.

**C · Every root stays active forever.**
`current` means "the newest active root", not "the only one". Old roots are not retracted (correct — they are history), but this means any code that asks "what is the world" must ask for *newest*, never *the*. A wording trap waiting for the first careless implementation.

## Rulings still owed

1. Should an approval carry a scope and a lifetime (one-shot, N uses, TTL)? (finding B)
2. Does `tick` need its own verb, or is a root claim with an unchanged tree enough? (finding A)
3. The trust root: still assumed, written down as an assumption (claim 2). Deferred with a trigger.

## What this probe still does not test

**A second world.** No forking, no two agents, no concurrency. Everything here is single-branch, and the whole point of the design is multi-branch. This is the largest untested surface, and saying otherwise would be exactly the failure this project is trying to avoid.
