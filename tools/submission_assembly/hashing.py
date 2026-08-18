"""Deterministic candidate-tree hashing without filesystem metadata."""

from __future__ import annotations

import hashlib
from pathlib import Path


def hash_tree(root: Path) -> tuple[list[dict[str, str]], str]:
    """Return sorted per-file hashes and the framed aggregate tree hash."""
    files = [
        {
            "path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    ]
    preimage = "".join(f"{entry['path']}:{entry['sha256']}\n" for entry in files)
    return files, hashlib.sha256(preimage.encode()).hexdigest()
