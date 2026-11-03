# Portfolio brief — Thai / English

## Identity

**Project:** CuraLoop-RL — Pharmaceutical Discovery Workbench

**Type:** Independent personal learning / engineering portfolio and research-oriented prototype.

**Presentation context:** May be shown to colleagues or evaluators interested in pharmaceutical R&D at GPO. **No actual organizational endorsement, approval, sponsorship, employment-based ownership or access to GPO operational data is asserted.**

## Thai elevator pitch (30 seconds)

> โครงการนี้เป็นระบบจำลองการคัดเลือกสารสำหรับงานวิจัยและพัฒนายา โดยนำ Machine Learning และแนวคิด Reinforcement Learning มาช่วยตัดสินใจว่าจะเลือกสารใดมาทดสอบต่อ ภายใต้งบประมาณและเวลาที่จำกัด ผู้ใช้งานสามารถเปรียบเทียบวิธีการคัดเลือกหลายแบบผ่าน Dashboard พร้อมตรวจสอบผลลัพธ์ย้อนหลังได้ ขณะนี้เป็นต้นแบบที่ใช้ข้อมูลสาธารณะหรือข้อมูลจำลอง ไม่ใช่ระบบที่เชื่อมต่อกับห้องปฏิบัติการขององค์กร และยังไม่ได้พิสูจน์ว่าช่วยลดต้นทุนจริง

## English elevator pitch

> CuraLoop-RL is a personal proof-of-concept workbench for prioritizing compound-screening experiments. It demonstrates transparent sequential decision-making with machine learning and, at later stages, reinforcement learning under constrained assay budgets and delayed feedback. The retrospective simulator compares policies using public or explicitly synthetic data. No organizational deployment, validated Digital Twin, drug efficacy, or real financial savings is claimed.

## Why a pharmaceutical organization may care

- **Selection efficiency:** simulated trade-offs between screening more diverse candidates and selecting top predicted hits.
- **Resource planning:** understand candidate count, batch limits and feedback delays before proposing experiments.
- **Traceability:** show what policy selected, what it knew at the time, how much simulated budget it used and what historical/simulated results were later revealed.
- **Communication:** provide a visual, accessible framework for cross-functional R&D conversations without requiring the viewer to read RL code.

These are *potential conceptual applications*, not claims that GPO has adopted or requested this workflow.

## Not the same as other domains

Drug discovery **compound screening** differs from formulation optimization, drug manufacturing process control, pharmacovigilance and pharmaceutical quality control. Do not pretend one demo solves all these workflows. Future extensions can be separately validated if legitimate project needs emerge.

## Bilingual terminology for on-screen hints

- Candidate compound = สารที่อยู่ในรายการพิจารณาคัดเลือก
- Target / assay = เป้าหมายหรือวิธีทดสอบฤทธิ์ทางชีวภาพ
- Active (in assay) = ให้ผลเป็นบวกตามเกณฑ์ของการทดสอบนั้น **ไม่ใช่ยาที่ใช้ได้จริง**
- Screening budget = งบประมาณหรือจำนวนการทดสอบที่อนุญาตในสถานการณ์จำลอง
- Policy = กลยุทธ์ที่ใช้เลือกสาร
- Digital-twin-ready simulator = ระบบจำลองที่วางสถาปัตยกรรมเผื่อการเชื่อมโยงข้อมูลจริงในอนาคต

## Review checklist before presentation

- Present as **personal work**, with no GPO logo/brand colors mimicking an official system.
- Screenshots show `SYNTHETIC_ONLY`, `HISTORICAL_PUBLIC_DATA` or other correct provenance flags.
- State any calculated hits or efficiency gains as *observed only within this run and dataset*.
- Distinguish comparison of selecting assay tests from the later steps required to validate a medicine.
- Do not represent GPL/third-party libraries and papers as original creations. Credit and honor applicable licenses.

## Public context link (not organizational validation)

GPO's 2026 innovation/research fund call included medicine/product R&D and AI/mathematical modeling of processes, as independently reported by HSRI: https://www.hsri.or.th/research_grant/research_news/detail/13 . The FY2026 submission window ended May 31, 2026; **do not imply a live funding opportunity**.
