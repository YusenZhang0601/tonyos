# The probe

Four passes. **Its job is to be wrong**, so the design stops being self-validating.

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

## Pass 4 — identity and the throughput ceiling

Two experiments, both runnable: `python3 probe/throughput.py`.

**Identity (D-038).** The id used to be hashed over `seq` and `ts`, so the same
claim on two nodes got two names. Now it covers content only:

```
node A id          : bff767701169e01e
node B id          : bff767701169e01e
same across nodes  : True
re-assert collapses: True (duplicates=1)
```

Collapsing is a consequence, not yet a ruling: two identical `did`s become one event.

**Throughput (D-037).** Four layouts, 1 / 2 / 4 / 8 writers, fsync per commit
unless stated. This machine's disk is a **spinning HDD** (WD10EZEX, ROTA=1), so
the absolute numbers are HDD numbers; the shape is the point.

```
layout         writers    ops/sec   mean ms   p99 ms
shared+fsync         1         38     26.20    68.42
shared+fsync         8        102     82.77   160.37
shard+fsync          1         32     32.00    75.14
shard+fsync          8        113     71.09   158.41
group                1       1398      0.71     3.09
group                8       3586      2.23     9.02
nofsync              1      22980      0.04     0.15
nofsync              8      22498      0.35    11.27
```

### What pass 4 taught

**A · Sharding the log bought nothing.** 102/s shared vs 113/s sharded at eight
writers — noise. The shared file was not the ceiling; **the device was**. The
global `seq` suspicion (D-037's first consequence) is not supported at the I/O
layer. This is a hypothesis the measurement killed, not one it confirmed.

**B · fsync is the ceiling, by 35x.** 3,586/s with group commit against 102/s
per-commit. D-037's prediction that throughput-first implies group commit held.

**C · The predicted tradeoff did not appear.** Group commit was supposed to spend
latency. At this load it improved both mean and tail: 0.68 ms / 3.0 ms at one
writer, 2.25 / 8.5 at eight, against 26–160 ms per-commit. The tradeoff exists in
principle — waiting for a 5 ms window — but the measured regime never entered it.

**D · The software ceiling is not visible here.** `nofsync` flattens at ~23k/s:
that is Python and the GIL, not the device. This experiment cannot say how a Rust
core would scale.

### What pass 4 does not test

The raw append path only. It bypassed `Ledger`: no CAS, no visibility scan, no
world semantics. **Two agents committing to one world is still untested.**

fsync is not a power cut; the file is on ext4, not a raw device.

## Still untested

**Concurrency semantics.** Two agents committing to one world. `did.at` is
designed as a compare-and-swap precondition but nothing enforces it.

**The Screen.** Four projections exist as functions; nothing renders them.

**Everything below the ledger.** A Python list of dicts is not a block device, not
content-addressed storage, not a booted system.

## Rulings owed

1. Does `tick` deserve its own verb, or is a root claim with an unchanged tree enough?
2. Should `*` (global) be limited to `may`/`counts`, or do sensor facts also belong above worlds?
3. The trust root: only the assumption claim exists (D-033).
4. Repeated identical `did`s collapse into one event (D-038). Is "it looked twice" information the ledger must keep?
