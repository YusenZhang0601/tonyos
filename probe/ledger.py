"""Append-only claim ledger.

Schema after the probe's first findings:
  - every claim carries a `world`; only `may` / `counts` may use "*" (D-030)
  - a commit is one `did` plus one `is(world, root)`; "where it came from" is
    recorded once, in the did's view, never twice (D-032)
  - a viewpoint IS a root claim: it pins world, sequence and tree at once
"""
import hashlib
import json
import os
import time

PREDICATES = {"is", "did", "may", "counts"}
VERBS = {"read", "write", "send"}
MODES = {"allow", "require", "deny"}
FORMS = {"identity", "satisfaction", "representation"}
HUMAN_ONLY = {"may", "counts"}
GLOBAL_OK = {"may", "counts"}


def digest(obj) -> str:
    raw = obj if isinstance(obj, bytes) else json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


class NotFound(Exception):
    pass


class Ledger:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.rows = []
        if os.path.exists(path):
            with open(path) as f:
                self.rows = [json.loads(line) for line in f if line.strip()]

    # ---------------------------------------------------------------- writing
    def append(self, subject, predicate, value, world, by, because=(), replaces=()):
        assert predicate in PREDICATES, f"unknown predicate {predicate}"
        assert world and (world == "*" or isinstance(world, str)), "world is required (D-030)"
        if predicate not in GLOBAL_OK:
            assert world != "*", f"{predicate} must land in a concrete world (D-030)"
        if predicate == "did":
            assert value["verb"] in VERBS, f"unknown verb {value['verb']}"
        if predicate == "may":
            assert value["mode"] in MODES, f"unknown mode {value['mode']}"
        if predicate == "counts":
            assert value["form"] in FORMS, f"unknown form {value['form']}"
        if predicate in HUMAN_ONLY and not by.startswith("human:"):
            assert value.get("proposal") is True, f"{predicate} is human-written; agent may only propose"
        body = {
            "seq": len(self.rows) + 1,
            "subject": subject,
            "predicate": predicate,
            "value": value,
            "world": world,
            "by": by,
            "ts": round(time.time(), 3),
            "because": list(because),
            "replaces": list(replaces),
        }
        body["id"] = digest(body)
        self.rows.append(body)
        with open(self.path, "a") as f:
            f.write(json.dumps(body, sort_keys=True, ensure_ascii=False) + "\n")
        return body["id"]

    # ---------------------------------------------------------------- reading
    def get(self, cid):
        for row in self.rows:
            if row["id"] == cid:
                return row
        raise NotFound(cid)

    def active(self):
        """A claim is inactive if an *active* claim retracts it (fixpoint: retracting a
        retraction brings the original back)."""
        live = {row["id"]: True for row in self.rows}
        changed = True
        while changed:
            changed = False
            for row in self.rows:
                if not live.get(row["id"]):
                    continue
                for target in row["replaces"]:
                    if live.get(target):
                        live[target] = False
                        changed = True
        return [row for row in self.rows if live[row["id"]]]

    def visible(self, viewpoint):
        """The slice of the ledger visible at a viewpoint.

        Scope resolution lives here, not in projections (D-031): a projection is
        handed a finished world and cannot read another one by accident.
        """
        root = self.get(viewpoint)
        assert root["predicate"] == "is" and "root" in root["value"], "a viewpoint must be a root claim"
        world, cutoff = root["world"], root["seq"]
        out = []
        for row in self.active():
            if row["seq"] > cutoff:
                continue
            if row["world"] == "*" or row["world"] == world:
                out.append(row)
        return out

    def current_root(self, world):
        roots = [r for r in self.active()
                 if r["predicate"] == "is" and r["value"].get("root") and r["world"] == world]
        if not roots:
            raise NotFound(f"world {world} has no root")
        return roots[-1]["id"]

    def chain(self, cid):
        """Roots of the justification: they must be human signatures or sensors."""
        row = self.get(cid)
        if not row["because"] or row["by"].startswith(("human:", "sensor:")):
            return [row["by"]]
        out = []
        for parent in row["because"]:
            out += self.chain(parent)
        return sorted(set(out))

    def dump(self):
        live = {r["id"] for r in self.active()}
        for row in self.rows:
            mark = "" if row["id"] in live else "  [retracted]"
            value = json.dumps(row["value"], ensure_ascii=False, sort_keys=True)
            print(f"{row['seq']:>3}  {row['predicate']:<6} {row['world']:<8} {row['subject']:<16} "
                  f"{row['by']:<14} {value}{mark}")
