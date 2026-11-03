# เปิด CuraLoop-RL Web บน Windows

## วิธีง่ายที่สุด

1. แตก ZIP ทั้งหมดไปยังโฟลเดอร์ที่เขียนไฟล์ได้เอง เช่น `C:\Projects\CuraLoopRL` (เป็นตัวอย่าง ไม่ใช่ตำแหน่งที่ระบบเขียนลงเครื่องคุณแล้ว)
2. เปิดโฟลเดอร์ source ที่มี `Start-CuraLoop-Web.cmd`
3. ตรวจว่ามี Python 3.11 หรือ 3.12 แบบ 64 bit บนเครื่อง แล้วดับเบิลคลิก **Start-CuraLoop-Web.cmd**
4. ครั้งแรก script จะสร้าง `.venv` และติดตั้ง dependencies จากอินเทอร์เน็ต ไม่ต้องสิทธิ์ administrator และไม่แก้ execution policy
5. หลัง setup สำเร็จ browser จะเปิด **http://127.0.0.1:8000** หน้าเดียวที่ให้บริการทั้ง React และ API
6. ใช้งานครั้งต่อไป offline ได้ ข้อมูล HIV, fingerprints, checkpoints, โลโก้, ฟอนต์ และ frontend build อยู่ในแพ็กเกจแล้ว
7. ปิดด้วย Ctrl+C ในหน้าต่างที่รัน แล้วจึงปิดหน้าต่างนั้น

**Node.js ไม่จำเป็นสำหรับการเปิด release ที่มี frontend build แล้ว** หากต้องแก้ frontend หรือ build ใหม่ ให้ติดตั้ง Node.js 22.12+ จากแหล่งทางการสำหรับบัญชีผู้ใช้เอง ไม่มีการติดตั้ง global executables อัตโนมัติ

## เปิดด้วย PowerShell โดยไม่ activate environment

```powershell
cd C:\Projects\CuraLoopRL  # เปลี่ยนเป็นโฟลเดอร์ source จริงของคุณ
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-web-lock.txt
.\.venv\Scripts\python.exe -m pip install -e ".[web]" --no-deps
.\.venv\Scripts\python.exe scripts\start_web.py
```

ถ้ามี Python 3.12 ให้ใช้ `py -3.12` หาก setup เครือข่ายขัดข้อง ให้รัน **Setup-CuraLoop-Web.cmd** อีกครั้ง หลังสำเร็จจึงเปิด Start ไม่มีคำสั่งหยุดแอปอื่นหรือเปลี่ยนระบบองค์กร

## สาธิต 5–7 นาที

Overview → Scenario builder (HIV, seed 42, budget 30, capacity 5, delay 2) → Simulation lab: Select batch → Advance +1 สองครั้ง → ดูผลและบัญชีงบ → Benchmark arena: เลือก policies แล้ว Compare → ดาวน์โหลด JSON/CSV → Research evidence ดู fallback และข้อจำกัด

ผล default seed อาจไม่พบ active hit นี่เป็นผลจริง ไม่ควรเปลี่ยน seed เพื่ออ้างความสำเร็จ ถ้าใช้ Guided presentation ปุ่มในหน้านั้นทำงานกับ campaign จริงชุดเดียวกัน

## บันทึกและกลับมาทำต่อ

Sessions อยู่ใน memory ของ local API เมื่อปิด server จะหาย ให้ Export JSON ของ run เดียวก่อนปิด แล้วเลือกไฟล์ใน Research evidence → Validate & resume เมื่อเปิดใหม่ การ resume ตรวจ dataset hash และ public event ledger ใหม่ก่อนรับผล ไม่ใช้ pickle

## Streamlit สำรอง

```powershell
.\.venv\Scripts\python.exe -m streamlit run app\streamlit_app.py
```

เปิด http://127.0.0.1:8501 เป็น fallback เดิม เก็บ scientific engine เดียวกัน

## สำหรับพัฒนาและตรวจสอบ

```powershell
.\.venv\Scripts\python.exe -m pytest -q
# API dev: เปิด terminal หนึ่ง
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
# frontend dev: อีก terminal หนึ่ง
cd frontend
npm ci
npm run dev
```

Frontend dev อยู่ที่ http://127.0.0.1:5173 ใช้ proxy ไป API ในเครื่อง เมื่อแก้เสร็จ `npm run build` แล้วกลับไปเปิด production mode หน้าเดียว

## ข้อจำกัดของหลักฐาน

คำสั่งและ launcher Windows นี้เขียนเพื่อการใช้งานจริง แต่ environment ที่ทดสอบในรอบนี้เป็น Linux/Python 3.12 ไม่อ้างว่าได้รันบนเครื่อง Windows ของเจ้าของ ไม่มีการ push, deploy, เข้าระบบบริษัท หรือใช้บริการเสียเงิน
