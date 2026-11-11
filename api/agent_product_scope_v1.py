"""Product-only capability preflight, separate from frozen research engine v1.

Uses the existing strong deterministic capability rule and real public source
adapter. Additional Thai phrases are conservative interface rules, not a
general intent classifier or evidence of language-model safety performance.
"""

import re
import time

from curaloop_rd.agent_rd.engine import deterministic
from curaloop_rd.agent_rd.evidence import collect, comparisons
from curaloop_rd.agent_rd.verifier import verify

POLICY_ID = "product-scope-preflight-v1"
DENIAL_FALLBACK = "DETERMINISTIC_CAPABILITY_PREFLIGHT_DENIAL"
THAI_UNAVAILABLE = (
    r"(?:ผล|ข้อมูล)(?:ลัพธ์)?(?:ที่)?(?:ถูก)?ซ่อน",
    r"ผล(?:ลัพธ์)?(?:ที่)?ยังไม่ออก",
    r"(?:ตัวตน|รายชื่อ)(?:ของ)?สาร",
    r"(?:ข้อมูล|สาร)(?:รายตัว|ส่วนตัว)",
    r"ประหยัด.{0,12}(?:แล็บ|ห้องปฏิบัติการ)",
    r"(?:ประสิทธิผล|ประโยชน์).{0,12}คลินิก",
    r"ผลตอบแทน.{0,12}(?:เงิน|ลงทุน)",
)


def inspect_scope(spec):
    start, cpu = time.monotonic(), time.thread_time()
    evidence = collect(spec)
    derived = comparisons(evidence)
    thai_match = any(re.search(pattern, spec.goal) for pattern in THAI_UNAVAILABLE)
    probe = spec.model_copy(update={"goal": "Provide private CF1 compound identities"}) if thai_match else spec
    reference = deterministic(probe, evidence, derived)
    denied = reference["action"] == "abstain"
    decision = {"policy_id": POLICY_ID, "decision": "DENY" if denied else "ALLOW",
                "basis": "conservative_thai_capability_phrase" if thai_match else "existing_deterministic_capability_rule",
                "frozen_research_condition": False, "model_called_by_policy": False,
                "source_evidence_id": evidence["evidence_id"],
                "policy_wall_seconds": time.monotonic() - start,
                "policy_thread_cpu_seconds": time.thread_time() - cpu}
    if not denied:
        return {"decision": decision}
    checked = verify(reference, evidence, derived)
    assert checked["valid"] and reference.get("values") == {}
    return {"decision": decision, "report": reference, "evidence": evidence, "derived": derived, "verification": checked}
