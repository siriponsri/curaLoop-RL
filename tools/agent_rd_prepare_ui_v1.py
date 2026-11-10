"""Add EN/TH mission labels, retaining the original translation catalogue."""

import json

from agent_rd_admin_v1 import ROOT, TASK, write

TH = {
    "Agent mission control": "ศูนย์ควบคุมงานวิจัย",
    "AGENT RD / LOCAL EVIDENCE": "AGENT RD / หลักฐานภายในเครื่อง",
    "From question to evidence.": "จากคำถาม สู่หลักฐาน",
    "One bounded mission. Trace every source, calculation and decision.": "งานวิจัยที่กำหนดขอบเขตชัด ตรวจย้อนกลับได้ทุกแหล่งข้อมูล การคำนวณ และการตัดสินใจ",
    "Read-only science": "อ่านหลักฐาน ไม่สั่งทดลอง",
    "Retrospective CF1 aggregates only. No private compounds, hidden outcomes or real laboratory actions.": "ใช้เฉพาะผลสรุปย้อนหลัง CF1 ไม่เปิดสารส่วนตัว ผลที่ซ่อน หรือสั่งงานห้องแล็บจริง",
    "Open source study": "เปิดหลักฐานต้นทาง",
    "Mission needs attention": "งานวิจัยนี้ต้องตรวจสอบ",
    "Your research question": "คำถามวิจัยของคุณ",
    "Mission goal": "โจทย์ที่ต้องการศึกษา",
    "Execution mode": "รูปแบบประมวลผล",
    "Real model · CPU via SSH": "โมเดลจริง · ใช้ CPU ผ่าน SSH",
    "Deterministic · no model": "คำนวณตามกฎ · ไม่ใช้โมเดล",
    "Compare all five budgets": "เปรียบเทียบงบทั้ง 5 ระดับ",
    "Allow an immutable local dossier for this mission": "อนุญาตจัดเก็บรายงานงานนี้ภายในเครื่อง โดยไม่เขียนทับฉบับเดิม",
    "Run research mission": "เริ่มงานวิจัย",
    "Opening this page starts nothing. The model needs an active authorized session; no paid fallback is used.": "การเปิดหน้านี้ไม่เริ่มประมวลผล โมเดลต้องมี session ที่อนุญาตและยังใช้งานได้ ไม่มีการเปลี่ยนไปใช้บริการเสียเงินอัตโนมัติ",
    "Try another question": "ลองโจทย์อื่น",
    "Explore the budget tradeoff": "สำรวจผลเมื่อเปลี่ยนงบ",
    "Test the evidence boundary": "ทดสอบขอบเขตหลักฐาน",
    "A mission you can inspect.": "งานวิจัยที่ตรวจสอบได้",
    "Ask a question, inspect the evidence trail, then open the verified result or an explicit abstention.": "ตั้งคำถาม ตรวจเส้นทางหลักฐาน แล้วอ่านผลที่ตรวจแล้ว หรือเหตุผลที่ยังสรุปไม่ได้",
    "Inspect": "ตรวจหลักฐาน",
    "Verify": "ตรวจข้ออ้าง",
    "Report": "จัดทำรายงาน",
    "No generated results are shown before execution.": "ยังไม่แสดงผลที่สร้างขึ้นก่อนเริ่มประมวลผล",
    "ACTUAL MISSION STATE": "สถานะงานที่บันทึกจริง",
    "Revision": "รุ่นข้อมูล",
    "Model calls": "ครั้งที่เรียกโมเดล",
    "Tool calls": "ครั้งที่เรียกเครื่องมือ",
    "Recorded model tokens": "โทเคนโมเดลที่บันทึกได้",
    "The evidence trail": "เส้นทางหลักฐาน",
    "Recorded events": "เหตุการณ์ที่บันทึก",
    "Waiting for the actual CPU model response. Closing this tab does not cancel the bounded mission.": "กำลังรอคำตอบจริงจากโมเดลบน CPU การปิดแท็บไม่ยกเลิกงานที่กำหนดเพดานไว้",
    "Execution failed": "ประมวลผลไม่สำเร็จ",
    "The failed attempt is retained. No mock result or provider substitution was used.": "เก็บรอบที่ล้มเหลวไว้ ไม่มีการใช้ผลจำลองหรือเปลี่ยนผู้ให้บริการแทน",
    "RELEASED RESULT": "ผลที่ระบบปล่อยให้แสดง",
    "The evidence does not support that conclusion.": "หลักฐานยังไม่รองรับข้อสรุปนั้น",
    "Source-backed values": "ค่าที่ตรวจตรงกับหลักฐาน",
    "Released scientific values": "ค่าทางวิทยาศาสตร์ที่ระบบปล่อยให้แสดง",
    "Value / comparison key": "รหัสค่า / การเปรียบเทียบ",
    "Observed or derived value": "ค่าจากข้อมูลหรือการคำนวณ",
    "Numbers use rounded source operands. Deltas are right minus left; HB/DB are fractions. These are historical counts, not laboratory savings.": "ใช้ค่าต้นทางที่ปัดเศษ ผลต่างเป็นค่าขวาลบซ้าย HB/DB เป็นสัดส่วน ตัวเลขคือข้อมูลย้อนหลัง ไม่ใช่ต้นทุนแล็บที่ประหยัดได้",
    "A source check is not proof that the model fully answered the question. Task completion is scored separately in the research evaluation.": "การตรวจค่าตรงกับแหล่งข้อมูลไม่ได้พิสูจน์ว่าโมเดลตอบโจทย์ครบ การประเมินวิจัยให้คะแนนความสำเร็จแยกต่างหาก",
    "Prepare local dossier": "จัดทำรายงานภายในเครื่อง",
    "Open dossier": "เปิดรายงาน",
    "Full trace": "บันทึกการทำงานทั้งหมด",
    "Manifest": "รายการไฟล์และรหัสตรวจสอบ",
    "Reconcile and resume": "ตรวจสถานะเดิมแล้วทำต่อ",
    "Inspect receipts and unverified proposals": "ดูหลักฐานการทำงานและข้อเสนอที่ยังไม่ยืนยัน",
    "Unverified model proposal": "ข้อเสนอโมเดลที่ยังไม่ยืนยัน",
    "Awaiting provider response": "กำลังรอคำตอบจากโมเดล",
    "Recorded local missions": "งานวิจัยที่บันทึกในเครื่อง",
    "Author computation, not independent validation": "ตรวจเชิงคำนวณโดยผู้พัฒนา ไม่ใช่การรับรองจากผู้ประเมินอิสระ",
    "No saved missions yet.": "ยังไม่มีงานวิจัยที่บันทึกไว้",
    "DRAFT": "ยังไม่เริ่มงาน", "VALIDATING": "กำลังตรวจขอบเขต", "PLAN_READY": "แผนพร้อม",
    "MODEL_REQUESTED": "กำลังรอโมเดลจริง", "MODEL_RETURNED": "ได้รับคำตอบโมเดลแล้ว",
    "TOOL_COMPLETED": "เครื่องมือทำงานเสร็จ", "VERIFYING": "กำลังตรวจข้ออ้าง",
    "COMPLETED": "เสร็จสิ้น", "ABSTAINED": "งดสรุปผล", "FAILED": "ไม่สำเร็จ",
    "CANCELLED": "ยกเลิกแล้ว", "INTERRUPTED_RECOVERABLE": "งานหยุดค้าง ตรวจสถานะเพื่อทำต่อได้",
    "QUEUED": "รอประมวลผล", "PROPOSAL_REJECTED": "ข้อเสนอโมเดลไม่ผ่าน",
}


def main():
    path = ROOT / "frontend/src/locales/th.json"
    original = TASK / "thai-catalogue-before-agent.json"
    if not original.exists():
        original.write_bytes(path.read_bytes())
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(TH)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    write(TASK / "thai-agent-additions-v1.json", {"keys": len(TH), "translations": TH}, True)
    print("PASS appended", len(TH), "EN/TH mission labels")


if __name__ == "__main__":
    main()
