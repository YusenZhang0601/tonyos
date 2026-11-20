"""Probe: install a package in a fake world, roll it back, and try to send something.

The point is not to work. The point is to find where the vocabulary strains.
Run: python3 probe/demo.py

Probe-level simplifications (all deliberate):
  - `may` is looked up per verb only, not per scope
  - one agent, one world branch, no concurrency
  - `is` carries exactly one attribute (the shape was forced by the probe, see README)
  - `did` carries the world it happened in (added by the probe, see README)
"""
import inspect
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import Ledger, digest          # noqa: E402
from world import World                    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "world")
AGENT = "agent:main"
HUMAN = "human:tony"
PKG = "pkg:htop"


def code_hash(fn) -> str:
    """A projection's code is part of the evidence: change it and old derivations die."""
    return digest(inspect.getsource(fn).encode())


# ---------------------------------------------------------------- projections
def check_installed(world, root, manifest):
    """Pure. Answers the human's rule: every file present, every byte identical."""
    present = set(world.ls(root))
    return all(path in present and world.read(root, path) == data
               for path, data in manifest.items())


def what_its_doing(ledger, world_root):
    """The work site. Takes the world explicitly: a projection that assumes "now" is wrong
    the moment the reference moves (this was the probe's most useful failure)."""
    writes = [r for r in ledger.active()
              if r["predicate"] == "did" and r["value"]["verb"] == "write"]
    verdict = ledger.current(PKG, "is")
    fresh = verdict and verdict["value"].get("world") == world_root
    return {"writes": len(writes), "status": verdict["value"]["status"] if fresh else "unknown"}


def what_it_needs(ledger):
    """Only what a human must decide: unsatisfied `require` rules."""
    return [r["value"] for r in ledger.active()
            if r["predicate"] == "may" and r["value"]["mode"] == "require"
            and not approved(ledger, r)]


# ------------------------------------------------------------------- the hand
def approved(ledger, rule):
    """A signature counts as approval. Only a human signature may do this."""
    return any(r["predicate"] == "counts"
               and r["value"].get("form") == "representation"
               and r["value"].get("approves") == rule["id"]
               and r["by"].startswith("human:")
               and r in ledger.active()
               for r in ledger.rows)


def execute(ledger, verb, target, act, world_root=None):
    """The enforcement point. The red line lives here, never in the agent's intentions."""
    rule = next((r for r in reversed(ledger.active())
                 if r["subject"] == AGENT and r["predicate"] == "may"
                 and r["value"]["verb"] == verb), None)
    mode = rule["value"]["mode"] if rule else "allow"
    value = {"verb": verb, "target": target, "world": world_root}
    if mode == "deny" or (mode == "require" and not approved(ledger, rule)):
        value.update({"outcome": "denied", "why": f"mode={mode}"})
        return ledger.append(AGENT, "did", value, by=AGENT,
                             because=[rule["id"]] if rule else [])
    value.update({"outcome": "done", "result": act()})
    return ledger.append(AGENT, "did", value, by=AGENT,
                         because=[rule["id"]] if rule else [])


# ---------------------------------------------------------------------- demo
def main():
    path = os.path.join(STATE, "claims.jsonl")
    if os.path.exists(path):
        os.remove(path)
    ledger, world = Ledger(path), World()

    # 0. the ground: a human signature and a sensor reading. Nothing below them.
    root0 = world.tree({"etc/manifest": b"baseline\n"})
    sig = ledger.append(HUMAN, "counts",
                        {"form": "representation", "approves": "self", "scope": "initial trust"},
                        by=HUMAN)
    ledger.append("host", "is", {"arch": "x86_64"}, by="sensor:cpu")
    ledger.append("world", "is", {"root": root0}, by="sensor:fs")

    # 1. the human writes the boundaries and the rule
    for verb, mode in (("read", "allow"), ("write", "allow"), ("send", "require")):
        ledger.append(AGENT, "may", {"verb": verb, "mode": mode}, by=HUMAN, because=[sig])
    manifest = {"/usr/bin/htop": b"\x7fELF htop\n",
                "/etc/htoprc": b"fields=1\n",
                "/usr/share/doc/htop": b"GPL-3.0\n"}
    rule = ledger.append(HUMAN, "counts",
                         {"form": "satisfaction", "scope": PKG,
                          "test": "all files present and byte-identical"},
                         by=HUMAN, because=[sig])

    # 2. the agent works: read, write each file, advance the reference
    root = root0
    execute(ledger, "read", "etc/manifest", lambda: sorted(world.ls(root0)), root0)
    for file, blob in manifest.items():
        root = world.write(root, file.lstrip("/"), blob)
        execute(ledger, "write", file, lambda f=file: f, root)
    ledger.append("world", "is", {"root": root}, by="sensor:fs")

    # 3. a derivation, not an announcement: the rule is the human's, the verdict is computed
    verdict = check_installed(world, root, {p.lstrip("/"): b for p, b in manifest.items()})
    # NOTE: "world" belongs in a claim-level scope field, not in the value.
    # The probe puts it here as a workaround; the schema change needs a ruling.
    ledger.append(PKG, "is", {"status": "installed" if verdict else "broken", "world": root},
                  by=f"projection:{code_hash(check_installed)}",
                  because=[rule] + [r["id"] for r in ledger.active() if r["predicate"] == "did"])

    # 4. the red line: an attempt to send, with no signature
    execute(ledger, "send", "mail:advisor", lambda: "sent", root)

    # 5. rollback: do not undo the events, re-point the reference
    before = world.snapshot(root0)
    pointer = ledger.current("world", "is")
    ledger.append("world", "is", {"root": root0}, by=HUMAN,
                  because=[sig], replaces=[pointer["id"]])

    print("\n--- ledger")
    ledger.dump()

    print("\n--- projections")
    print("what it is doing :", json.dumps(what_its_doing(ledger, ledger.current("world", "is")["value"]["root"]), ensure_ascii=False))
    print("what it needs     :", json.dumps(what_it_needs(ledger), ensure_ascii=False))

    print("\n--- verification")
    now = ledger.current("world", "is")["value"]["root"]
    print("rollback byte-identical :", world.snapshot(now) == before)
    print("package files gone      :", "usr/bin/htop" not in world.snapshot(now))
    print("send was blocked        :", any(r["predicate"] == "did" and r["value"].get("outcome") == "denied"
                                          for r in ledger.active()))
    print("history still records it:", sum(1 for r in ledger.active()
                                           if r["predicate"] == "did" and r["value"]["verb"] == "write"), "writes")
    deriv = [r for r in ledger.active() if r["by"].startswith("projection:")]
    print("derivation roots        :", sorted({r.split(":")[0] for d in deriv for r in ledger.chain(d["id"])}))
    print("claims in one screen    :", len(ledger.rows))


if __name__ == "__main__":
    main()
