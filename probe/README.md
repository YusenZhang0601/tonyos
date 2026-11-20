# The probe

One day of work, deliberately crude. **Its job is to be wrong**, so the design stops being self-validating.

```bash
python3 probe/demo.py
```

Three files: `ledger.py` (claims, retraction, justification chains), `world.py` (content-addressed blobs behind a root pointer), `demo.py` (the scenario and two projections). State goes to `probe/world/`, which is gitignored.

**Scope, frozen**: install a package into a fake world → advance the reference → roll it back → attempt a `send` with no signature. No real syscalls, no package manager, no concurrency, no adapters, no UI.

## The ledger, in full

```
  1  counts human:tony    human:tony   {"approves": "self", "form": "representation", "scope": "initial trust"}
  2  is     host          sensor:cpu   {"arch": "x86_64"}
  3  is     world         sensor:fs    {"root": "4faa3e5f1e76b5e9"}
  4  may    agent:main    human:tony   {"mode": "allow", "verb": "read"}
  5  may    agent:main    human:tony   {"mode": "allow", "verb": "write"}
  6  may    agent:main    human:tony   {"mode": "require", "verb": "send"}
  7  counts human:tony    human:tony   {"form": "satisfaction", "scope": "pkg:htop", "test": "all files present and byte-identical"}
  8  did    agent:main    agent:main   {"outcome": "done", "target": "etc/manifest", "verb": "read", "world": "4faa…"}
  9  did    agent:main    agent:main   {"outcome": "done", "target": "/usr/bin/htop", "verb": "write", "world": "81fb…"}
 10  did    agent:main    agent:main   {"outcome": "done", "target": "/etc/htoprc", "verb": "write", "world": "ca92…"}
 11  did    agent:main    agent:main   {"outcome": "done", "target": "/usr/share/doc/htop", "verb": "write", "world": "43fd…"}
 12  is     world         sensor:fs    {"root": "43fd…"}                                   [retracted]
 13  is     pkg:htop      projection:1a64d2514c345c7d  {"status": "installed", "world": "43fd…"}
 14  did    agent:main    agent:main   {"outcome": "denied", "target": "mail:advisor", "verb": "send", "why": "mode=require"}
 15  is     world         human:tony   {"root": "4faa…"}
```

Fifteen claims. **It fits on one screen.** That is the vocabulary's first real evidence.

## What survived

- **Four predicates were enough.** Nothing needed a fifth. Intent, approval, success and rollback all landed.
- **The justification chain bottoms out where it should**: at a human signature and a sensor reading. `derivation roots: ['human']`.
- **Rollback was pointer-only and byte-identical.** Nothing was undone, nothing was copied; the world was simply no longer referenced. "Undo" and "restore" never appeared.

## What broke

### 1. A claim has no scope — and it needs one

`did` records `world`, but only because the probe put it in `value`. A derived `is` claim does the same. Both are really saying *which world this is about*, and that belongs in the record, not in the value:

```
claim { subject, predicate, value, world, by, at, because, replaces }
```

**Needs a ruling.** Without it, claims from different branches are indistinguishable.

### 2. A projection that assumes "now" is wrong

First implementation of `what_its_doing(ledger)` read "the current status" and answered `installed` **after the world had been rolled back**. The bug is not the bug; the lesson is that the design's "there is no global now" is only real if the projection API forces a world argument. Fixed here by taking the root explicitly; the constraint must become a rule, not a habit.

### 3. `is` needs a shape: one attribute per claim

The first run mixed `{"field": …, "value": …}` with `{"status": …}` and immediately drifted into a self-contradicting value: `{"status": "installed", "proved": false}`. One claim, one attribute — the contradiction becomes impossible to write.

### 4. Failure is also a `did`, and the ledger must say which kind

A denied `send` is recorded as `outcome: "denied"`. Without that, a blocked red line leaves **no trace** — and a blocked red line is exactly what an audit needs to see. Outcome must be part of the vocabulary, not an afterthought.

### 5. The first signature signs itself

`{"approves": "self"}` is the bootstrap: the root of trust is a signature approving itself. The probe stepped over it. A real system cannot — this is where the measured boot chain has to come in, and where "assumption" must be written as an assumption.

### 6. One file, one claim — it will not scale

Three files took fifteen claims. A real package has hundreds. Per-file `did` will explode the ledger and make the one-screen map impossible.

**Needs a ruling**: a batch form (one `did` over a manifest, or a `did` whose subject is a tree). Note this is exactly the kind of thing a language would have solved, and we chose not to have one — so it has to be solved in the vocabulary.

## Rulings this probe asks for

1. Add a `world` scope to every claim (finding 1).
2. Make the world an explicit argument of every projection, enforced by the API (finding 2).
3. Define a batch/aggregate form for `did` (finding 6).
4. Decide how the first signature is grounded (finding 5).

Findings 3 and 4 were cheap and are already applied in the probe.
