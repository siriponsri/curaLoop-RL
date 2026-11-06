"""Verify and safely retain every byte from an owned remote-task snapshot."""

import argparse
import hashlib
import json
import os
import stat
import zipfile
from pathlib import Path

from tools.index_fsmol_archive_v1 import unsafe_name

ROOT = Path(__file__).resolve().parents[1]


def unsafe_windows_path(name):
    if unsafe_name(name):
        return True
    reserved = {"CON", "PRN", "AUX", "NUL"} | {
        f"{p}{n}" for p in ("COM", "LPT") for n in range(1, 10)
    }
    return any(
        part.endswith((" ", ".")) or part.split(".")[0].upper() in reserved
        for part in name.split("/")
    )


def sha(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024**2), b""):
            value.update(block)
    return value.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--folder", type=Path, required=True)
    args = p.parse_args()
    folder = args.folder.resolve(strict=True)
    allowed = (ROOT / ".local/goal4r2a3-20261106-v1/remote-return").resolve()
    if not allowed.is_relative_to(ROOT.resolve()) or not folder.is_relative_to(allowed):
        raise ValueError("Return folder must stay in the explicit local preservation tree.")
    receipt_path, output = folder / "local-verification.json", folder / "files"
    if receipt_path.exists() or output.exists():
        raise FileExistsError("Preserve the existing return/receipt.")
    if (folder / "manifest.json").stat().st_size > 50 * 1024**2:
        raise ValueError("Manifest size cap exceeded.")
    manifest = json.loads((folder / "manifest.json").read_text())
    if manifest["root"] != "/home/chaw/curaloop-rl/goal4r2a3-20261106-v1":
        raise ValueError("Manifest must identify the exact approved remote root.")
    expected = {r["path"]: r for r in manifest["files"]}
    if (
        len(expected) != manifest["file_count"]
        or len(expected) > 50000
        or manifest["bytes"] > 16 * 1024**3
        or sum(r["bytes"] for r in expected.values()) != manifest["bytes"]
        or any(type(r["bytes"]) is not int or r["bytes"] < 0 for r in expected.values())
        or len({n.casefold() for n in expected}) != len(expected)
    ):
        raise ValueError("Invalid/oversized task manifest.")
    archive_path = folder / "task.zip"
    if archive_path.stat().st_size > manifest["bytes"] + max(1024**2, len(expected) * 1024):
        raise ValueError("Archive size exceeds bounded inventory allowance.")
    if sha(archive_path) != manifest["zip_sha256"]:
        raise ValueError("Transfer archive checksum differs.")
    with zipfile.ZipFile(folder / "task.zip") as archive:
        infos = archive.infolist()
        if len(infos) != len(expected) or {i.filename for i in infos} != set(expected):
            raise ValueError("Archive and file manifest differ.")
        for info in infos:
            target = output / info.filename
            if unsafe_windows_path(info.filename) or not target.resolve().is_relative_to(
                output.resolve()
            ):
                raise ValueError("Unsafe snapshot path.")
            if (
                stat.S_ISLNK(info.external_attr >> 16)
                or info.file_size != expected[info.filename]["bytes"]
            ):
                raise ValueError("Snapshot entry type/size differs.")
        for info in infos:
            target = output / info.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            value = hashlib.sha256()
            with archive.open(info) as source, target.open("xb") as dest:
                for block in iter(lambda: source.read(1024**2), b""):
                    dest.write(block)
                    value.update(block)
            if value.hexdigest() != expected[info.filename]["sha256"]:
                raise ValueError("Restored file checksum differs: " + info.filename)

    def traversal_error(error):
        raise error

    actual = []
    for parent, dirs, files in os.walk(output, onerror=traversal_error, followlinks=False):
        for name in dirs + files:
            path = Path(parent) / name
            if path.is_symlink() or not path.resolve().is_relative_to(output.resolve()):
                raise ValueError("Unexpected retained symlink/path.")
            if path.is_file():
                actual.append(
                    {
                        "path": path.relative_to(output).as_posix(),
                        "bytes": path.stat().st_size,
                        "sha256": sha(path),
                    }
                )
            elif not path.is_dir():
                raise ValueError("Unsupported retained filesystem entry.")
    rows = sorted(manifest["files"], key=lambda r: r["path"])
    if sorted(actual, key=lambda r: r["path"]) != rows:
        raise ValueError("Reread of retained local files does not match complete inventory.")
    tree_sha = hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if tree_sha != manifest["tree_sha256"]:
        raise ValueError("Manifest tree digest differs.")
    result = {
        "status": "PASS_LOCAL_ALL_FILES_VERIFIED",
        "remote_root": manifest["root"],
        "local_files": str(output),
        "file_count": len(rows),
        "bytes": manifest["bytes"],
        "tree_sha256": tree_sha,
        "zip_sha256": manifest["zip_sha256"],
        "scientific_contents_deserialized": False,
    }
    receipt_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
