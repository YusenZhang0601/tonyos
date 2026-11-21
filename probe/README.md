# The probe

Nine passes. **Its job is to be wrong**, so the design stops being self-validating.

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

## Pass 5 — a crash, a torn tail, and a flipped bit

Three questions: does a torn tail destroy the store, is content-addressing
verified, does a framed log recover a prefix at every cut? `python3 probe/crash.py`

```
A · torn tail
  reload after a mid-line cut : JSONDecodeError — the whole store is unreadable
  same bytes, lenient reader  : recovered 2 of 5
  same cut, framed log        : recovered 2 of 5, stopped at byte 368
  fsync in ledger.append      : no — a commit is not durable

B · cut at every byte offset, 5 records
  jsonl strict   cuts= 871  raised= 860  not-a-prefix=0
  jsonl lenient  cuts= 871  raised=   0  not-a-prefix=0
  framed+crc     cuts= 921  raised=   0  not-a-prefix=0

C · flip one byte inside a value, then reload
  stored value                : {'arch': 'x86_65'}
  id still matches content    : False

D · overhead, 200 records: +5.7% (10 bytes each)
```

### What pass 5 taught

**A · The store is not crash-safe, and the format is not the reason.**
`Ledger()` parses every line eagerly, so one torn byte makes the entire ledger
unreadable — not the tail, everything. A lenient reader over the *same bytes*
recovers two of five. **This is a reader-policy bug, not a JSONL bug.**

**B · My prediction was wrong.** I expected a lenient reader to occasionally
accept a truncated line as a valid shorter record. Across every cut offset it
never did: a cut JSON object is either complete or unparseable. The exhaustive
test refuted the hypothesis, so the framing's value is not prefix recovery.

**C · Content-addressing was claimed, not enforced.** A flipped byte changed the
value to `x86_65` while the stored id still named the original. `digest(content)
== id` was false and nothing cared. The checksum is what catches this; the id
alone cannot, because nothing recomputes it.

**D · A commit is not durable.** `append()` never calls `fsync`. Closing a file
is not a durability boundary. A "committed" claim can vanish, and the design
says a vanished claim must mean it never happened — which is only true if
`commit` means "fsync returned".

**E · The checksum is not a signature.** An agent can rewrite a frame and
recompute its CRC. CRC32 protects against accident, not against a writer. That
is the trust root (D-033), and it is still an assumption.

### The contract this produces

1. A claim is committed when the `fsync` covering it returns; before that it may
   vanish, and vanishing means it never happened.
2. Records are framed (`magic | length | crc32`); recovery returns the longest
   prefix of valid frames, truncates the tail, and leaves a trace of the cut.
3. Recovery stops at the first bad frame and reports it. Silently skipping is
   forbidden: a lost tail must be visible.
4. The id is derived from content and asserted on write. Re-verifying identities
   is a scrub, not the normal read path.

### Adopted (D-039)

`Ledger` now frames, fsyncs on append, verifies the checksum on recovery, and cuts
the tail. The same experiment after adoption:

```
reload after a mid-line cut : 2 of 5 recovered, 110 bytes of tail cut
fsync in ledger.append      : yes
one flipped byte            : 0 of 1, the frame failed its checksum
```

The pre-fix lines above are kept: they are the evidence, not the current state.

Still untested: a real power cut (this is a file, not a block device), and
mid-file corruption followed by valid data (resync is a scrub policy, not
decided).

## Pass 6 — two agents, one world

Real processes, one file. Both read the head, then wait, so the race is reachable
on two cores. `python3 probe/concurrent.py`

```
A · no compare-and-swap
  both processes returned a root : True
  roots in world:lab             : 3 (1 seed + 2 commits)
  commits sharing one parent     : 1 parent(s) for 2 commits
  duplicate sequence numbers     : True
  what the screen would show     : 2 heads, silently

B · compare-and-swap, 5 rounds
  exactly one winner per round   : True
  loser forked instead of dying  : True
  fork sees the parent's claims  : True
  fork does not see the winner   : True

C · cost, one world, sequential
  5 commits in 0.32s             : 15.5 commits/s (65 ms each, 2 fsyncs)
```

