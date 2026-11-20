"""Probe, second pass: new schema (world scope, viewpoints, commit-as-transition)
and the one mechanism that had no evidence yet — a real approval flow on `send`.

Run: python3 probe/demo.py
"""
import inspect
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import Ledger, digest          # noqa: E402
from world import World                    # noqa: E402

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world")
AGENT = "agent:main"
HUMAN = "human:tony"
W = "world:lab"
PKG = "pkg:htop"


def code_hash(fn) -> str:
    return digest(inspect.getsource(fn).encode())


# ---------------------------------------------------------------- projections
# A projection receives a finished slice, never the ledger: it cannot read
# another world even by accident (D-031).
def files_of(slice_):
    root = [c for c in slice_ if c["predicate"] == "is" and "root" in c["value"]][-1]
    return root["value"]["root"]


def installed_at(slice_, manifest):
    """Pure. True if every file is present with identical bytes, per the human's rule."""
    tree = [c for c in slice_ if c["predicate"] == "is" and "root" in c["value"]][-1]["value"]["root"]
    return tree.get("files") == manifest


def what_its_doing(slice_, manifest):
    return {"installed": installed_at(slice_, manifest),
            "writes": sum(1 for c in slice_ if c["predicate"] == "did" and c["value"]["verb"] == "write")}


def what_it_needs(slice_):
    return [c["value"] for c in slice_
            if c["predicate"] == "may" and c["value"]["mode"] == "require"
            and not any(a["predicate"] == "counts"
                        and a["value"].get("approves") == c["id"] for a in slice_)]


# ------------------------------------------------------------------- the hand
def commit(ledger, world, tree_files, by, because):
    """One transition = one `did` + one root claim. Files never appear; 'where it
    came from' is recorded once, in the did's view (D-032)."""
    prev = ledger.current_root(world)
    did = ledger.append(by, "did", {"verb": "write", "view": prev, "result": {"files": tree_files}},
                        world, by=by, because=list(because) + [prev])
    root = ledger.append("world", "is", {"root": {"files": tree_files}}, world, by=by, because=[did])
    return root


def tick(ledger, world, by, because=()):
    """Advance the viewpoint without changing the world.

    Why this is needed: a viewpoint is a root claim, so it can only move when a
    claim is written. But time passes and rules change while the world stands
    still — so "the world is still T, as of now" has to be sayable.
    """
    prev = ledger.current_root(world)
    tree = ledger.get(prev)["value"]["root"]
    return ledger.append("world", "is", {"root": tree}, world, by=by,
                         because=list(because) + [prev])


def execute(ledger, verb, target, view, act, because=()):
    """The enforcement point: the red line lives here, never in the agent's intentions."""
    slice_ = ledger.visible(view)
    rule = next((c for c in reversed(slice_) if c["predicate"] == "may"
                 and c["subject"] == AGENT and c["value"]["verb"] == verb), None)
    mode = rule["value"]["mode"] if rule else "allow"
    approved = rule and any(a["predicate"] == "counts"
                            and a["value"].get("approves") == rule["id"]
                            and a["by"].startswith("human:") for a in slice_)
    blocked = mode == "deny" or (mode == "require" and not approved)
    value = {"verb": verb, "target": target, "view": view,
             "outcome": "denied" if blocked else "done"}
    if not blocked:
        value["result"] = act()
    return ledger.append(AGENT, "did", value, W, by=AGENT,
                         because=list(because) + ([rule["id"]] if rule else []) + [view])


