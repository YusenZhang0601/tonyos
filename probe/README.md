# The probe

Three passes. **Its job is to be wrong**, so the design stops being self-validating.

```bash
python3 probe/demo.py
```

`ledger.py` (claims, worlds, viewpoints, ancestry, retraction) · `world.py` (content-addressed files) · `demo.py` (the scenario). State is gitignored.

**Scope, frozen**: install a package → try to send without a signature → get one → send → try again → fork a second world → roll back the first. No real syscalls, no package manager, no concurrency.

## Pass 1 — six findings

No `world` on claims · a projection that assumed "now" reported `installed` after a rollback · `is` drifted into self-contradiction · a blocked `send` left no trace · the first signature signed itself · one file per claim took fifteen claims for three files.

## Pass 2 — the fixes, and what the fix broke

Applied **world scope**, **viewpoint = a root claim**, **commit = one `did` + one root**.

Broke: **time could not advance without the world changing** (the signature written after v1 was invisible at v1 → `tick`), and **an approval never expired**.

Proven: `installed_at(v1) = True`, `installed_at(v3) = False` — same question, two viewpoints, opposite answers, both correct.

## Pass 3 — two worlds, and signatures that can be spent once

```
  1  counts *             {"approves": "bootstrap"}                       ← human authorizes
  2  counts *             {"assumption": true, "integrity": "unmeasured"} ← human says: not measured
  3  is     world:lab     {"root": {"files": {}}}
  4-6 may   *             read allow / write allow / send require
  7  counts *             {"form": "satisfaction", "scope": "pkg:htop"}
  8  did    world:lab     write  → 3 files                              ← one commit, not three
  9  is     world:lab     {"root": {…3 files…}}
 10  did    world:lab     send → denied                                   ← no signature
 11  counts *             {"approves": <send rule>, "target": "mail:advisor"}
 12  is     world:lab     tick (same tree)
 13  did    world:lab     send → done, replaces 11                        ← act and spending are one claim
 14  is     world:lab     tick
 15  did    world:lab     send → denied                                   ← already spent
 16  counts *             {"approves": …, "until": 17}                    ← dead on arrival
 17  did    world:lab     send → denied                                   ← expired
 18  did    world:sandbox write, view = a lab viewpoint                   ← the fork
 19  is     world:sandbox {"root": {…1 file…}}
 20  is     world:sandbox tick
 21  is     world:lab     {"root": {"files": {}}}                         ← rollback, lab only
```

### Verified by running

```
approval one-shot: denied→sent→denied : True
expired approval rejected             : True
fork sees the ancestor's claims       : True
sibling does not see the fork's work  : True
rollback in W1 leaves W2 intact       : True
W1 after rollback is empty            : True
W2 does not see W1's later rollback   : True
global rules visible in both worlds   : True
```

### What pass 3 taught

**A · An approval is spent by using it, and that is one claim, not two.**
The `did` that sends also retracts the signature it consumed. So "who used this signature, and when" is answered by the send itself. A one-shot signature needs no counter — **one signature, one act**. Want two sends? Get two signatures.

**B · Expiry belongs to the ledger, not the clock.**
`until` is a ledger position, not a wall time. A deadline expressed in wall-clock requires trusting a clock, and requirement 5 of the substrate says we do not have one we trust yet. "Valid until sequence 40" is checkable without trusting anything.

**C · Ancestry belongs to the world, not to a viewpoint.**
First implementation walked the fork chain from the viewpoint's own `because`. That works until someone ticks: a tick has no `did`, so the chain ends and **the fork's ancestry silently disappears** — the child world stops seeing its parent's work, and nothing errors. Fixed by deriving origin once per world.

This is the most useful bug of the three, because it fails *quietly*: the screen still rendered, the numbers still looked plausible.

## Still untested

**Concurrency.** Two agents committing to one world at the same time. The probe assumes serial execution; `did.at` is designed as a compare-and-swap precondition but nothing enforces it yet.

**The Screen.** Four projections exist as functions; nothing renders them.

**Everything below the ledger.** It is a Python list of dicts, not a block device, not content-addressed storage, not a booted system.

## Rulings owed

1. Does `tick` deserve its own verb, or is a root claim with an unchanged tree enough?
2. Should `*` (global) be limited to `may`/`counts`, or do sensor facts also belong above worlds?
3. The trust root: only the assumption claim exists (D-033).
