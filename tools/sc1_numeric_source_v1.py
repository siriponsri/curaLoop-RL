"""Inspect the official public numeric-data folder, without loading target values."""
import json
import re
from tools.sc1_control_v1 import ACCOUNT, ROOT, write_new
from tools.sc1_intake_v1 import fetch


def main():
    path = ACCOUNT / "numeric-source-v1" / "official-folder.html"
    receipt = fetch("https://drive.google.com/drive/folders/1W5GZW6_bdiDAiipuFMqdUhvUaHIj6-pR?usp=drive_link", path, 4194304)
    write_new(path.parent / "receipt.json", receipt)
    print(json.dumps(receipt))
    if receipt["status"] != "PASS_TRANSPORT_ONLY":
        raise SystemExit(2)
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer("test_data", text))
    print(json.dumps({"filename_matches": len(matches), "metadata_contexts": [text[max(0, m.start()-130):m.end()+150] for m in matches[:6]]}))


if __name__ == "__main__":
    main()
