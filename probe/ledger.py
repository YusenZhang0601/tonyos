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

from store import frame, recover

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
        self.duplicates = 0
        self.truncated = 0
        if os.path.exists(path):
            raw = open(path, "rb").read()
            payloads, valid = recover(raw)
            self.rows = [json.loads(p) for p in payloads]
            if valid < len(raw):
                # The tail never made it, or the first bad frame starts here. Cut it
                # and keep the fact (D-039): a lost tail must be visible, not silent.
                self.truncated = len(raw) - valid
                with open(path, "r+b") as f:
                    f.truncate(valid)

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
        # Identity is content only (D-038). Position is a property of the container,
        # never of the name: two nodes asserting the same thing must agree on the id.
        content = {
            "subject": subject,
            "predicate": predicate,
            "value": value,
            "world": world,
            "by": by,
            "because": list(because),
            "replaces": list(replaces),
        }
        cid = digest(content)
        if any(row["id"] == cid for row in self.rows):
            # Re-asserting the same thing is not a new event. Whether that is right
            # for repeated identical `did`s is an open question, not a settled one.
            self.duplicates += 1
            return cid
        body = dict(content, id=cid, seq=len(self.rows) + 1, ts=round(time.time(), 3))
        raw = json.dumps(body, sort_keys=True, ensure_ascii=False).encode()
        with open(self.path, "ab") as f:
            f.write(frame(raw))
            f.flush()
            os.fsync(f.fileno())          # the commit point (D-039)
        self.rows.append(body)
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

    def _origin(self, root):
        """The viewpoint a root was forked from, if it came from another world.

        A fork is just a commit whose `did.view` points into a different world, so
        ancestry is derivable and needs no extra field.
        """
        for cid in root["because"]:
            claim = self.get(cid)
            if claim["predicate"] == "did" and claim["value"].get("view"):
                parent = self.get(claim["value"]["view"])
                if parent["world"] != root["world"]:
                    return claim["value"]["view"]
        return None

    def _world_origin(self, world):
        """Where a world was forked from, if it was. A property of the world, not
        of a viewpoint: otherwise any later tick would lose the ancestry."""
        for row in self.rows:
            if row["world"] != world or row["predicate"] != "is" or "root" not in row["value"]:
                continue
            origin = self._origin(row)
            if origin:
                return origin
        return None

    def visible(self, viewpoint):
        """The slice of the ledger visible at a viewpoint, walking ancestry.

        Scope resolution lives here, not in projections (D-031): a projection is
        handed a finished world and cannot read another one by accident.
        """
        root = self.get(viewpoint)
        assert root["predicate"] == "is" and "root" in root["value"], "a viewpoint must be a root claim"
        windows = []
        world, cutoff = root["world"], root["seq"]
        while world and world != "*":
            windows.append((world, cutoff))
            origin = self._world_origin(world)
            if not origin:
                break
            parent = self.get(origin)
            world, cutoff = parent["world"], parent["seq"]
        live = self.active()
        return [row for row in live
                if row["world"] == "*"
                or any(row["world"] == w and row["seq"] <= cutoff for w, cutoff in windows)]

    def seq_of(self, cid):
        return self.get(cid)["seq"]

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
