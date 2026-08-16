"""scan_path must fail closed on every documented category, using only
synthetic placeholder fixtures, and must never descend into pruned dirs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.offline_ops.secrets.scanner import scan_path


def _categories(root: Path) -> set[str]:
    return {finding.category for finding in scan_path(root)}


def test_missing_root_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        scan_path(tmp_path / "does-not-exist")


def test_empty_directory_has_no_findings(tmp_path: Path) -> None:
    assert scan_path(tmp_path) == []


def test_private_key_is_detected(tmp_path: Path) -> None:
    (tmp_path / "key.pem").write_text(
        "-----BEGIN RSA PRIVATE KEY-----\nFAKE-NOT-A-REAL-KEY\n-----END RSA PRIVATE KEY-----\n",
        encoding="utf-8",
    )
    assert "private_key" in _categories(tmp_path)


def test_aws_style_access_key_is_detected(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("token=AKIAAAAAAAAAAAAAAAAA", encoding="utf-8")
    assert "aws_access_key" in _categories(tmp_path)


def test_authorization_header_is_detected(tmp_path: Path) -> None:
    (tmp_path / "req.txt").write_text(
        "Authorization: Bearer FAKE-TOKEN-VALUE-123", encoding="utf-8"
    )
    assert "authorization_header" in _categories(tmp_path)


def test_generic_secret_assignment_is_detected(tmp_path: Path) -> None:
    (tmp_path / "settings.py").write_text('api_key = "not-a-real-secret-value"', encoding="utf-8")
    assert "generic_secret_assignment" in _categories(tmp_path)


def test_tunnel_url_is_detected(tmp_path: Path) -> None:
    (tmp_path / "notes.md").write_text("endpoint: my-peer.ngrok.io", encoding="utf-8")
    assert "tunnel_url" in _categories(tmp_path)


def test_tunnel_config_filename_is_detected(tmp_path: Path) -> None:
    (tmp_path / "ngrok.yml").write_text("tunnels: {}\n", encoding="utf-8")
    assert "tunnel_configuration" in _categories(tmp_path)


def test_cache_and_temp_filenames_are_detected(tmp_path: Path) -> None:
    (tmp_path / "module.pyc").write_bytes(b"\x00")
    assert "cache_or_temp_file" in _categories(tmp_path)


def test_pruned_directories_are_never_descended_into(tmp_path: Path) -> None:
    pycache = tmp_path / "__pycache__"
    pycache.mkdir()
    (pycache / "leaked.txt").write_text("AKIAAAAAAAAAAAAAAAAA", encoding="utf-8")
    assert scan_path(tmp_path) == []


def test_non_artifact_nonce_in_json_is_detected(tmp_path: Path) -> None:
    (tmp_path / "unexpected_dump.json").write_text('{"nonce": "abc"}', encoding="utf-8")
    assert "non_artifact_nonce" in _categories(tmp_path)


def test_nonce_in_a_canonical_artifact_filename_is_exempt(tmp_path: Path) -> None:
    (tmp_path / "log_game1_g01.json").write_text('{"nonce": "abc"}', encoding="utf-8")
    assert _categories(tmp_path) == set()


def test_nonce_under_the_interop_fixtures_directory_is_exempt(tmp_path: Path) -> None:
    interop_dir = tmp_path / "interop" / "golden_vectors"
    interop_dir.mkdir(parents=True)
    (interop_dir / "vectors.json").write_text('{"nonce": "abc"}', encoding="utf-8")
    assert _categories(tmp_path) == set()


def test_exclude_relative_dirs_prunes_given_paths(tmp_path: Path) -> None:
    excluded = tmp_path / "tests" / "offline_ops"
    excluded.mkdir(parents=True)
    (excluded / "leak.txt").write_text("AKIAAAAAAAAAAAAAAAAA", encoding="utf-8")

    findings = scan_path(tmp_path, exclude_relative_dirs=frozenset({"tests/offline_ops"}))

    assert findings == []


def test_symlink_escaping_the_root_is_detected(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside_target.txt"
    outside.write_text("not a secret", encoding="utf-8")
    scan_root = tmp_path / "scan_root"
    scan_root.mkdir()
    link = scan_root / "escape_link.txt"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation requires elevated privilege on this platform")
    try:
        assert "symlink" in _categories(scan_root)
    finally:
        outside.unlink(missing_ok=True)