### What pass 6 taught

**A · None of the three predicted outcomes happened.** I expected one failure,
one overwrite, or two forks. Instead **both returned a root and the world grew two
heads sharing one parent**, with two records at the same position. Nothing failed.
Immutable data cannot be overwritten, and the "fork" was never *declared* — both
roots claimed the same world. A silent split is worse than a visible conflict.

**B · The position counter is part of the race.** Each process computed
`seq = len(rows) + 1` from its own stale snapshot, so two claims got the same
position. Reading the head, assigning the position and advancing the head must be
**one critical section**; they are not three steps.

**C · One winner, and the loser is told.** Under a lock plus a re-check of the
head, exactly one commits per round in 5/5 rounds. The loser gets a `Conflict`,
not a second head.

**D · The loser's exit is a fork, not a retry.** Forking from the head it read
kept both intents: the fork sees the parent's claims and never the winner's. This
is the first evidence for "a fork is concurrency's escape", not just an
experiment tool.

**E · Correctness costs 65 ms per commit** — two `fsync`s, one for the `did` and
one for the root — about 15.5 commits/s per world on this HDD. One `fsync`
covering both frames is enough for the world: an orphan `did` without a root means
"did not happen" (§4.7). Whether a failed attempt must survive a crash is a
policy question, and it costs the second `fsync`.

**F · A reader must not truncate.** Adopting D-039 made every `Ledger()` cut an
invalid tail. A reader opening during a write would cut a frame the writer is
still producing. Readers now open read-only; truncation requires exclusive
access.

### What pass 6 does not test

The race is **forced** (both read, then wait). It proves the schedule is
reachable, not how often it occurs. Cross-node concurrency, and a crash between
the `did` and the root, are still untested.

## Pass 7 — one entry, one fsync, one batch

The write path, closed. Roots can only be written by `commit` / `tick` /
`rollback` / `bootstrap`; `append` refuses a root. The head check, the position
and the write are one critical section inside the store (D-040). Both frames of a
commit share one `fsync`. Group commit is in-process and bounded by a 2 ms window.

Same world, 1.5 s per cell, retries charged to the writer:

```
path     writers  commits   per s   p50 ms   p99 ms  fsync/commit  batch
locked         1       58      39    25.1     40.4          1.00      —
locked         2       38      25    44.6    581.8          1.00      —
locked         4       42      28    38.6   1179.0          1.00      —
locked         8       40      27   172.5   1968.1          1.00      —
group          1       49      33    32.9     42.3          1.02      1.0
group          2      106      71    26.2     43.4          0.51      2.0
group          4      177     118    33.8     55.0          0.26      3.9
group          8      292     195    38.0     78.7          0.16      6.4
group         16      347     231    65.2    244.0          0.11      8.7
group         32      371     247    81.4    709.0          0.11      8.3
```

Window sweep at 8 writers: 2 ms → 166/s, 5 ms → 185/s, 10 ms → 181/s; the batch
moves 6.4 → 7.0 → 7.6. A wider window does not buy much: the writers are the limit.

### What pass 7 taught

**A · The guard is real.** `append` a root → refused. A commit with a bad head →
`Conflict`. Five of five rounds still produce exactly one winner, and the loser
forks (D-040).

**B · One fsync is 2.2x.** 18.8 → 39.4 commits/s. The second fsync was buying
nothing the world needed: an orphan `did` already means "did not happen".

**C · Group commit works, but the batch cannot exceed the writers.** A writer
waits for its own durability before issuing the next commit, so a batch is at
most the number of concurrent writers. `fsync/commit` falls to 0.16 at 8 writers.

**D · The tail improves more than the mean.** Locked at 8 writers: p50 172 ms,
p99 1,968 ms. Group at 8: p50 38 ms, p99 79 ms. Contention was the tail.

