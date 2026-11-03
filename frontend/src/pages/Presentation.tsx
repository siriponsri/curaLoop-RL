import { useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  Clock3,
  Play,
  Presentation,
} from "lucide-react";
import { useApp } from "../state";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import {
  KpiStrip,
  PageHeading,
  SourceBadge,
  Workflow,
} from "../components/shared";

export default function GuidedPresentation() {
  const { run, t, act, busy } = useApp();
  const [step, setStep] = useState(0);
  if (!run) return null;
  const slides = [
    {
      title: t("The decision", "โจทย์การตัดสินใจ"),
      time: "0:00–1:00",
      text: t(
        "A screening library has more candidates than the available budget. We choose what to assay first—not what to prescribe.",
        "สารที่ต้องการศึกษามีมากกว่างบที่ทดสอบได้ เรากำลังเลือกสารเพื่อ assay ไม่ได้เลือกยาสำหรับรักษา",
      ),
    },
    {
      title: t("What is real?", "อะไรคือข้อมูลจริง?"),
      time: "1:00–2:00",
      text: t(
        run.report.manifest.data_origin === "HISTORICAL_PUBLIC_DATA"
          ? "HIV assay outcomes and molecular structures are historical public data. Costs, timing and capacity are simulated assumptions."
          : "This campaign uses synthetic descriptors and fictional labels. It contains no real molecular structures or biological assay outcomes. Costs, timing and capacity are simulated assumptions.",
        run.report.manifest.data_origin === "HISTORICAL_PUBLIC_DATA"
          ? "ผล HIV assay และโครงสร้างโมเลกุลเป็นข้อมูลสาธารณะย้อนหลัง ส่วนต้นทุน เวลา และความจุเป็นสมมติฐานจำลอง"
          : "แคมเปญนี้ใช้ descriptors และผลสังเคราะห์ ไม่มีโครงสร้างโมเลกุลหรือผล assay จริง ต้นทุน เวลา และความจุเป็นสมมติฐานจำลอง",
      ),
    },
    {
      title: t("Select, then wait", "เลือกสาร แล้วรอผล"),
      time: "2:00–3:30",
      text: t(
        "Select a batch below. Watch budget become reserved. Advance simulated time until results are due. Pending compounds are not confirmed hits.",
        "กดเลือก batch ดูงบที่ถูกจอง แล้วเลื่อนเวลาจำลองจนผลครบกำหนด สารที่รอผลยังไม่ใช่ confirmed hit",
      ),
    },
    {
      title: t("Adapt with evidence", "ปรับการเลือกด้วยผลที่รู้แล้ว"),
      time: "3:30–5:00",
      text: t(
        "Only delivered labels update the policy. Every request and outcome is recorded in an immutable public ledger.",
        "นโยบายใช้เฉพาะ labels ที่เปิดเผยแล้ว ทุกคำขอและผลถูกบันทึกใน public ledger",
      ),
    },
    {
      title: t("Compare honestly", "เปรียบเทียบตามหลักฐาน"),
      time: "5:00–7:00",
      text: t(
        "Use matched conditions and export the result. Trained controllers used Greedy fallback on the historical benchmark. This remains a retrospective simulator.",
        "ใช้เงื่อนไขเดียวกันและส่งออกผล controller ที่ฝึกแล้วใช้ Greedy fallback ใน historical benchmark ระบบนี้ยังเป็น retrospective simulator",
      ),
    },
  ];
  return (
    <>
      <PageHeading
        title={t("Guided presentation", "นำเสนอแบบมีผู้ช่วย")}
        description={t(
          "A 5–7 minute walkthrough using the live campaign—no scripted success data.",
          "นำเสนอ 5–7 นาทีด้วย campaign ที่รันจริง ไม่มีข้อมูลความสำเร็จที่เขียนล่วงหน้า",
        )}
      />
      <div className="presentation-origin">
        <SourceBadge /> <span>{run.report.manifest.dataset.name}</span>
      </div>
      <div className="presentation-layout">
        <aside className="presentation-steps">
          {slides.map((s, i) => (
            <button
              key={i}
              className={step === i ? "active" : ""}
              onClick={() => setStep(i)}
            >
              <span>{i + 1}</span>
              <div>
                <strong>{s.title}</strong>
                <small>{s.time}</small>
              </div>
            </button>
          ))}
        </aside>
        <div className="surface presentation-stage">
          <Badge className="badge-teal">
            <Presentation size={14} />
            {slides[step].time}
          </Badge>
          <h2>{slides[step].title}</h2>
          <p className="presentation-copy">{slides[step].text}</p>
          <Workflow run={run} compact />
          <div className="presentation-actions">
            <Button
              aria-label="Presentation select batch"
              onClick={() => void act("select")}
              disabled={Boolean(busy) || !run.can_select}
            >
              <Play size={15} />
              {t("Select batch", "เลือก batch")}
            </Button>
            <Button
              aria-label="Presentation advance time"
              variant="outline"
              onClick={() => void act("advance")}
              disabled={Boolean(busy) || !run.pending.length}
            >
              <Clock3 size={15} />
              {t("Advance +1", "เลื่อนเวลา +1")}
            </Button>
            <Button asChild variant="ghost">
              <Link to={step === 4 ? "/benchmarks" : "/lab"}>
                {step === 4
                  ? t("Open benchmark arena", "เปิดหน้าเปรียบเทียบ")
                  : t("Inspect full lab", "ดูห้องจำลองเต็มหน้า")}
                <ArrowRight size={15} />
              </Link>
            </Button>
          </div>
          <div className="presentation-footer">
            <Button
              variant="ghost"
              onClick={() => setStep((s) => s - 1)}
              disabled={!step}
            >
              <ArrowLeft size={15} />
              {t("Back", "ย้อนกลับ")}
            </Button>
            <span>
              {step + 1} / {slides.length}
            </span>
            <Button
              variant="outline"
              onClick={() => setStep((s) => s + 1)}
              disabled={step === slides.length - 1}
            >
              {t("Next chapter", "บทถัดไป")}
              <ArrowRight size={15} />
            </Button>
          </div>
        </div>
      </div>
      <KpiStrip run={run} />
    </>
  );
}
