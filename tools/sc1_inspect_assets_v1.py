"""Inspect official archive/schema and split identities without printing task content."""
import json
import stat
import zipfile
from pathlib import Path
from tools.sc1_control_v1 import ACCOUNT, ROOT, digest, write_new


def main():
    root = ROOT / "research/raw_data/external-benchmarks/scicode-2024"
    target = root / "upstream-code"
    if target.exists():
        raise FileExistsError(target)
    with zipfile.ZipFile(root / "upstream-code.zip") as archive:
        members = archive.infolist()
        if len(members) > 1000 or sum(item.file_size for item in members) > 33554432:
            raise ValueError("Unexpected official code archive size")
        for item in members:
            relative = Path(*Path(item.filename).parts[1:])
            if not relative.parts:
                continue
            dest = (target / relative).resolve()
            if not dest.is_relative_to(target.resolve()) or stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError("Unsafe archive path/type")
            if item.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with dest.open("xb") as stream:
                    stream.write(archive.read(item))
    catalog = {}
    for split in ("dev", "test"):
        rows = [json.loads(line) for line in (root / "upstream-hf" / f"problems_{split}.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        data = []
        for row in rows:
            steps = row.get("sub_steps", row.get("substeps", []))
            data.append({"main_id": row.get("problem_id", row.get("problem_index", row.get("id"))),
                         "keys": sorted(row), "subproblem_count": len(steps),
                         "subproblem_keys": sorted(steps[0]) if steps else [],
                         "field": row.get("field"), "subfield": row.get("subfield")})
        catalog[split] = {"main_problem_count": len(rows), "metadata": data}
    write_new(ACCOUNT / "asset-schema-v1.json", {"catalog": catalog, "source_files": [str(path.relative_to(target)) for path in target.rglob("*") if path.is_file()],
                                              "test_problem_content_printed": False, "numeric_targets_loaded": False})
    print(json.dumps({"dev": catalog["dev"]["main_problem_count"], "test": catalog["test"]["main_problem_count"],
                      "example_schema_only": catalog["dev"]["metadata"][0],
                      "files": [str(path.relative_to(target)) for path in target.rglob("*") if path.is_file()]}, indent=2))


if __name__ == "__main__":
    main()