**E · The 35x from E1 is not reproduced, and should not be.** E1 measured raw
appends that never waited for durability. A waiting commit is bounded by
`writers / (fsync + window)`. At 16–32 writers the batch plateaus at 8–9 and
throughput at ~250/s: the ceiling is the commit path on two cores in Python, not
the disk. That is exactly the boundary the Rust core exists to move.

### What pass 7 does not test

- **Cross-process group commit.** Two processes cannot share an `fsync` boundary
  without a daemon owning the log.
- **A real power cut.** `fsync` is not a power cut; the file is on ext4.
- **Per-world locking.** The store is one file, so the write lock is per ledger, not
  per world. Sharding the log is untested; the design says contention is per world.
- **Rust.** Every number here is Python on two cores; none of it predicts the core.

## Pass 8 — measure the commit path, then stop re-reading it

The stage's premise was that pass 7's ceiling was the per-commit scan. The
counters said something else, and the difference changed what was worth building.

A. Before any fix (`probe/cost.py`), per commit:

```
path     w   per s   read B  reload  scans   rows  load ms  scan ms  wall ms
locked   1    37.3     2597     1.0    2.0     20     0.43     0.03    26.80
locked   8    18.8   107989     6.0    7.0    479    24.74     1.68    53.06
locked  32     3.2   965582    24.1   25.1   3728   401.08    21.19   309.12
group   32   382.2        0     0.0    2.0    320     0.00     0.33     2.72
```

**Suspect 1 was the ceiling in the locked path** — 24 full re-reads per commit at
32 writers. **Suspect 2 was not**: the head scan was 0.33 ms of a 2.72 ms group
commit. The premise was half wrong, and the counters said which half.

B. `_exclusive` reads only the bytes appended since the last offset. Readers never
truncate; only a writer cuts a tail.

```
locked 32: 3.2 -> 26.6/s; 966 KB -> 12.7 KB per commit; reload 24 -> 0;
           load 401 ms -> 4.3 ms
locked  8: 18.8 -> 32.2/s
group    : unchanged (it never reloaded)
```

C. The head is a per-world index, rebuilt from the log on open. Verified in
`probe/index.py`: 500 mixed operations, 43 worlds, 835 claims, **0 mismatches**
against an independent brute-force head; a fresh `Ledger` on the same log rebuilds
**0 mismatches**; after load, 50 pure commits do **0 scans and read 0 bytes**.

```
locked 32: 26.6 -> 31.5/s; scan 2.28 -> 0 ms
group  32: 368 -> 453/s
group.py 32: pass 7 255/s -> 590-617/s; batch 8.9 -> 21
```

### What pass 8 taught

**A · The scan was cheap and expensive at the same time.** Its direct cost was
0.3 ms. But it ran *under the write lock*, so each writer held the lock while
scanning and only ~9 could enqueue per window. Removing it grew the batch to 21.
The index bought **lock hold time**, not milliseconds.

**B · A premise is not a measurement.** "The per-commit scan is the ceiling" was
true only of the locked path, and even there the reload was 20x larger. Building
the index first would have left the real bottleneck untouched.

**C · The locked path is now fsync-bound.** 27 ms of a 31 ms commit. The group
path at 617/s is bound by the commit path on two cores, not the device.

**D · A pre-existing contradiction surfaced, and was settled.** `active()` said
"retracting a retraction brings the original back", but it was a one-pass cascade:
a retracted by b, b retracted by c, and a stayed dead. Fixing it as written would
revive a spent approval if the `did` that spent it were retracted — one signature,
two sends. **D-041** splits the vocabulary: a `did` is an event and cannot be
retracted; `is` / `may` / `counts` are beliefs and are computed to a fixpoint.
`probe/retract.py` checks four retraction graphs against a **subset oracle** that
enumerates every consistent active set, so it cannot share the implementation's
bug. A spent approval stays spent.

### What pass 8 does not test

- `visible()` still scans every row, and the whole log is in memory. The Screen and
  scale will hit both.
