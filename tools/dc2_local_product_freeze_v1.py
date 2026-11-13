"""Freeze author engineering cases before any product model response; not a benchmark."""
from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, authority, sha, write

CSV = "compound_id,smiles\naspirin,CC(=O)Oc1ccccc1C(=O)O\ncaffeine,Cn1c(=O)c2c(ncn2C)n(C)c1=O\nethanol,CCO\nbenzene,c1ccccc1\nbenzoic_acid,O=C(O)c1ccccc1\ninvalid,bad!\nethanol,CCO\n"

def main():
    authority()
    assert not (PUBLIC / "product-acceptance-freeze-v1.json").exists()
    cases = []
    for key, value, selected, en, th in (
        ("molecular_weight_max", 100, ["ethanol", "benzene"], "Select compounds with molecular weight at most 100 g/mol. Keep other limits at the supplied defaults.", "เลือกสารที่มีมวลโมเลกุลไม่เกิน 100 g/mol ส่วนเกณฑ์อื่นใช้ค่าเริ่มต้นที่ให้มา"),
        ("logp_max", 0, ["caffeine", "ethanol"], "Select compounds with LogP at most zero. Keep other limits at the supplied defaults.", "เลือกสารที่มี LogP ไม่เกินศูนย์ ส่วนเกณฑ์อื่นใช้ค่าเริ่มต้นที่ให้มา"),
        ("tpsa_max", 0, ["benzene"], "Select compounds with TPSA at most zero square angstroms. Keep other limits at the supplied defaults.", "เลือกสารที่มี TPSA ไม่เกินศูนย์ตารางอังสตรอม ส่วนเกณฑ์อื่นใช้ค่าเริ่มต้นที่ให้มา"),
    ):
        parameters = {"molecular_weight_max": 500, "logp_max": 5, "tpsa_max": 140, key: value}
        for locale, goal in (("en", en), ("th", th)):
            cases.append({"id": key + "-" + locale, "goal": goal, "locale": locale, "expected_parameters": parameters, "expected_selected_ids": selected})
    files = list((ROOT / "src/curaloop_rd/local_agent_v1").glob("*.py")) + [ROOT / "api/local_workflow_routes_v1.py"]
    freeze = {"schema": "curaloop.local-workflow.author-acceptance.v1", "scope": "Six author-selected bilingual software cases; NOT an external benchmark, efficacy test or independent validation", "csv_text": CSV, "defaults": {"molecular_weight_max": 500, "logp_max": 5, "tpsa_max": 140}, "expected_counts": {"input_rows": 7, "valid": 5, "rejected": 2}, "cases": cases, "scoring": "One attempt per case. Exact typed parameters, COMPLETED, exact selected ID set, current artifact checks and nonempty genuine GPU provider receipts. Preserve failed cases; no outcome-driven repair/rerun.", "deterministic_checks": "One per unique parameter set; actual RDKit conformance, not research controls", "model_call_cap": 12, "model": "Typhoon 2.1 Gemma3 12B Q4_K_M", "source_sha256": {p.relative_to(ROOT).as_posix(): sha(p) for p in files}, "external_comparison": "NOT_RUN", "primary_effect": "NOT_ESTIMABLE"}
    write(PUBLIC / "product-acceptance-freeze-v1.json", freeze)
    write(TASK / "product-acceptance-freeze-pin-v1.json", {"sha256": sha(PUBLIC / "product-acceptance-freeze-v1.json")})
    print("PASS_AUTHOR_ACCEPTANCE_FROZEN_NOT_RESEARCH_PROTOCOL")

if __name__ == "__main__":
    main()
