"""Trusted selected-row label projection. Never return final outcomes."""

import gzip
import hashlib
import io
import json
import math

from research.benchmark_v3.prepare_features_v2 import canonical


class LabelAccessError(Exception):
    """Fixed codes only; arbitrary source rows never reach exception text."""


def source_boolean(value):
    # Pinned FS-Mol loader uses bool(float(Property)); require binary numeric
    # semantics and abort globally on unexpected values, rather than truthiness.
    if type(value) not in (str, bool, int, float):
        raise LabelAccessError("UNSUPPORTED_SOURCE_BOOLEAN_SEMANTICS")
    try:
        number = float(value)
    except (ValueError, OverflowError):
        raise LabelAccessError("UNSUPPORTED_SOURCE_BOOLEAN_SEMANTICS") from None
    if not math.isfinite(number) or number not in (0.0, 1.0):
        raise LabelAccessError("UNSUPPORTED_SOURCE_BOOLEAN_SEMANTICS")
    return bool(number)


def project_labels(feature, compressed, limits):
    # This check precedes decoding and applies even to directly invoked helpers.
    if feature.get("role") not in ("development", "validation"):
        raise LabelAccessError("FORBIDDEN_OUTCOME_ROLE")
    if hashlib.sha256(compressed).hexdigest() != feature["member_sha256"]:
        raise LabelAccessError("MEMBER_HASH_MISMATCH")
    wanted = {r["source_row"]: r for r in feature["records"]}
    if len(wanted) != len(feature["records"]):
        raise LabelAccessError("DUPLICATE_SELECTED_SOURCE_ROW")
    labels, expanded = {}, 0
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
            for index in range(limits["maximum_rows_per_assay"] + 1):
                line = stream.readline(limits["maximum_row_bytes"] + 1)
                if not line:
                    break
                expanded += len(line)
                if (index >= limits["maximum_rows_per_assay"] or
                    len(line) > limits["maximum_row_bytes"] or
                    expanded > limits["maximum_member_expanded_bytes"]):
                    raise LabelAccessError("SOURCE_MEMBER_LIMIT")
                if index not in wanted:
                    continue
                row = json.loads(line)
                record = wanted[index]
                if (not isinstance(row, dict) or row.get("Assay_ID") != feature["task_id"] or
                    type(row.get("SMILES")) is not str or canonical(row["SMILES"]) != record["canonical_smiles"]):
                    raise LabelAccessError("SELECTED_ROW_IDENTITY_MISMATCH")
                value = source_boolean(row.get("Property"))
                cid = record["candidate_id"]
                if cid != "s-" + hashlib.sha256(record["canonical_smiles"].encode()).hexdigest():
                    raise LabelAccessError("CANONICAL_CANDIDATE_ID_MISMATCH")
                labels[cid] = value
    except (ValueError, UnicodeError, gzip.BadGzipFile, EOFError, OSError):
        raise LabelAccessError("INVALID_SOURCE_MEMBER") from None
    if len(labels) != len(wanted):
        raise LabelAccessError("MISSING_SELECTED_ROWS")
    return labels


