# Benchmark ที่ใช้ข้อมูลจริง และหลักฐานที่ตรวจแล้ว

ตรวจแหล่งต้นฉบับวันที่ 3 พฤศจิกายน 2026 (Asia/Bangkok) การมี paper รองรับแหล่งข้อมูลไม่ได้รับรองว่า CuraLoop-RL หรือยาที่เลือกมีประสิทธิผล

| Benchmark | แหล่งต้นฉบับ / paper | ใช้ประเมินอะไร | สถานะในรุ่นนี้ |
|---|---|---|---|
| MoleculeNet HIV / NCI DTP | Wu et al., Chemical Science 2018, DOI [10.1039/C7SC02664A](https://doi.org/10.1039/C7SC02664A); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5868307/) | การจัดลำดับสารจากผล assay จริงย้อนหลัง; predictor scaffold split | โหลดจริง ตรวจโครงสร้างจริง และรวมชุด replay 1,200 โมเลกุลใน package |
| Therapeutics Data Commons HTS HIV | Huang et al., NeurIPS Datasets & Benchmarks 2021, [paper](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/4c56ff4ce4aaf9573aa5dff913df997a-Abstract-round1.html); [dataset documentation](https://tdcommons.ai/single_pred_tasks/hts/#hiv) | แหล่งอ้างอิง task, splits และสิทธิ์ข้อมูล | หน้า HIV ระบุ CC BY 4.0; attribution และ changes บันทึกใน manifest |
| LIT-PCBA | Tran-Nguyen et al., JCIM 2020, DOI [10.1021/acs.jcim.0c00155](https://doi.org/10.1021/acs.jcim.0c00155); [official site](https://lab.drugdesign.unistra.fr/datasets/lit-pcba/) | หลาย protein targets, active/inactive ที่ผ่านการคัดกรอง; เหมาะทดสอบ virtual screening ระดับวิจัย | ตรวจ paper/site แล้ว มีแผน ingestion และข้อกำหนด; ไม่แจก raw data เพราะหน้าแหล่งข้อมูลยังไม่ให้ข้อกำหนด redistribution ที่ชัดเจน |
| Tox21 (MoleculeNet) | Wu et al., ข้างต้น; [TDC toxicity](https://tdcommons.ai/single_pred_tasks/tox/) | stress-response/nuclear-receptor toxicity endpoints ที่แยกกัน | ใช้เป็นตัวเลือกการวิจัยที่ประเมินแล้ว ไม่รวมใน software release นี้; ต้องตรวจสิทธิ์เฉพาะไฟล์และ missing-label handling ก่อน |

## สิ่งที่ดาวน์โหลดและทำจริง

- Source: `https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/HIV.csv` เป็น mirror ของ DeepChem/MoleculeNet ไม่ใช่ API ของหน่วยงานไทย
- Source SHA256: `9ffa7fe57dc86c342627ee1d5255e937e2ab812393c73c4d16c697022f6e1d22` จำนวนจริง 41,127 แถว ไม่ใช้ตัวเลข 41,913 จาก paper มาแทนจำนวนของไฟล์นี้
- RDKit อ่าน SMILES ไม่ได้ 7 แถว เหลือ 41,120 แถว ไม่พบ canonical duplicate หรือ label conflict ตามกฎที่ใช้
- สุ่ม 1,200 แถวด้วย `random.Random(20261103).sample` หลังตรวจความถูกต้อง โดยไม่ stratify หรือคัดด้วย activity
- Seed labels ใน replay จริงสุ่มแบบ uniform จาก pool ไม่รับประกันว่ามีสองคลาส จึงอาจเห็น `FALLBACK_RANDOM_ONE_CLASS`
- Morgan radius 2 / 1024 bits และ Bemis–Murcko scaffold ถูกคำนวณจากโครงสร้างจริงก่อนทำ replay ไม่ใช้ activity เป็น feature
- ค่าใช้จ่าย, batch capacity, delay และ missingness เป็น **สมมติฐานจำลอง** แม้ assay labels จะเป็นข้อมูลจริง
- การขอ TDC Dataverse file ID 4259593 ตอบ HTTP 403 ใน environment นี้ จึงใช้ DeepChem mirror ที่ดาวน์โหลดได้จริง; ไม่อ้างว่าได้ดาวน์โหลดจาก TDC

## ความหมายของ label

[NCI DTP](https://wiki.nci.nih.gov/spaces/NCIDTPdata/pages/158204006/AIDS+Antiviral+Screen+Data) ระบุ CA = confirmed active, CM = confirmed moderately active, CI = confirmed inactive; MoleculeNet รวม CA และ CM เป็น positive และ CI เป็น negative ไม่ใช่ข้อมูลยืนยันประสิทธิผลทางคลินิก

## สองวิธีประเมินที่แยกจากกัน

1. **Sequential historical replay:** policy ไม่เห็น labels นอก seed และผลที่ส่งคืนแล้ว ทุกวิธีใช้ pool, seed labels, feature representation, งบ, delay และ capacity เดียวกัน Primary metric = unique delivered active hits เทียบต้นทุนที่ชำระแล้ว; paired seeds 0–9; เทียบ 5 policies และบันทึกทุก event
2. **Predictor audit:** evaluator สร้าง whole-scaffold split แบบกำหนดไว้ล่วงหน้าโดย hash ของ scaffold กับ seed 42, ประมาณ train/test 80/20; fit scaler และ logistic บน train เท่านั้น รายงาน AUROC, average precision และ Brier เมื่อมีทั้งสองคลาส ไม่มีโมเดลหรือ labels จาก evaluator ถูกนำกลับไปให้ policy

Split และ subset เป็นของโครงการนี้ ไม่ใช่ official MoleculeNet/TDC leaderboard split คะแนนไม่ควรถูกนำไปเทียบตรงกับตารางใน paper; การวัด 10 seeds บน assay เดียววัด variability ของ initialization ไม่ใช่ biological replication 10 ชุด

## Trained controller: ขอบเขตที่พิสูจน์ได้

Q-learning และ contextual bandit ฝึกอย่างละ 160 episodes บน synthetic_linear/shift, episode seeds 10000–10159 ไม่มี HIV labels ในการฝึก controller ค่า Q/average reward, action counts และ episode returns อยู่ใน checkpoint JSON พร้อม hash การนำมาเลือก strategy บน HIV คือการทดสอบ transfer เบื้องต้น ไม่ใช่หลักฐานว่าถ่ายโอนสำเร็จหรือชนะ baseline

## LIT-PCBA ingestion ที่ต้องรักษา

ใช้ official per-target `active.smi` / `inactive.smi` เท่านั้น บันทึก release/hash, PubChem AID/SID, assay endpoint และ active semantics แยกตาม target; ไม่เปลี่ยน label ระหว่าง targets ตรวจ canonical collisions และ label conflicts ก่อน; split ตาม target families สำหรับ learned-policy transfer และ scaffold สำหรับ predictor ประกาศแยก within-target replay จาก cross-target generalization Raw files เก็บ `data/raw/` ที่ gitignore และไม่แจกซ้ำก่อนมีสิทธิ์ชัดเจน

## สิทธิ์

Code license ไม่ครอบคลุม dataset หรือ paper ส่วน resource HIV ใช้ตาม CC BY 4.0 ที่หน้า task ของ TDC ระบุ พร้อม credit NCI DTP, MoleculeNet, DeepChem และ TDC; การแปลงข้อมูลระบุไว้ใน `THIRD_PARTY_NOTICES.md` และ resource manifest ไม่ได้รวม PDF บทความที่มีสิทธิ์แตกต่างกัน
