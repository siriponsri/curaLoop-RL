"""Record the SI/source-name conflict without reading any campaign payload."""
# ruff: noqa: E402

import csv
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, read, sha, start
from tools.cf1_source_inventory_v1 import fetch


def main():
    commit = "04c58e85188e724ec5ff44cbed2e7b960f6f3df3"
    # Table S3, pp6-7, visually checked against the rendered owner-supplied SI.
    names = ["transporter", "transcription", "transcription_2", "GPCR_2", "GPCR_3", "ion_channel",
             "ion_channel_2", "ion_channel_3", "kinase", "GPCR", "serine", "transcription_3",
             "ubiquitin", "splicing", "channel_atp", "cysteine_protease", "zinc_finger"]
    pairs = [(485270, 492964), (1040, 1254), (628, 677), (1672, 2032), (449739, 489005),
             (2239, 2287), (2661, 2821), (488975, 493221), (504558, 588343), (2098, 2382),
             (624304, 624474), (485273, 493155), (873, 1431), (2221, 435010), (720511, 743267),
             (686996, 720632), (1832, 1960)]
    table = dict(zip(pairs, names, strict=True))
    roster = list(csv.DictReader((TASK / "source/metadata/Logs/dataset_metadata.csv").open(encoding="utf-8")))
    comparisons = []
    for row in roster:
        pair = (int(row["Primary  HTS AID"]), int(row["Confirmatory HTS AID"]))
        comparisons.append({"primary_aid": pair[0], "confirmation_aid": pair[1],
                            "repository_codename": row["Codename"], "si_table_s3_codename": table[pair],
                            "same_codename": row["Codename"] == table[pair]})
    tree = {r["path"]: r for r in read(TASK / "source/tree.json")["tree"] if r["type"] == "blob"}
    evidence = []
    for name in ("channel_atp", "cysteine_protease", "ion_channel_3", "zinc_finger"):
        relative = "Logs/cleanup/" + name + ".txt"
        body = fetch(f"https://raw.githubusercontent.com/dahvida/AIC_Finder/{commit}/{relative}",
                     "metadata/" + relative, maximum=32768)
        assert hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest() == tree[relative]["sha"]
        match = re.search(r"AID\s+(\d+)\s+and\s+(\d+)", body.decode())
        assert match
        row = next(r for r in roster if r["Codename"] == name)
        pair = (int(match.group(1)), int(match.group(2)))
        assert pair == (int(row["Primary  HTS AID"]), int(row["Confirmatory HTS AID"]))
        evidence.append({"repository_codename": name, "primary_aid": pair[0], "confirmation_aid": pair[1],
                         "cleanup_log_sha256": sha(TASK / "source/metadata" / relative),
                         "git_blob_authenticated": True, "conflicts_with_si_codename": name != table[pair]})
    summary = {"status": "STOP_DEPENDENT_INTAKE_SOURCE_CONCORDANCE_OWNER_DECISION", "si": read(TASK / "si-receipt-v1.json"),
        "si_table_pages_visually_checked": [6, 7], "campaign_pairs_in_both_sources": len(comparisons),
        "codename_conflicts": sum(not r["same_codename"] for r in comparisons),
        "comparisons": comparisons, "cleanup_log_crosschecks": evidence,
        "campaign_payload_downloads": 0, "confirmation_values_analyzed": False,
        "source_correction_applied": False, "final16_access": False}
    new(TASK / "si-concordance-v1.json", summary)
    new(PUBLIC / "si-concordance-v1.json", summary)
    print({"status": summary["status"], "pairs": len(comparisons), "codename_conflicts": summary["codename_conflicts"],
           "cleanup_log_crosschecks": evidence})


if __name__ == "__main__":
    guard = start("si-source-concordance", 120, 300)
    try:
        main()
        finish("si-source-concordance", guard, "PASS_AUDIT_SOURCE_CONFLICT_FOUND")
    except BaseException:
        finish("si-source-concordance", guard, "FAIL")
        raise
