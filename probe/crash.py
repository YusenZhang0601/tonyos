"""E2: what does a crash actually do to the claim log?

Three questions:
  1. Does a torn tail destroy the whole store, or just the tail?
  2. Is content-addressing verified on load, or only claimed?
  3. Does a framed, checksummed log recover a prefix at *every* cut point?

Run: python3 probe/crash.py
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import Ledger, digest          # noqa: E402
from store import frame, recover           # noqa: E402

W = "world:lab"
AGENT = "agent:main"


def claims(n=5):
    return [{"subject": "pkg:htop", "predicate": "is",
             "value": {"file": f"/usr/bin/tool{i}", "note": "x" * 40},
             "world": W, "by": AGENT} for i in range(n)]


def as_jsonl(items):
    return b"".join(json.dumps(c, sort_keys=True).encode() + b"\n" for c in items)


def as_framed(items):
    return b"".join(frame(json.dumps(c, sort_keys=True).encode()) for c in items)


def jsonl_strict(data):
    return [json.loads(line) for line in data.splitlines() if line.strip()]


def jsonl_lenient(data):
    out = []
    for line in data.splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            break
    return out


def framed(data):
    payloads, _ = recover(data)
    return [json.loads(p) for p in payloads]


def part_a_torn_tail():
    print("--- A · what a torn tail does to the current ledger")
    d = tempfile.mkdtemp(dir="/tmp")
    path = os.path.join(d, "claims.jsonl")
    try:
        led = Ledger(path)
        for i in range(5):
            led.append("pkg:htop", "is", {"file": f"/usr/bin/tool{i}"}, W, by=AGENT)
        raw = open(path, "rb").read()
        cut = len(raw) // 2
        open(path, "wb").write(raw[:cut])
        try:
            Ledger(path)
            print("  reload after a mid-line cut : OK (unexpected)")
        except Exception as exc:                      # noqa: BLE001 - we want the type
            print(f"  reload after a mid-line cut : {type(exc).__name__} — the whole store is unreadable")
        blob = as_framed(claims())
        payloads, valid = recover(blob[:len(blob) // 2])
        print(f"  same bytes, lenient reader  : recovered {len(jsonl_lenient(raw[:cut]))} of 5")
        print(f"  same cut, framed log        : recovered {len(payloads)} of 5, stopped at byte {valid}")
        print(f"  fsync in ledger.append      : {'yes' if 'fsync' in open('probe/ledger.py').read() else 'no — a commit is not durable'}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def part_b_every_cut():
    print("\n--- B · cut at every byte offset, 5 records")
    items = claims()
    for name, blob, decode in (("jsonl strict", as_jsonl(items), jsonl_strict),
                               ("jsonl lenient", as_jsonl(items), jsonl_lenient),
                               ("framed+crc", as_framed(items), framed)):
        failures, mismatches = 0, 0
        for cut in range(len(blob) + 1):
            try:
                got = decode(blob[:cut])
            except Exception:                         # noqa: BLE001 - a failure is the result
                failures += 1
                continue
            if got != items[:len(got)] or len(got) > len(items):
                mismatches += 1
        print(f"  {name:<13} cuts={len(blob)+1:>4}  raised={failures:>4}  not-a-prefix={mismatches}")


def part_c_integrity():
    print("\n--- C · flip one byte inside a value, then reload")
    d = tempfile.mkdtemp(dir="/tmp")
    path = os.path.join(d, "claims.jsonl")
    try:
        led = Ledger(path)
        cid = led.append("host", "is", {"arch": "x86_64"}, W, by="sensor:cpu")
        raw = open(path, "rb").read()
        assert b"x86_64" in raw
        open(path, "wb").write(raw.replace(b"x86_64", b"x86_65", 1))
        row = Ledger(path).get(cid)
        content = {k: row[k] for k in ("subject", "predicate", "value", "world",
                                       "by", "because", "replaces")}
        print(f"  stored value                : {row['value']}")
        print(f"  id still matches content    : {digest(content) == row['id']}")
        print("  → content-addressing was claimed, not verified")

        blob = bytearray(as_framed(claims(3)))
        blob[-20] ^= 0x01                             # corrupt inside the last frame
        payloads, valid = recover(bytes(blob))
        print(f"  framed log after corruption : recovered {len(payloads)} of 3, "
              f"valid prefix {valid}/{len(blob)} bytes (taught: the corrupt frame is refused)")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def part_d_overhead():
    items = claims(200)
    j, f = len(as_jsonl(items)), len(as_framed(items))
    print("\n--- D · cost of the frame header, 200 records")
    print(f"  jsonl {j} bytes  /  framed {f} bytes  /  +{100*(f-j)/j:.1f}%  "
          f"({f//200 - j//200} bytes per record)")


if __name__ == "__main__":
    part_a_torn_tail()
    part_b_every_cut()
    part_c_integrity()
    part_d_overhead()
    print("\n--- read this as")
    print("  prefix recovery: both formats can do it with the right reader.")
    print("  integrity: only the checksum can. Without it, a flipped byte is accepted.")