- A real power cut; Rust numbers; cross-process group commit (needs one owner of
  the fsync).

## Pass 9 — the mapping before the pixels

Pass A of stage 3, and **no code**: this is the table `docs/GOAL-screen.md` requires before
`probe/screen.py` may exist. The question is not "what should a panel say" but **which
active claim says it, and what the panel prints when none does**.

The fixture is `probe/demo.py`, unmodified, with its state file redirected to a scratch
directory. The dump is taken at the **final viewpoint** — the head of `world:lab` after the
rollback, `60c2c7cb66e31f05`, seq 22 — because that is what a Screen opened now would be
handed. Every line below is read off that slice, not inferred from the scenario.

```
$ python3 - <<'PY'
import json, os, shutil, sys
sys.path.insert(0, "probe")
import demo
from ledger import Ledger
STATE = "/tmp/opencode/passA/fixture"
shutil.rmtree(STATE, ignore_errors=True); os.makedirs(STATE)
demo.STATE = STATE
demo.main()                                   # the fixture, unmodified
led = Ledger(os.path.join(STATE, "claims.jsonl"), writable=False)
vp = led.current_root("world:lab")            # the final viewpoint
s = led.visible(vp)
print(f"final viewpoint: world:lab @ seq {led.seq_of(vp)}  id={vp}  slice={len(s)} claims")
for c in s:
    print(f"{c['seq']:>2} {c['predicate']:<6} {c['world']:<14} {c['subject']:<11} "
          f"{json.dumps(c['value'], sort_keys=True, ensure_ascii=False)}  {c['id']}")
print("require rule      :", [(c['id'], c['value']) for c in s if c['predicate']=='may' and c['value']['mode']=='require'])
print("approvals in slice:", [(c['seq'], c['id'], c['value']) for c in s if c['predicate']=='counts' and 'approves' in c['value']])
print("demo.what_it_needs:", demo.what_it_needs(s))
print("denied sends      :", [c['seq'] for c in s if c['predicate']=='did' and c['value'].get('outcome')=='denied'])
print("non-root is       :", [c['seq'] for c in s if c['predicate']=='is' and 'root' not in c['value']])
print("identity counts   :", [c['seq'] for c in s if c['predicate']=='counts' and c['value'].get('form')=='identity'])
print("subject human:*   :", [(c['seq'], c['by']) for c in s if c['subject'].startswith('human:')])
PY
--- (the fixture's own output, 8/8 verification, omitted here) ---
final viewpoint: world:lab @ seq 22  id=60c2c7cb66e31f05  slice=17 claims
 1 counts *              human:tony  {"approves": "bootstrap", "form": "representation", "scope": "first installation"}  2723f36d08ba1da7
 2 counts *              machine     {"assumption": true, "form": "satisfaction", "integrity": "unmeasured"}  f30a5942374fcad5
 3 is     world:lab      world       {"root": {"files": {}}}  dc63162abc565057
 4 may    *              agent:main  {"mode": "allow", "verb": "read"}  3f9bd4d7d98c7a71
 5 may    *              agent:main  {"mode": "allow", "verb": "write"}  f7946ffb299481d5
 6 may    *              agent:main  {"mode": "require", "verb": "send"}  963bba95a1590350
 7 counts *              human:tony  {"form": "satisfaction", "scope": "pkg:htop", "test": "every file present, bytes identical"}  f41d847dd8e2c53e
 8 did    world:lab      agent:main  {"result": {"files": {"/etc/htoprc": "fields=1", "/usr/bin/htop": "ELF"}}, "verb": "write", "view": "dc63162abc565057"}  98971c4816f68358
 9 is     world:lab      world       {"root": {"files": {"/etc/htoprc": "fields=1", "/usr/bin/htop": "ELF"}}}  d85b8684d801a245
10 did    world:lab      agent:main  {"outcome": "denied", "target": "mail:advisor", "verb": "send", "view": "d85b8684d801a245"}  21576b045f1934af
12 is     world:lab      world       {"root": {"files": {"/etc/htoprc": "fields=1", "/usr/bin/htop": "ELF"}}}  9099074bce5486dc
13 did    world:lab      agent:main  {"outcome": "done", "result": "sent", "target": "mail:advisor", "verb": "send", "view": "9099074bce5486dc"}  94f42dff95ee9a36
14 is     world:lab      world       {"root": {"files": {"/etc/htoprc": "fields=1", "/usr/bin/htop": "ELF"}}}  7b335c651543bc07
15 did    world:lab      agent:main  {"outcome": "denied", "target": "mail:advisor", "verb": "send", "view": "7b335c651543bc07"}  3f3e9f5d641b366e
16 counts *              human:tony  {"approves": "963bba95a1590350", "form": "representation", "target": "mail:advisor", "until": 15}  88c2b9ceb588f3dc
18 did    world:lab      agent:main  {"outcome": "denied", "target": "mail:advisor", "verb": "send", "view": "3c53ec540d80f7c5"}  38f5db219639e1a5
22 is     world:lab      world       {"root": {"files": {}}}  60c2c7cb66e31f05

require rule      : [('963bba95a1590350', {'mode': 'require', 'verb': 'send'})]
approvals in slice: [(1, '2723f36d08ba1da7', {'approves': 'bootstrap', 'form': 'representation', 'scope': 'first installation'}), (16, '88c2b9ceb588f3dc', {'approves': '963bba95a1590350', 'form': 'representation', 'target': 'mail:advisor', 'until': 15})]
demo.what_it_needs: []
denied sends      : [10, 15, 18]
non-root is       : []
identity counts   : []
subject human:*   : [(1, 'human:tony'), (7, 'human:tony'), (16, 'human:tony')]
```

