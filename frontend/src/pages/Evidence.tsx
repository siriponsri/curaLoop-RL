import { useState } from "react";
import {
  ArrowUpRight,
  CheckCircle2,
  Download,
  FileJson,
  GitBranch,
  ShieldCheck,
  Upload,
} from "lucide-react";
import { api } from "../api";
import { useApp } from "../state";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { ExportButtons, PageHeading, SourceBadge } from "../components/shared";
import { ReturnChart } from "../components/charts";
import { number, short } from "../lib";

export default function Evidence() {
  const { run, meta, evidence, setRun, t } = useApp();
  const [resumeFile, setResumeFile] = useState<File | null>(null),
    [resumeStatus, setResumeStatus] = useState(""),
    [resuming, setResuming] = useState(false);
  if (!run || !meta || !evidence) return null;
  const m = run.report.manifest;
  async function resume() {
    if (!resumeFile) return;
    setResuming(true);
    try {
      if (resumeFile.size > 10_000_000)
        throw new Error(
          t("JSON file exceeds 10 MB.", "ไฟล์ JSON ต้องมีขนาดไม่เกิน 10 MB"),
        );
      const restored = await api.resume(JSON.parse(await resumeFile.text()));
      setRun(restored);
      setResumeStatus("success");
    } catch (e) {
      setResumeStatus("error:" + (e as Error).message);
    } finally {
      setResuming(false);
    }
  }
  return (
    <>
      <PageHeading
        title={t("Research evidence", "หลักฐานและข้อจำกัด")}
        description={t(
          "Trace the data, methods and limits behind every number.",
          "ตรวจที่มาของข้อมูล วิธีประเมิน และขอบเขตของทุกตัวเลข",
        )}
      >
        <ExportButtons id={run.session_id} />
      </PageHeading>
      <div className="evidence-intro">
        <ShieldCheck size={26} />
        <div>
          <h2>
            {t(
              "A personal research workbench, with explicit boundaries.",
              "เครื่องมือวิจัยส่วนบุคคล พร้อมขอบเขตที่ชัดเจน",
            )}
          </h2>
          <p>
            {t(
              "Not an official GPO system. No lab integration, validated Digital Twin, clinical efficacy or GMP claim.",
              "ไม่ใช่ระบบทางการของ GPO ไม่มีการเชื่อมแล็บ และไม่อ้าง Digital Twin ที่ยืนยันแล้ว ประสิทธิผลทางคลินิก หรือการรับรอง GMP",
            )}
          </p>
        </div>
      </div>
      <div className="evidence-grid">
        <section className="surface">
          <div className="section-heading">
            <h2>{t("Dataset provenance", "ที่มาของข้อมูล")}</h2>
            <SourceBadge />
          </div>
          <dl className="details-list">
            <div>
              <dt>Assay / target</dt>
              <dd>{m.dataset.assay_id}</dd>
            </div>
            <div>
              <dt>Label semantics</dt>
              <dd>{m.dataset.label_semantics}</dd>
            </div>
            <div>
              <dt>Dataset release</dt>
              <dd>{m.dataset.release}</dd>
            </div>
            <div>
              <dt>Dataset SHA256</dt>
              <dd className="small-mono break-text">{m.dataset.sha256}</dd>
            </div>
            <div>
              <dt>Source</dt>
              <dd className="break-text">{m.dataset.source}</dd>
            </div>
            <div>
              <dt>Rights status</dt>
              <dd>{m.dataset.terms_status}</dd>
            </div>
            <div>
              <dt>Seed-label selection</dt>
              <dd>
                {m.initial_label_selection}
                <br />
                {m.initial_labels_budget_rule}
              </dd>
            </div>
          </dl>
          <p className="small muted">
            {t(
              "References for the separately recorded historical HIV benchmark",
              "เอกสารอ้างอิงของ benchmark HIV ย้อนหลังที่บันทึกแยกไว้",
            )}
          </p>
          <div className="evidence-links">
            {evidence.source_links.map((link) => (
              <a
                href={link.url}
                key={link.url}
                target="_blank"
                rel="noreferrer"
              >
                {link.title}
                <ArrowUpRight size={15} />
              </a>
            ))}
          </div>
        </section>
        <section className="surface">
          <div className="section-heading">
            <h2>{t("Reproduction identity", "ข้อมูลสำหรับตรวจสอบซ้ำ")}</h2>
            <GitBranch size={20} />
          </div>
          <dl className="details-list">
            <div>
              <dt>Web / engine version</dt>
              <dd>
                v{meta.web_version} / v{meta.engine_version}
              </dd>
            </div>
            <div>
              <dt>{t("Current code revision", "เวอร์ชันโค้ดปัจจุบัน")}</dt>
              <dd className="small-mono break-text">
                {meta.repo_git_sha}
                <br />
                <Badge className="badge-amber">
                  {meta.working_tree_dirty === false
                    ? t("Clean working tree", "ไฟล์ตรงกับ commit")
                    : meta.working_tree_dirty === true
                      ? t(
                          "Uncommitted changes present",
                          "มีการแก้ไขที่ยังไม่ commit",
                        )
                      : t("Git state unavailable", "ไม่พบสถานะ Git")}
                </Badge>
              </dd>
            </div>
            <div>
              <dt>Engine source SHA256</dt>
              <dd className="small-mono break-text">{meta.source_sha256}</dd>
            </div>
            <div>
              <dt>Frontend build SHA256</dt>
              <dd className="small-mono break-text">
                {meta.frontend_build_sha256 ??
                  t("Not available", "ไม่พบ build")}
              </dd>
            </div>
            <div>
              <dt>Algorithm</dt>
              <dd>{m.algorithm_version}</dd>
            </div>
            <div>
              <dt>Scenario source</dt>
              <dd>
                <Badge className="badge-amber">{m.scenario_origin}</Badge>
              </dd>
            </div>
            <div>
              <dt>Digital Twin maturity</dt>
              <dd>RETROSPECTIVE_SIMULATOR</dd>
            </div>
          </dl>
          <div className="verification-note">
            <CheckCircle2 size={18} />
            <p>
              {t(
                "79 passing tests belong to the original v0.1 evidence. This rebuild has separately executed API, frontend and browser evidence in docs/evidence/web-v2.",
                "ผล 79 tests เป็นหลักฐานของ v0.1 การตรวจรอบ rebuild แยกผล API, frontend และ browser ไว้ที่ docs/evidence/web-v2",
              )}
            </p>
          </div>
        </section>
      </div>
      <section className="surface">
        <div className="section-heading">
          <div>
            <h2>
              {t(
                "Held-out predictor audit",
                "ผล predictor บนข้อมูลที่กันไว้ทดสอบ",
              )}
            </h2>
            <p>{evidence.predictor.scope}</p>
          </div>
          <Badge>Recorded · v0.1</Badge>
        </div>
        <div className="predictor-metrics">
          <div>
            <span>AUROC</span>
            <strong>{number(evidence.predictor.auroc, 3)}</strong>
          </div>
          <div>
            <span>Average precision</span>
            <strong>{number(evidence.predictor.average_precision, 4)}</strong>
          </div>
          <div>
            <span>Test prevalence</span>
            <strong>
              {number(evidence.predictor.test_prevalence * 100, 1)}%
            </strong>
          </div>
          <div>
            <span>Scaffold overlap</span>
            <strong>{evidence.predictor.scaffold_overlap}</strong>
          </div>
        </div>
        <p className="honesty-note-text">
          {t(
            "960 train / 240 test molecules, with only 6 test actives. These weak predictions and the custom split do not establish drug-discovery utility or a published leaderboard result.",
            "train 960 / test 240 โมเลกุล โดย test มี active เพียง 6 ตัว ผลการทำนายยังต่ำ และ split นี้ไม่ใช่ official leaderboard จึงยังไม่ยืนยันประโยชน์ต่อ drug discovery",
          )}
        </p>
      </section>
      <section className="surface">
        <div className="section-heading">
          <div>
            <h2>
              {t(
                "Trained controllers, visible limitations",
                "โมเดลที่ฝึกจริง พร้อมข้อจำกัดที่ตรวจพบ",
              )}
            </h2>
            <p>
              {t(
                "Training returns are actual checkpoint records—not evaluation performance.",
                "กราฟ training return มาจาก checkpoint จริง ไม่ใช่คะแนนประเมินผลภายนอก",
              )}
            </p>
          </div>
          <Badge className="badge-amber">Synthetic training only</Badge>
        </div>
        <div className="controller-grid">
          {evidence.controllers.map((cp) => (
            <div key={cp.policy_id}>
              <h3>
                {cp.policy_id === "q_learning"
                  ? "Tabular Q-learning"
                  : "Contextual bandit"}
              </h3>
              <span className="muted small">
                {cp.training_episodes} episodes ·{" "}
                {short(cp.checkpoint_sha256, 16)}
              </span>
              <ReturnChart returns={cp.episode_returns} />
            </div>
          ))}
        </div>
        <div className="honesty-note amber-note">
          <ShieldCheck size={18} />
          <p>
            {evidence.controller_historical_fallback}.{" "}
            {t(
              "All recorded historical selections therefore came from Greedy fallback, not learned controller transfer.",
              "ทุกการเลือกใน benchmark ย้อนหลังจึงมาจาก Greedy fallback ไม่ใช่ผลของ learned transfer",
            )}
          </p>
        </div>
      </section>
      <div className="evidence-grid">
        <section className="surface">
          <h2>{t("Scientific limitations", "ข้อจำกัดทางวิทยาศาสตร์")}</h2>
          <ul className="limitations-list">
            {m.limitations.map((item, i) => (
              <li key={item}>
                {t(
                  item,
                  [
                    "โครงการส่วนบุคคลที่เป็นอิสระ ไม่ใช่โครงการทางการหรือระบบที่ GPO รับรอง",
                    "ที่มาและความหมายของผลขึ้นกับแต่ละชุดข้อมูล ผล assay ย้อนหลังไม่ใช่หลักฐานประสิทธิผลของยา",
                    "ต้นทุน ความจุ เวลารอ และผลสูญหายเป็นสมมติฐานจำลอง ไม่ใช่ค่าเงินจริงหรือยอดประหยัดจริง",
                    "ข้อมูลตั้งต้นเป็นต้นทุนจมร่วมกันและไม่นับเป็น hits ใหม่ มีเพียงข้อมูลสังเคราะห์ที่จัด seed ตามสัดส่วนคลาส",
                    "ค่าความน่าจะเป็นจาก Logistic ยังไม่ผ่าน calibration ระยะจาก 0.5 เป็นเพียงเกณฑ์เชิง heuristic ไม่ใช่ uncertainty ที่ตรวจสอบแล้ว",
                    "การเปรียบเทียบ seed เดียวใช้แสดงพฤติกรรม ความแปรผันหลาย seeds ใน assay เดียวไม่ใช่การยืนยันข้ามเป้าหมาย",
                    "ตัวควบคุมฝึกด้วยงานสังเคราะห์เท่านั้น ยังไม่ยืนยันการถ่ายโอนสู่เภสัชกรรม การเชื่อมแล็บ Digital Twin หรือการใช้ทาง GMP/คลินิก",
                    "การแยก process ของนโยบายไม่ใช่ OS sandbox สำหรับโค้ดที่เป็นอันตราย หรือการย้อนสร้างค่าจริงของข้อมูลสังเคราะห์",
                  ][i] ??
                    "เก็บคำอธิบาย RUN_STARTED แบบเดิมเพื่อ replay ตรงต้นฉบับ โปรดดูที่มาและ hash ของข้อมูลประกอบ",
                )}
              </li>
            ))}
          </ul>
        </section>
        <section className="surface resume-section">
          <FileJson size={28} />
          <h2>
            {t(
              "Your evidence travels with you",
              "เก็บหลักฐานและกลับมาทำต่อได้",
            )}
          </h2>
          <p>
            {t(
              "Export the current public snapshot before restarting. A single-run JSON can restore its pending queue and validated event history.",
              "ส่งออก public snapshot ก่อนปิดระบบ ไฟล์ JSON ของ run เดียวสามารถคืนสถานะคิวรอผลและประวัติที่ตรวจสอบแล้วได้",
            )}
          </p>
          <ExportButtons id={run.session_id} />
          <hr />
          <label className="file-field">
            <Upload size={18} />
            <span>
              {resumeFile?.name ??
                t(
                  "Choose a run JSON · max 10 MB",
                  "เลือก JSON ของ run · สูงสุด 10 MB",
                )}
            </span>
            <input
              aria-label="Resume JSON file"
              type="file"
              accept=".json,application/json"
              onChange={(e) => setResumeFile(e.target.files?.[0] ?? null)}
            />
          </label>
          <Button
            disabled={!resumeFile || resuming}
            variant="outline"
            onClick={() => void resume()}
          >
            {resuming
              ? t("Validating…", "กำลังตรวจสอบ…")
              : t("Validate & resume", "ตรวจและกลับมาทำต่อ")}
          </Button>
          {resumeStatus && (
            <p role="status" className="field-note">
              {resumeStatus === "success"
                ? t(
                    "Snapshot reconciled. Your campaign is ready in Simulation lab.",
                    "ตรวจประวัติสำเร็จ เปิดห้องจำลองเพื่อทำแคมเปญต่อได้",
                  )
                : t("Could not resume: ", "กลับมาทำต่อไม่สำเร็จ: ") +
                  resumeStatus.replace(/^error:/, "")}
            </p>
          )}
          <p className="muted small">
            <Download size={13} />
            {t(
              meta.session_note,
              "เซสชันเก็บในหน่วยความจำ ส่งออก JSON เพื่อกลับมาทำต่อหลังรีสตาร์ตเซิร์ฟเวอร์",
            )}
          </p>
        </section>
      </div>
    </>
  );
}
