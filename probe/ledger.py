"""Append-only claim ledger: one record type, four predicates, closed vocabulary.

Not a framework. Just enough to find out whether the vocabulary holds.
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


def digest(obj) -> str:
    raw = obj if isinstance(obj, bytes) else json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


class Ledger:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.rows = []
        if os.path.exists(path):
            with open(self.path) as f:
                self.rows = [json.loads(line) for line in f if line.strip()]

    def append(self, subject, predicate, value, by, because=(), replaces=()):
        assert predicate in PREDICATES, f"unknown predicate {predicate}"
        if predicate == "did":
            assert value["verb"] in VERBS, f"unknown verb {value['verb']}"
        if predicate == "may":
            assert value["mode"] in MODES, f"unknown mode {value['mode']}"
        if predicate == "counts":
            assert value["form"] in FORMS, f"unknown form {value['form']}"
        if predicate in HUMAN_ONLY and not by.startswith("human:"):
            # D-019: the agent may draft, but only a signature makes it real
            assert value.get("proposal") is True, f"{predicate} is human-written; agent may only propose"
        body = {
            "seq": len(self.rows) + 1,
            "subject": subject,
            "predicate": predicate,
            "value": value,
            "by": by,
            "at": round(time.time(), 3),
            "because": list(because),
            "replaces": list(replaces),
        }
        body["id"] = digest(body)
        self.rows.append(body)
        with open(self.path, "a") as f:
            f.write(json.dumps(body, sort_keys=True, ensure_ascii=False) + "\n")
        return body["id"]

    def get(self, cid):
        for row in self.rows:
            if row["id"] == cid:
                return row
        raise KeyError(cid)

    def active(self):
        """A claim is inactive if an *active* claim retracts it. Retraction is a fixpoint,
        so retracting a retraction brings the original back (TMS semantics)."""
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

    def current(self, subject, predicate):
        found = [r for r in self.active() if r["subject"] == subject and r["predicate"] == predicate]
        return found[-1] if found else None

    def chain(self, cid, depth=0):
        """Walk the justification to its roots. Roots must be human signatures or sensors."""
        row = self.get(cid)
        if not row["because"] or row["by"].startswith(("human:", "sensor:")):
            return [row["by"]]
        out = []
        for parent in row["because"]:
            out += self.chain(parent, depth + 1)
        return sorted(set(out))

    def dump(self):
        for row in self.rows:
            mark = "" if row["id"] in {r["id"] for r in self.active()} else "  [retracted]"
            value = json.dumps(row["value"], ensure_ascii=False, sort_keys=True)
            print(f"{row['seq']:>3}  {row['predicate']:<6} {row['subject']:<18} {row['by']:<16} {value}{mark}")