### The four panels, line by line

"Absent" is what the line prints when no claim supplies it. Claim ids are abbreviated to
the sequence number; the full id is in the dump above.

| # | line (FOUNDATION §6) | predicate | the active claim that supplies it, at seq 22 | printed when absent |
|---|---|---|---|---|
| 1.1 | the work site: which world, where in it, how big | `is` root | seq 22 itself — `{"root": {"files": {}}}`, `world:lab`, 0 files; `world` and `seq` are fields of that claim | `—` (0 roots) |
| 1.2 | how far: the declared check, and whether it passes | `counts` satisfaction | seq 7 names the criterion (`scope pkg:htop`, `test "every file present, bytes identical"`). **No claim states the result** | `—` (0 tests); with a test present the result is still not a claim — **gap G1** |
| 1.3 | the last thing that happened | `did` | seq 18 — `send`, `target mail:advisor`, `outcome denied` | `—` (0 events) |
| 1.4 | where it is stuck | `did` | seq 10, 15, 18 — three `send → denied`; 3 of 4 sends blocked, the last at 18 | `—` (0 denials) |
| 1.5 | the pointer moved after the last event | `is` root | seq 22 `replaces` the seq-17 root and `because` points back to seq 3; no `did` follows seq 18 | `—` (0 roots); the *kind* of root is not a claim — **gap G4** |
| 2.1 | the rule that needs you | `may require` | seq 6 — `subject agent:main`, `verb send`, `mode require`, world `*`, active | `—` (0 require) |
| 2.2 | the act actually waiting, and its target | `did` + `may` | seq 18 (`send → denied`, `mail:advisor`) joined to seq 6 | `—` (0 blocked acts) |
| 2.3 | is it unsatisfied **now** | `counts` | no usable approval for seq 6: seq 16 approves it but carries `until: 15` while sitting at 16, so `spendable()` returns nothing; the spent approval (seq 11) is not in the slice | `0 usable`; read as `demo.what_it_needs` reads it, `—` (satisfied) — **gap G2** |
| 3.1 | who it is: identity | `counts` identity | none in the slice. The form exists (FOUNDATION §1.1), the fixture has 0 instances | `—` (0 identity claims) — empty, not a gap |
| 3.2 | what it has | `may allow` + `is` root | seq 4 read allow, seq 5 write allow; seq 22 tree = 0 files | `—` (0 allow, 0 files) |
| 3.3 | what it is holding | `counts` representation | seq 16 is active and unspent but expired at this position → 0 usable, 1 held-and-dead. The **spent** one (seq 11) is in no slice at all | `—` (0 approvals); "already spent" is unavailable — **gap G3** |
| 3.4 | what it intends | — | nothing. No claim, and no shape: the four predicates record what is, did, may, counts — none is a future act | `—` (0) — **gap G5** |
| 4.1 | its observations about the human | — | nothing. Three claims carry `subject human:tony` (1, 7, 16) and all three are the human's own acts — two approvals and one definition. Zero agent-authored observations | `—` (0) — **gap G6**, a ruling |

