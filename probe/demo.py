"""Probe, third pass: two worlds, and signatures that can only be spent once.

Run: python3 probe/demo.py
"""
import inspect
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import Ledger, digest          # noqa: E402

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world")
AGENT = "agent:main"
HUMAN = "human:tony"
W1, W2 = "world:lab", "world:sandbox"
PKG = "pkg:htop"
MANIFEST = {"/usr/bin/htop": "ELF", "/etc/htoprc": "fields=1"}


def code_hash(fn):
    return digest(inspect.getsource(fn).encode())


# ---------------------------------------------------------------- projections
# They receive a slice, never the ledger (D-031).
def tree_of(slice_):
    return [c for c in slice_ if c["predicate"] == "is" and "root" in c["value"]][-1]["value"]["root"]


def installed_at(slice_, manifest=MANIFEST):
    files = tree_of(slice_).get("files", {})
    return all(files.get(p) == b for p, b in manifest.items())


def what_its_doing(slice_):
    return {"installed": installed_at(slice_),
            "writes": sum(1 for c in slice_ if c["predicate"] == "did" and c["value"]["verb"] == "write")}


def what_it_needs(slice_):
    """Unsatisfied `require` rules, judged from the slice alone."""
    out = []
    for c in slice_:
        if c["predicate"] != "may" or c["value"]["mode"] != "require":
            continue
        if not any(a["predicate"] == "counts" and a["value"].get("approves") == c["id"] for a in slice_):
            out.append(c["value"]["verb"])
    return out


# ------------------------------------------------------------------- the hand
def commit(ledger, world, files, by, because, view=None):
    """One transition = one did + one root. Forking is the same call with a view
    that points into another world. The head check lives in the ledger (D-040)."""
    expect = view or ledger.current_root(world)
    return ledger.commit(world, files, by, expect, because=list(because))


def tick(ledger, world, by):
    """Advance time without changing the world."""
    return ledger.tick(world, by, ledger.current_root(world))


def spendable(ledger, slice_, rule, target):
    """An approval is one-shot and may carry a deadline expressed in ledger
    positions, not wall-clock: expiry must not depend on trusting a clock."""
    for c in slice_:
        if c["predicate"] != "counts" or c["value"].get("approves") != rule["id"]:
            continue
        if c["value"].get("target") not in (None, "*", target):
            continue
        until = c["value"].get("until")
        if until is not None and c["seq"] >= until:
            continue
        return c
    return None


def execute(ledger, verb, target, view, act, because=()):
    slice_ = ledger.visible(view)
    rule = next((c for c in reversed(slice_) if c["predicate"] == "may"
                 and c["subject"] == AGENT and c["value"]["verb"] == verb), None)
    mode = rule["value"]["mode"] if rule else "allow"
    ticket = spendable(ledger, slice_, rule, target) if rule and mode == "require" else None
    blocked = mode == "deny" or (mode == "require" and ticket is None)
    value = {"verb": verb, "target": target, "view": view, "world": None}
    del value["world"]
    value["outcome"] = "denied" if blocked else "done"
    if not blocked:
        value["result"] = act()
    # The act and the spending are one claim: a did that retires the signature it used.
    return ledger.append(AGENT, "did", value, ledger.get(view)["world"], by=AGENT,
                         because=list(because) + [view] + ([rule["id"]] if rule else [])
                         + ([ticket["id"]] if ticket else []),
                         replaces=[ticket["id"]] if ticket else [])


def approve(ledger, view, rule_id, target="*", until=None):
    value = {"form": "representation", "approves": rule_id, "target": target}
    if until is not None:
        value["until"] = until
    return ledger.append(HUMAN, "counts", value, "*", by=HUMAN, because=[view])


