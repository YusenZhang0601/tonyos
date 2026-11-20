"""Append-only claim ledger.

Schema, after the probe's findings:
  - every claim carries a `world`; only `may` / `counts` may use "*" (D-030)
  - a commit is one `did` plus one `is(world, root)`; "where it came from" is
    recorded once, in the did's view, never twice (D-032)
  - a viewpoint IS a root claim: it pins world, sequence and tree at once
  - identity is content, not position (D-038)
  - records are framed and checksummed; a commit is durable at fsync (D-039)
  - reading the head, assigning the position and advancing it are ONE critical
    section, and it lives here, not in the caller (D-040)
"""
import contextlib
import fcntl
import hashlib
import json
import os
import threading
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


class Conflict(Exception):
    """The head moved. The caller may retry or fork; it is never silent."""


class Batcher:
    """One fsync serves every commit that arrived during the window.

    In-process only: a second process writing the same file cannot share an fsync
    boundary. Cross-process writers use the locked, per-commit path.
    """

    def __init__(self, path, window=0.002):
        self.fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        self.cv = threading.Condition()
        self.pending = []
        self.next_ticket = 1
        self.flushed = 0
        self.fsyncs = 0
        self.batches = 0
        self.batch_sizes = []
        self.stop = False
        self.window = window
        self.fail = None
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def enqueue(self, data):
        with self.cv:
            if self.fail:
                raise self.fail
            ticket = self.next_ticket
            self.next_ticket += 1
            self.pending.append((ticket, data))
            self.cv.notify()
            return ticket

    def wait(self, ticket):
        with self.cv:
            while self.flushed < ticket:
                if self.fail:
                    raise self.fail
                self.cv.wait()

    def _run(self):
        while True:
            with self.cv:
                while not self.pending and not self.stop:
                    self.cv.wait(self.window)
                if self.stop and not self.pending:
                    return
                # Condition.wait returns on notify, not only on timeout; loop to the
                # deadline so the whole window is actually used.
                deadline = time.monotonic() + self.window
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    self.cv.wait(remaining)
                batch, self.pending = self.pending, []
                target = batch[-1][0]
            try:
                os.write(self.fd, b"".join(data for _, data in batch))
                os.fsync(self.fd)
            except OSError as exc:                 # a failed fsync must not look like success
                with self.cv:
                    self.fail = exc
                    self.cv.notify_all()
                return
            with self.cv:
                self.fsyncs += 1
                self.batches += 1
                self.batch_sizes.append(len(batch))
                self.flushed = target
                self.cv.notify_all()

    def close(self):
        with self.cv:
            self.stop = True
            self.cv.notify_all()
        self.thread.join()
        os.close(self.fd)