**13 lines: 6 are supplied by an active claim with no further definition** (1.1, 1.3, 1.4,
2.1, 2.2, 3.2); **1 is empty but correctly empty** (3.1); **1 is half-supplied** (3.3 — the
unspent half works, the spent half cannot be shown); **5 have no claim behind them** (1.2,
1.5, 2.3, 3.4, 4.1), which produce **six gaps**. Per panel: 3 of 5 / 2 of 3 / 1 of 4 / 0 of 1.

### The gaps

**G1 · "how far" has a criterion but no result.**
Seq 7's `test` is English prose; `installed_at()` in `demo.py` hardcodes `MANIFEST` to
evaluate it. Two projections can disagree and both be "right", and a check hardcoded in the
Screen is exactly the hidden query the goal file forbids.
*Smallest closing claim*: a `counts` satisfaction that **is** the verdict, tied to a root —
`{form: satisfaction, scope: pkg:htop, of: <seq 7>, at: <root id>, result: false}` with
`because=[root, test]`, written by whoever ran the check. Tying it to a root id is D-034's
expiry pattern: a verdict must go stale when the world moves.

**G2 · "unsatisfied require" has no definition, and the fixture gives two answers.**
At seq 22 the slice contains both `send → denied` (seq 18) and `what_it_needs(slice) == []`.
The demo counts any active `counts` with `approves == rule.id` as satisfaction, ignoring
`target` and `until`; `spendable()` honours both. So the Screen would print "nothing needed"
next to "stuck: send denied".
*Smallest closing claim*: none — this is a definition. Either "satisfied" means *an
approval `spendable()` would return* (one predicate shared by the hand and the Screen), or
the authorisation is itself a claim. The first needs no new vocabulary and no new claim;
it needs the Screen to use the hand's rule. Raised, not chosen.

**G3 · a spent approval can be shown in no slice.**
Seq 11 (`f2b182b292d913e7`) is retracted by seq 13, and `visible()` filters on the final
`active()` set, so seq 11 is in **no** viewpoint's slice. The panel can say "holding 0"; it
can never say "you signed one, and it was used at 13" — which is the answer to the question
a human actually asks when the agent is stuck.
*Smallest closing claim*: none. Either the panel gets a slice that includes retracted
claims (contradicting "one slice"), or the Screen is a work site and the audit trail stays
elsewhere. `docs/GOAL-screen.md` already defers "retracted history on a panel"; this is its
concrete case. Raise.

**G4 · a root has no kind, and an act by the human leaves no event.**
All five roots in the slice have `subject: "world"`. Seq 22 is a rollback only because it
carries `replaces=[<seq-17 root>]` and `because=[<seq-3 root>]`. Its `by` is `human:tony`,
yet `did` by a human in the slice is `[]`: the human moved the world and the event list has
no entry for it.
*Smallest closing claim*: a `did` for the pointer move —
`{verb: write, target: world:lab, result: {rollback_to: <v0>}}` by `human:tony`. But D-032
made a commit one `did` + one root and left `tick` / `rollback` root-only; adding a `did`
changes the event model. The alternative is that the Screen classifies roots by shape and
prints "pointer moved" — deterministic, but the wording is the projection's invention.
Raise.

