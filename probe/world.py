"""A fake world: content-addressed blobs plus an immutable tree, behind a root pointer.

No filesystem, no syscalls. Everything is derived from a root hash, so "rolling back"
is just re-pointing the root — which is the whole idea, tested cheaply.
"""
import hashlib
import json


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


class World:
    def __init__(self):
        self.blobs = {}   # hash -> bytes
        self.trees = {}   # hash -> {path: blob hash}

    def put(self, data: bytes) -> str:
        key = digest(data)
        self.blobs[key] = data
        return key

    def tree(self, files: dict) -> str:
        """files: path -> bytes. Returns a tree hash, never mutates an existing one."""
        entries = {path: self.put(data) for path, data in files.items()}
        key = digest(json.dumps(entries, sort_keys=True).encode())
        self.trees[key] = entries
        return key

    def write(self, root: str, path: str, data: bytes) -> str:
        entries = dict(self.trees[root])
        entries[path] = self.put(data)
        return self.tree_from_entries(entries)

    def tree_from_entries(self, entries: dict) -> str:
        key = digest(json.dumps(entries, sort_keys=True).encode())
        self.trees[key] = dict(entries)
        return key

    def ls(self, root: str) -> list:
        return sorted(self.trees[root].keys())

    def read(self, root: str, path: str) -> bytes:
        return self.blobs[self.trees[root][path]]

    def snapshot(self, root: str) -> dict:
        """Byte-level view, for proving a rollback really restored the same state."""
        return {path: self.blobs[blob] for path, blob in self.trees[root].items()}
