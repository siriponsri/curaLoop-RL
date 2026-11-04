"""Preservation guard must distinguish checkout line endings from actual edits."""

import hashlib
import subprocess

from tools.check_research_package import active_markdown, protected_match


def git(root, *args):
    return (
        subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL)
        .decode()
        .strip()
    )


def test_crlf_acceptance_requires_source_blob_and_no_real_working_tree_change(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "core.autocrlf", "true")
    source = tmp_path / "source.py"
    original = b"value = 1\n"
    source.write_bytes(original)
    git(tmp_path, "add", "source.py")
    git(
        tmp_path,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        "fixture",
    )
    head = git(tmp_path, "rev-parse", "HEAD")
    record = {"path": "source.py", "sha256": hashlib.sha256(original).hexdigest()}
    assert protected_match(tmp_path, record, head) == "raw"
    source.write_bytes(b"value = 1\r\n")
    assert protected_match(tmp_path, record, head) == "git_verified_crlf_only"
    source.write_bytes(b"value = 2\r\n")
    assert protected_match(tmp_path, record, head) is None
    source.write_bytes(b"value = 1\r\n")
    assert protected_match(tmp_path, record, "absent-ref") is None


def test_markdown_scope_excludes_ignored_dependencies_and_old_snapshots(tmp_path):
    git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text("outputs/\n.venv/\n")
    for name in (
        "README.md",
        "docs/new.md",
        "outputs/private.md",
        ".venv/vendor.md",
        "docs/archive/original.md",
        "requirements_v3/old.md",
    ):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("text")
    assert {p.relative_to(tmp_path).as_posix() for p in active_markdown(tmp_path)} == {
        "README.md",
        "docs/new.md",
    }