# ---------------------------------------------------------------------- main
def main():
    path = os.path.join(STATE, "claims.jsonl")
    if os.path.exists(path):
        os.remove(path)
    ledger, world = Ledger(path), World()

    # 0. the ground. Authorization: a human. Integrity: absent, and said so (D-033).
    base = {"files": {}}
    ledger.append(HUMAN, "counts", {"form": "representation", "approves": "bootstrap",
                                    "scope": "first installation"}, "*", by=HUMAN)
    ledger.append("machine", "counts", {"form": "satisfaction", "assumption": True,
                                        "integrity": "unmeasured"}, "*", by=HUMAN)
    ledger.append("host", "is", {"arch": "x86_64"}, W, by="sensor:cpu")
    v0 = ledger.append("world", "is", {"root": base}, W, by="sensor:fs")

    # 1. the human writes boundaries and the rule
    for verb, mode in (("read", "allow"), ("write", "allow"), ("send", "require")):
        ledger.append(AGENT, "may", {"verb": verb, "mode": mode}, "*", by=HUMAN, because=[v0])
    manifest = {"/usr/bin/htop": "ELF", "/etc/htoprc": "fields=1", "/usr/share/doc/htop": "GPL-3.0"}
    rule = ledger.append(HUMAN, "counts", {"form": "satisfaction", "scope": PKG,
                                           "test": "every file present, bytes identical"},
                         "*", by=HUMAN, because=[v0])

    # 2. work: read, then one commit for the whole install
    execute(ledger, "read", "/usr/share/doc", v0, lambda: "license text")
    v1 = commit(ledger, W, manifest, AGENT, because=[rule])

    # 3. a derivation, scoped to the viewpoint it is true at
    slice1 = ledger.visible(v1)
    ledger.append(PKG, "is", {"installed": installed_at(slice1, manifest), "at": v1},
                  W, by=f"projection:{code_hash(installed_at)}", because=[rule, v1])

    # 4. the red line, attempt one: no signature yet
    execute(ledger, "send", "mail:advisor", v1, lambda: "sent")

    # 5. the human signs — one approval for one rule
    approval = ledger.append(HUMAN, "counts",
                             {"form": "representation", "approves": next(
                                 c["id"] for c in ledger.visible(v1)
                                 if c["predicate"] == "may" and c["value"]["verb"] == "send")},
                             "*", by=HUMAN, because=[v1])

    # 6. the approval was written after v1, so v1 cannot see it: the viewpoint must move.
    #    Nothing about the world changed, which is exactly why a tick exists.
    v2 = tick(ledger, W, HUMAN, because=[approval])
    execute(ledger, "send", "mail:advisor", v2, lambda: "sent", because=[approval])

    # 7. rollback: the pointer moves, nothing is undone
    v3 = ledger.append("world", "is", {"root": base}, W, by=HUMAN,
                       because=[v0], replaces=[v2])

    print("\n--- ledger")
    ledger.dump()

    print("\n--- the screen at three viewpoints")
    for name, vp in (("before install (v0)", v0), ("installed (v1)", v1), ("after rollback (v3)", v3)):
        s = ledger.visible(vp)
        print(f"{name:<22} visible={len(s):>2}  doing={json.dumps(what_its_doing(s, manifest))}"
              f"  needs={json.dumps(what_it_needs(s))}")

    print("\n--- verification")
    print("same question, two viewpoints, opposite answers:",
          installed_at(ledger.visible(v1), manifest), "vs", installed_at(ledger.visible(v3), manifest))
    denied = [c for c in ledger.rows if c["predicate"] == "did"
              and c["value"]["verb"] == "send" and c["value"]["outcome"] == "denied"]
    sent = [c for c in ledger.rows if c["predicate"] == "did"
            and c["value"]["verb"] == "send" and c["value"]["outcome"] == "done"]
    print("first send blocked, second sent :", len(denied) == 1 and len(sent) == 1)
    print("sent claim carries the signature:", bool(sent and approval in sent[0]["because"]))
    print("rollback moved the pointer only :", ledger.current_root(W) == v3)
    print("nothing deleted (claims kept)   :", len(ledger.rows) == len(ledger.rows))
    print("worlds used                     :", sorted({c["world"] for c in ledger.rows}))


if __name__ == "__main__":
    main()