def prepare_role(role, protocol, root, output):
    from research.benchmark_v3.prepare_features_v2 import sha_file, write_new
    from .identity import PACKET_RELATIVE, RUN_RELATIVE, verify_selection

    # Reject before opening even an index/member. Validation needs its later gate.
    if role not in protocol["permitted_outcome_roles"] or role not in ("development", "validation"):
        raise LabelAccessError("FORBIDDEN_OUTCOME_ROLE")
    if protocol["status"] != "FROZEN_BEFORE_GOAL4_OUTCOMES":
        raise LabelAccessError("PROTOCOL_NOT_FROZEN")
    if role == "validation":
        try:
            verify_selection(root, protocol)
        except (OSError, ValueError, KeyError):
            raise LabelAccessError("VALIDATION_REQUIRES_SELECTION_FREEZE") from None
    allowed = (root / RUN_RELATIVE / "private-inputs" / role).resolve()
    if output.resolve() != allowed:
        raise LabelAccessError("PRIVATE_OUTPUT_PATH_REQUIRED")
    try:
        ignored = json.loads((root / PACKET_RELATIVE / f"ignored-path-{role}-v1.json").read_text())
        if (ignored["status"] != "PASS_GIT_IGNORE_PREFLIGHT" or
            ignored["output_relative"] != output.relative_to(root).as_posix() or
            sha_file(root / ".gitignore") != ignored["gitignore_sha256"]):
            raise ValueError("Ignore proof mismatch.")
    except (OSError, KeyError, ValueError):
        raise LabelAccessError("PRIVATE_OUTPUT_NOT_VERIFIED_IGNORED") from None
    manifest_path = root / protocol["cohort_manifest"]
    if sha_file(manifest_path) != protocol["cohort_manifest_sha256"]:
        raise LabelAccessError("COHORT_MANIFEST_MISMATCH")
    manifest = json.loads(manifest_path.read_text())
    if manifest["status"] != "PASS_FEATURE_COHORT":
        raise LabelAccessError("COHORT_GATE_NOT_PASSED")
    raw = manifest_path.parent.parent
    config_path = root / "research/configs/goal3_feature_preparation_v2.json"
    if sha_file(config_path) != protocol["cohort_config_sha256"]:
        raise LabelAccessError("COHORT_CONFIGURATION_MISMATCH")
    limits = json.loads(config_path.read_text())
    if sha_file(raw / "fsmol.tar") != manifest["identities"]["archive_sha256"]:
        raise LabelAccessError("ARCHIVE_HASH_MISMATCH")
    header_path = raw / "header-audit-v2.json"
    if sha_file(header_path) != manifest["identities"]["header_index_sha256"]:
        raise LabelAccessError("HEADER_INDEX_MISMATCH")
    headers = {r["name"]: r for r in json.loads(header_path.read_text())["members"] if r["kind"] == "file"}
    selected = [a for a in manifest["selected_assays"] if a["role"] == role]
    output.mkdir(exist_ok=False)
    receipts = []
    with (raw / "fsmol.tar").open("rb") as archive:
        for assay in selected:
            feature_path = (manifest_path.parent / assay["feature_file"]).resolve()
            if feature_path.parent != manifest_path.parent.resolve() or sha_file(feature_path) != assay["feature_sha256"]:
                raise LabelAccessError("FEATURE_HASH_OR_PATH_MISMATCH")
            feature = json.loads(feature_path.read_text())
            if feature["role"] != role or feature["task_id"] != assay["assay_id"] or feature["family_id"] != assay["family_id"]:
                raise LabelAccessError("FEATURE_ROLE_IDENTITY_MISMATCH")
            header = headers[feature["source_member"]]
            if header["bytes"] > limits["maximum_member_compressed_bytes"]:
                raise LabelAccessError("COMPRESSED_MEMBER_LIMIT")
            archive.seek(header["data_offset"])
            data = archive.read(header["bytes"])
            if len(data) != header["bytes"]:
                raise LabelAccessError("TRUNCATED_MEMBER")
            labels = project_labels(feature, data, limits)
            payload = {
                "schema_version": "curaloop.goal4.private-task.v1",
                "task_id": feature["task_id"], "role": role, "family_id": feature["family_id"],
                "feature_sha256": assay["feature_sha256"], "member_sha256": feature["member_sha256"],
                "records": [{"candidate_id": r["candidate_id"], "morgan_on_bits": r["morgan_on_bits"],
                             "active": labels[r["candidate_id"]]} for r in feature["records"]],
            }
            path = output / (feature["task_id"] + ".json")
            write_new(path, payload)
            receipts.append({"task_id": feature["task_id"], "role": role, "family_id": feature["family_id"],
                             "rows": len(labels), "sha256": sha_file(path), "file": path.name})
    write_new(output / "manifest.json", {"role": role, "tasks": receipts, "final_outcomes_prepared": False})
    return receipts
