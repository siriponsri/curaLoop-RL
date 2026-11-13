"""Receive the exact numeric asset linked by the official SciCode repository."""
from tools.sc1_control_v1 import ACCOUNT, ROOT, write_new
from tools.sc1_intake_v1 import fetch
import json


def main():
    target = ROOT / "research/raw_data/external-benchmarks/scicode-2024/evaluator-private/test_data.h5"
    record = fetch("https://drive.usercontent.google.com/download?id=17G_k65N_6yFFZ2O-jQH00Lh6iaw3z-AW&export=download&confirm=t", target, 10737418240 - 2097152)
    if record["status"] == "PASS_TRANSPORT_ONLY":
        with target.open("rb") as stream:
            signature = stream.read(8)
        record["hdf5_signature_valid"] = signature == b"\x89HDF\r\n\x1a\n"
        record["matches_official_folder_declared_bytes"] = record["bytes"] == 1049345865
        if not record["hdf5_signature_valid"] or not record["matches_official_folder_declared_bytes"]:
            record["status"] = "FAIL_SOURCE_IDENTITY"
    write_new(ACCOUNT / "numeric-download-v1.json", record)
    print(json.dumps(record))
    if record["status"] != "PASS_TRANSPORT_ONLY":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