# ---------------------------------------------------------------------- main
def main():
    path = os.path.join(STATE, "claims.jsonl")
    if os.path.exists(path):
        os.remove(path)
    ledger = Ledger(path)

    # bootstrap: authorization is human, integrity is absent and said so (D-033)
    ledger.append(HUMAN, "counts", {"form": "representation", "approves": "bootstrap",
                                    "scope": "first installation"}, "*", by=HUMAN)
    ledger.append("machine", "counts", {"form": "satisfaction", "assumption": True,
                                        "integrity": "unmeasured"}, "*", by=HUMAN)
    v0 = ledger.bootstrap(W1, {}, by="sensor:fs")
    for verb, mode in (("read", "allow"), ("write", "allow"), ("send", "require")):
        ledger.append(AGENT, "may", {"verb": verb, "mode": mode}, "*", by=HUMAN, because=[v0])
    rule = ledger.append(HUMAN, "counts", {"form": "satisfaction", "scope": PKG,
                                           "test": "every file present, bytes identical"},
                         "*", by=HUMAN, because=[v0])
    send_rule = next(c["id"] for c in ledger.visible(v0)
                     if c["predicate"] == "may" and c["value"]["verb"] == "send")

    # world 1: install
    v1 = commit(ledger, W1, MANIFEST, AGENT, because=[rule])

    # signatures: absent → spent → expired
    e1 = execute(ledger, "send", "mail:advisor", v1, lambda: "sent")
    a1 = approve(ledger, v1, send_rule, target="mail:advisor")
    v2 = tick(ledger, W1, HUMAN)
    e2 = execute(ledger, "send", "mail:advisor", v2, lambda: "sent", because=[a1])
    v3 = tick(ledger, W1, HUMAN)
    e3 = execute(ledger, "send", "mail:advisor", v3, lambda: "sent")
    a2 = approve(ledger, v3, send_rule, target="mail:advisor", until=ledger.rows[-1]["seq"])
    v4 = tick(ledger, W1, HUMAN)
    e4 = execute(ledger, "send", "mail:advisor", v4, lambda: "sent", because=[a2])

    # world 2: fork from v1, remove a file there
    v2a = commit(ledger, W2, {"/etc/htoprc": "fields=1"}, AGENT, because=[rule], view=v1)
    v2b = tick(ledger, W2, HUMAN)

    # rollback world 1 only
    v5 = ledger.rollback(W1, v0, HUMAN, expect=ledger.current_root(W1))

    print("\n--- the ledger (trimmed: id/view/ts columns omitted)")
    for row in ledger.rows:
        live = row["id"] in {c["id"] for c in ledger.active()}
        print(f"{row['seq']:>3} {row['predicate']:<6} {row['world']:<14} {row['subject']:<12} "
              f"{json.dumps(row['value'], ensure_ascii=False, sort_keys=True)[:74]}"
              f"{'' if live else '  [retracted]'}")

    print("\n--- four screens")
    for name, vp in (("W1 installed", v1), ("W1 after rollback", v5),
                     ("W2 fork (htoprc only)", v2b), ("W2 before fork*", v0)):
        s = ledger.visible(vp)
        print(f"{name:<24} visible={len(s):>2} doing={json.dumps(what_its_doing(s))} needs={what_it_needs(s)}")

    print("\n--- verification")
    print("approval one-shot: denied→sent→denied :",
          [e1["outcome"] if isinstance(e1, dict) else ledger.get(e1)["value"]["outcome"],
           ledger.get(e2)["value"]["outcome"], ledger.get(e3)["value"]["outcome"]]
          == ["denied", "done", "denied"])
    print("expired approval rejected              :", ledger.get(e4)["value"]["outcome"] == "denied")
    w2_slice = ledger.visible(v2b)
    print("fork sees the ancestor's claims       :",
          any(r["world"] == W1 and r["predicate"] == "did" for r in w2_slice))
    print("sibling does not see the fork's work  :",
          not any(r["world"] == W2 for r in ledger.visible(v5)))
    print("rollback in W1 leaves W2 intact       :",
          tree_of(w2_slice)["files"] == {"/etc/htoprc": "fields=1"})
    print("W1 after rollback is empty            :", tree_of(ledger.visible(v5))["files"] == {})
    print("W2 does not see W1's later rollback   :",
          not any(r["world"] == W1 and r["seq"] > ledger.seq_of(v1) for r in w2_slice))
    print("global rules visible in both worlds   :",
          all(any(c["predicate"] == "may" for c in ledger.visible(vp)) for vp in (v5, v2b)))
    print("rollback deleted nothing              :", len(ledger.rows))
    print("worlds                                :", sorted({r["world"] for r in ledger.rows}))


if __name__ == "__main__":
    main()
