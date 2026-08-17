"""Shared path-escape safety check for filesystem-walking commands."""

from __future__ import annotations

from pathlib import Path


def escapes_root(root: Path, entry: Path) -> bool:
    """Return whether ``entry``, once resolved, is not a descendant of ``root``.

    Used to fail closed on a symlink (or a symlinked ancestor directory)
    that points outside the directory being scanned or validated.
    """
    try:
        entry.resolve().relative_to(root.resolve())
    except ValueError:
        return True
    return False