class Ledger:
    def __init__(self, path, writable=True, group=False, window=0.002):
        self.path = path
        self.writable = writable
        self.group = group and writable
        self._mu = threading.RLock()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.rows = []
        self.duplicates = 0
        self.truncated = 0
        self._batcher = Batcher(path, window) if self.group else None
        self._fsyncs = 0
        self._load(truncate=writable)

    def close(self):
        if self._batcher:
            self._batcher.close()

    @property
    def fsyncs(self):
        return self._batcher.fsyncs if self._batcher else self._fsyncs

    @property
    def batch_stats(self):
        if not self._batcher:
            return (0, [])
        return (self._batcher.batches, list(self._batcher.batch_sizes))

    # ------------------------------------------------------------------ storage
    def _load(self, truncate=False):
        """Read the file. Cutting a bad tail is only allowed under exclusive access."""
        self.rows = []
        if not os.path.exists(self.path):
            return
        raw = open(self.path, "rb").read()
        payloads, valid = recover(raw)
        self.rows = [json.loads(p) for p in payloads]
        if valid < len(raw):
            self.truncated = len(raw) - valid
            if truncate:
                with open(self.path, "r+b") as f:
                    f.truncate(valid)

    @contextlib.contextmanager
    def _exclusive(self, world):
        """One writer at a time, and a fresh view of the file inside.

        The lock is per ledger, not per world: one file. A per-world lock without
        per-world files would let two writers append to one file while a third
        re-reads it. Sharding the log is a later step, and it needs its own probes.
        """
        assert self.writable, "this ledger was opened read-only"
        if self.group:                         # in-process only; see Batcher
            with self._mu:
                yield
            return
        with open(self.path + ".lock", "a+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                self._load(truncate=True)
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def _body(self, subject, predicate, value, world, by, because, replaces):
        # Identity is content only (D-038). Position is a property of the container.
        content = {
            "subject": subject,
            "predicate": predicate,
            "value": value,
            "world": world,
            "by": by,
            "because": list(because),
            "replaces": list(replaces),
        }
        return dict(content, id=digest(content), seq=0, ts=round(time.time(), 3))

    def _write(self, bodies, defer=False):
        """Write frames and make them durable. Positions are assigned here.

        `defer` is for the group path: enqueue under the lock, wait outside it, so
        neighbours can join the same fsync.
        """
        assert bodies, "nothing to write"
        base = len(self.rows)
        for i, body in enumerate(bodies):
            body["seq"] = base + i + 1
        data = b"".join(frame(json.dumps(b, sort_keys=True, ensure_ascii=False).encode())
                        for b in bodies)
        if self.group:
            ticket = self._batcher.enqueue(data)
            self.rows.extend(bodies)
            if not defer:
                self._batcher.wait(ticket)
            return ticket
        with open(self.path, "ab") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())          # the commit point (D-039)
        self._fsyncs += 1
        self.rows.extend(bodies)
        return None

    # ------------------------------------------------------------------ writing
    def append(self, subject, predicate, value, world, by, because=(), replaces=()):
        """A claim that does not advance a world. Roots have their own methods."""
        assert self.writable, "this ledger was opened read-only"
        assert predicate in PREDICATES, f"unknown predicate {predicate}"
        assert world and (world == "*" or isinstance(world, str)), "world is required (D-030)"
        if predicate not in GLOBAL_OK:
            assert world != "*", f"{predicate} must land in a concrete world (D-030)"
        if predicate == "is" and isinstance(value, dict) and "root" in value:
            raise AssertionError("a root may only be written by commit/tick/rollback/bootstrap")
        if predicate == "did":
            assert value["verb"] in VERBS, f"unknown verb {value['verb']}"
        if predicate == "may":
            assert value["mode"] in MODES, f"unknown mode {value['mode']}"
        if predicate == "counts":
            assert value["form"] in FORMS, f"unknown form {value['form']}"
        if predicate in HUMAN_ONLY and not by.startswith("human:"):
            assert value.get("proposal") is True, f"{predicate} is human-written; agent may only propose"

        with self._exclusive(world):
            body = self._body(subject, predicate, value, world, by, because, replaces)
            if any(row["id"] == body["id"] for row in self.rows):
                # Re-asserting the same thing is not a new event. Whether that is
                # right for repeated identical `did`s is still open (D-038).
                self.duplicates += 1
                return body["id"]
            self._write([body])
            return body["id"]

    def _roots(self, world):
        return [r for r in self.active()
                if r["predicate"] == "is" and isinstance(r["value"], dict)
                and "root" in r["value"] and r["world"] == world]

    def _head_checked(self, world, expect):
        """The parent viewpoint, or Conflict. A world with no root accepts a fork."""
        roots = self._roots(world)
        if roots:
            cur = roots[-1]["id"]
            if cur != expect:
                raise Conflict(f"{world}: expected {expect}, current {cur}")
            return cur
        parent = self.get(expect)         # the fork's parent must exist
        if parent["predicate"] != "is" or "root" not in parent["value"]:
            raise Conflict(f"{expect} is not a viewpoint")
        return expect

    def bootstrap(self, world, files, by, because=()):
        """The first root of a world. Refuses if one already exists."""
        with self._exclusive(world):
            if self._roots(world):
                raise Conflict(f"{world} already has a root")
            root = self._body("world", "is", {"root": {"files": files}},
                              world, by, because, [])
            self._write([root])
            return root["id"]

    def commit(self, world, files, by, expect, because=(), replaces=()):
        """Advance a world: one did + one root, under a compare-and-swap on the head."""
        if self.group:
            with self._mu:
                parent = self._head_checked(world, expect)
                did, root = self._commit_bodies(world, files, by, parent, because, replaces)
                ticket = self._write([did, root], defer=True)
            self._batcher.wait(ticket)         # outside the lock: neighbours batch in
            return root["id"]
        with self._exclusive(world):
            parent = self._head_checked(world, expect)
            did, root = self._commit_bodies(world, files, by, parent, because, replaces)
            # One write, one fsync: the commit point covers both frames. An orphan
            # did can still survive if the two frames straddle a page boundary and
            # only the first page reaches the disk; that means "the attempt was
            # recorded, the world did not advance" (§4.7), not a committed write.
            self._write([did, root])
            return root["id"]

    def _commit_bodies(self, world, files, by, parent, because, replaces):
        did = self._body(by, "did",
                         {"verb": "write", "view": parent, "result": {"files": files}},
                         world, by, list(because) + [parent], [])
        root = self._body("world", "is", {"root": {"files": files}},
                          world, by, [did["id"]], list(replaces))
        return did, root

    def tick(self, world, by, expect, because=()):
        """Same tree, later position. Time must be able to advance without the world."""
        with self._exclusive(world):
            parent = self._head_checked(world, expect)
            tree = self.get(parent)["value"]["root"]
            root = self._body("world", "is", {"root": tree}, world, by,
                              list(because) + [parent], [])
            self._write([root])
            return root["id"]

    def rollback(self, world, to, by, expect, because=()):
        """Move the pointer back. Nothing is undone; history does not move."""
        with self._exclusive(world):
            parent = self._head_checked(world, expect)
            target = self.get(to)
            if target["predicate"] != "is" or "root" not in target["value"]:
                raise Conflict(f"{to} is not a viewpoint")
            root = self._body("world", "is", {"root": target["value"]["root"]},
                              world, by, list(because) + [to], [parent])
            self._write([root])
            return root["id"]

    # ------------------------------------------------------------------ reading
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
        """The viewpoint a root was forked from, if it came from another world."""
        for cid in root["because"]:
            claim = self.get(cid)
            if claim["predicate"] == "did" and claim["value"].get("view"):
                parent = self.get(claim["value"]["view"])
                if parent["world"] != root["world"]:
                    return claim["value"]["view"]
        return None

    def _world_origin(self, world):
        """Where a world was forked from. A property of the world, not a viewpoint:
        otherwise any later tick would lose the ancestry."""
        for row in self.rows:
            if row["world"] != world or row["predicate"] != "is" or "root" not in row["value"]:
                continue
            origin = self._origin(row)
            if origin:
                return origin
        return None

    def visible(self, viewpoint):
        """The slice of the ledger visible at a viewpoint, walking ancestry.

        A projection receives a slice, never the ledger: it cannot read another
        world by accident (D-031).
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

    def reload(self):
        """Refresh this reader's view. A writer re-reads inside the lock anyway."""
        self._load(truncate=False)

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