**G5 · "what it intends" has no claim shape.**
`did` is past, `may` is a rule the human set, `counts` is a definition, `is` is what the
world is. Nothing records a future act, and FOUNDATION never says `is` may carry one.
*Smallest closing claim*: an `is` claim, subject `agent:main`, in a concrete world (D-030
forbids `*` for `is`), value `{"intends": …}`, `because=[…]`. Two objections before anyone
writes it: it is unverified self-report, and FOUNDATION §6 asks who vouches for the
self-report; and `counts` cannot carry it, because `counts` is human-written and the agent
may only propose. So either the line is dropped from panel 3, or a self-report is admitted
as a claim the agent may write and the Screen labels as self-reported. A decision.

**G6 · panel 4 has no claim shape, and the obvious shape collides with D-030.**
Zero agent-authored claims about the human. The shape that would be needed, stated
precisely: `is`, subject `human:tony`, concrete world (D-030: `is` may not be `*`), by
`agent:main`, value = the observation, `because=[the did that observed it]`. Consequences
that need a ruling, in order: (a) world-scoped, so the same person is observed separately
in `world:lab` and `world:sandbox` — is a per-world belief about a person acceptable?
(b) `counts` cannot carry it, since an agent may not stipulate what its own observation
counts as; (c) `did read` records that it looked, not what it concluded, so the observation
still needs `is`; (d) whether the ledger holds beliefs about a person at all is the privacy
ruling the goal file already defers. Recorded, not decided — and not implemented.

### Two defects in the slice itself

Both were found by asking every root to render itself; neither is patched.

**S1 · `*` claims ignore the viewpoint's position.** `visible()` keeps every active global
claim regardless of the viewpoint's `seq`, so a viewpoint does not pin the moment for
`may` / `counts`. At seq 3 the slice already contains seq 4–7 and seq 16: the read and write
permissions and an approval that did not exist yet. Panel 3 at the seed viewpoint would
report "it has read allow, write allow" about a moment when the human had granted nothing.

```
$ python3 - <<'PY'
import sys; sys.path.insert(0, "probe")
from ledger import Ledger
led = Ledger("/tmp/opencode/passA/fixture/claims.jsonl", writable=False)
roots = [r for r in led.rows if r["predicate"] == "is" and "root" in r["value"]]
for r in roots:
    s = led.visible(r["id"])
    print(f"  {r['world']:<14} vp seq={r['seq']:>2}  rows={len(s):>2}  "
          f"self_in_slice={r['id'] in {c['id'] for c in s}}  "
          f"claims_after_vp={[c['seq'] for c in s if c['seq'] > r['seq']]}")
print("spent approval seq 11 in any slice?",
      any(11 in [c["seq"] for c in led.visible(r["id"])] for r in roots))
PY
  world:lab      vp seq= 3  rows= 8  self_in_slice=True  claims_after_vp=[4, 5, 6, 7, 16]
  world:lab      vp seq= 9  rows=10  self_in_slice=True  claims_after_vp=[16]
  world:lab      vp seq=12  rows=12  self_in_slice=True  claims_after_vp=[16]
  world:lab      vp seq=14  rows=14  self_in_slice=True  claims_after_vp=[16]
  world:lab      vp seq=17  rows=15  self_in_slice=False claims_after_vp=[]
  world:sandbox  vp seq=20  rows=12  self_in_slice=True  claims_after_vp=[]
  world:sandbox  vp seq=21  rows=13  self_in_slice=True  claims_after_vp=[]
  world:lab      vp seq=22  rows=17  self_in_slice=True  claims_after_vp=[]
spent approval seq 11 in any slice? False
```

**S2 · a retracted viewpoint is not in its own slice.** The seq-17 root is retracted by the
rollback, so `visible(<seq 17>)` does not contain the claim that names the viewpoint — line
1.1 has no supplier, and a historical screenshot cannot be reproduced. Cause: activity is
the final fixpoint, not activity as of the viewpoint's position.

