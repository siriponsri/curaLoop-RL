# UX Blueprint (ภาษาไทย) — Portfolio Demo สำหรับผู้ฟังด้านเภสัชกรรม

**แนวคิด:** ผู้ชมควรรู้ใน 30 วินาทีว่าโครงการนี้ตอบคำถามอะไร และรู้ใน 2 นาทีว่าผลมาจากข้อมูลจำลองหรือผลการทดสอบย้อนหลัง ไม่ใช่ผลทดลองในองค์การเภสัชกรรม

## Design principles

- ใช้ธีม Research Workbench: พื้นหลังเรียบ ขาว/เทาอ่อน ข้อความอ่านง่าย accent สีเขียวอมฟ้าไม่ฉูดฉาด กราฟไม่ซ้อนเกิน 3 เส้นในจอหลัก
- ใช้ภาษาไทยที่เข้าใจง่ายและวงเล็บศัพท์เทคนิคอังกฤษครั้งแรก เช่น `สารที่พบฤทธิ์ใน assay (Active Hit)` ไม่เรียกยาใหม่
- แสดง provenance banner ถาวร: `ข้อมูลจำลอง | Synthetic demo` หรือ `ข้อมูลทดสอบย้อนหลังสาธารณะ | Historical public assay`
- แสดง `Demo only; not an official GPO system; not validated for wet-lab or clinical use` ใน About/Export และด้านล่างจอ
- ตัวเลขที่ขึ้นต้น 'ราคา' ต้องเป็น **หน่วยต้นทุนจำลอง** (cost units) ห้ามใส่ `บาทที่ประหยัด` โดยไม่มีหลักฐานจริง

## Tab 1 — Overview / ทำไมต้องเลือกสาร

**Hero:** `ถ้าทดสอบสารได้เพียง 30 จาก 240 ตัว เราจะเริ่มจากตัวไหน?`

แสดง 4 ขั้นตอน: คัดเลือกสาร → ส่งทดสอบจำลอง → เปิดเผยผลเฉพาะที่ครบกำหนด → ปรับคำแนะนำรอบใหม่

ค่าสรุปขนาดเล็ก: `จำนวนสารทั้งหมด`, `งบประมาณทดสอบ`, `สารที่ทดสอบแล้ว`, `สารที่พบฤทธิ์จากผลที่เปิดเผยแล้ว` พร้อมคำอธิบายทุกค่าจาก event log เท่านั้น

## Tab 2 — Scenario / ตั้งเงื่อนไข

Fields: `Dataset origin`, `assay/target`, `seed`, `initial labeled seed`, `budget in cost units`, `batch size`, `simulated result delay`, `policy`, `scenario flags`. Validation under each field. Three explainers:

1. ตัวอย่างนี้ใช้ต้นทุนและเวลาจำลอง ไม่ใช่ค่าใช้จ่ายหรือเวลาทำงานของหน่วยงาน
2. ผล assay ถูกซ่อนไว้จนกว่าจะเลือกทดสอบและถึงกำหนดเปิดเผย
3. นโยบายแต่ละแบบจะเริ่มด้วยข้อมูลตั้งต้นและงบประมาณเท่ากัน

Primary CTA `เริ่มการจำลอง` and secondary CTA `คืนค่าเริ่มต้น`.

## Tab 3 — Screening Run / ดูการตัดสินใจทีละรอบ

Left: timeline (`requested → pending → delivered`), queue duration and round status. Main: table of suggested candidate IDs, selection rationale from policy, known features; do **not** render private hidden oracle labels. Right: budget reserve/spent/remaining and confirmed hits delivered. Actions: `เลือกครั้งถัดไป`, `เลื่อนเวลาจำลอง`, `เริ่มใหม่`. All must affect state, reject invalid action with explanation.

**Evidence strip:** seed, policy implementation, data provenance, model version, code SHA, simulation timestamp.

## Tab 4 — Compare & Export / เปรียบเทียบแบบยุติธรรม

Primary line chart: **Confirmed hits (delivered)** vs **spent cost units** for Random, Greedy and Uncertainty, using same seed/pool/initial labels. Secondary charts: pending queue and simulated elapsed time (not real-time), selected diversity if computed. Show per-policy table with `Budget consumed`, `Confirmed hits`, `Simulation time`, `Seed` and `Limitations`.

Export JSON/CSV from real log and manifest. Clear note: single run is illustrative; it is NOT evidence that a policy generally beats competitors. When many seeds later available, add aggregate effect size and confidence intervals.

## First demo narrative — 5 to 7 minutes

1. **0:00–0:45:** ปัญหาการเลือกสารภายใต้ทรัพยากรจำกัด และขอบเขตข้อมูลจำลอง
2. **0:45–1:30:** อธิบาย 'สารที่ยังไม่รู้ผล' กับ 'ผลที่เปิดเผยแล้ว'
3. **1:30–2:30:** ตั้ง budget 30 units, batch 5, delay 1–2 simulation steps
4. **2:30–4:00:** รันรอบจริง 2–3 รอบ ดู pending vs delivered
5. **4:00–5:30:** เปรียบเทียบ 3 นโยบายภายใต้เงื่อนไขเท่ากัน และชี้ข้อจำกัด single run
6. **5:30–6:30:** อธิบายอนาคตของ RL meta-policy และ Digital Twin maturity อย่างไม่กล่าวเกินหลักฐาน
7. **6:30–7:00:** เปิด GitHub local repo/README และความสามารถที่ตรวจสอบซ้ำได้

## Accessibility and error states

Use labels, readable typography (at least 14px for main text), keyboard-friendly controls, accessible chart colors and patterns. Render explicit states: no positive seed, zero budget, pending-only, unavailable RDKit, dataset download refused, invalid SMILES and no results. Never show made-up metrics to fill an empty chart.