S1 and S2 are the same question seen twice: **what does a viewpoint pin?** D-031 says "the
branch, the moment and the tree". For `*` it pins the branch and the tree; for retracted
claims it pins neither the moment nor itself. Reported with reproduction; not patched.

### What pass 9 taught

**A · The vocabulary describes a world and its rules, and has almost nothing to say about
the agent.** 6 of 13 lines resolve outright — all six are about the world (tree, events,
rules, denials). The two panels that describe the *agent* are the two that fail: "who it
is" has no identity claim and no intention shape, and "how it sees you" has no claim at
all. That is not a rendering problem, which is the thing this pass existed to find out.

**B · The fixture contradicts itself on panel 2, and the contradiction is in a definition,
not in a claim.** Three denied sends and `needs=[]`, from the same slice. `what_it_needs`
is the closest thing to a panel implementation that exists, and it is wrong in a way that
looks confident: "nothing needed" beside "stuck: send denied".

**C · A viewpoint does not pin the moment for global claims.** Five claims written after
the viewpoint appear in its slice, including the permissions. Any header reading
"world:lab @ 3" sits above a panel that is lying, and nothing errors. This is the same
class of failure as pass 3's silent ancestry bug: the screen renders and the numbers look
plausible.

**D · "How far" needs a verdict claim, not a criterion claim.** A prose test cannot be
evaluated by a projection, so the probe's own projection hardcodes the check. Either the
test is machine-checkable or the result is a claim — and if it is a claim, it must be tied
to a root, or it survives a rollback that should have invalidated it.

**E · The four panels survive as a layout, not yet as a handoff packet.** The layout holds:
four questions, 13 lines, six supplied, and the panels are not arbitrary — every line that
resolves does so from one claim without interpretation. But a new brain reading the final
viewpoint would learn the tree, the rules, the events and the block, and would not learn
who it is, what it is trying to do, or anything about the person it serves. The three
questions that fail are the three that make it a *brain* rather than a work log.

### What pass 9 does not test

- **The line set is the author's.** The brief names four headings and six sub-phrases, not
  13 lines. A different decomposition moves the gap count; it does not move S1 or S2.
- **One fixture, one viewpoint for the reading.** Every root in the fixture was checked for
  slice self-consistency (S1, S2); the line-by-line table is read at the final viewpoint
  only. Panel lines at other viewpoints (0 events at seq 3, no sends at seq 9) were checked
  for presence, not for readability.
- **Nothing is rendered, measured, or timed.** Passes B and C remain unstarted by design.

## Still untested

**The Screen.** Four projections exist as functions; nothing renders them. Pass 9 is the
map they would have to be built from: thirteen lines, six supplied, six gaps behind five of
them.

**Everything below the ledger.** A Python list of dicts is not a block device, not
content-addressed storage, not a booted system.

## Rulings owed

1. Does `tick` deserve its own verb, or is a root claim with an unchanged tree enough?
2. Should `*` (global) be limited to `may`/`counts`, or do sensor facts also belong above worlds?
3. The trust root: only the assumption claim exists (D-033).
4. Repeated identical `did`s collapse into one event (D-038). Is "it looked twice" information the ledger must keep?
5. Where does a conflict get recorded? `did` cannot be global, and the world it
   failed to advance is exactly the one it must not write to.
6. Must a failed attempt survive a crash? It costs a second `fsync` (D-040).
7. Is "unsatisfied `require`" a computed predicate over (rule, approval, target,
   position), or a claim? The fixture gives two answers from one slice (pass 9, G2).
8. Is a pointer move an action? `tick` / `rollback` write a root and no `did`, so the
   event list has no entry for a rollback the human performed (pass 9, G4).
9. May `is` carry an intention, and is a self-report a claim the agent may write?
   Panel 3 asks for "what it intends" and the vocabulary has no shape for it (pass 9, G5).
