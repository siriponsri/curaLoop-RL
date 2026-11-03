import { useEffect, useState } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Database,
  GitBranch,
  ShieldCheck,
} from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../state";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { GoLink, KpiStrip, SourceBadge, Workflow } from "../components/shared";
import { RecordedBenchmarkChart } from "../components/charts";
import { short } from "../lib";
import type { Candidate } from "../types";

export default function Overview() {
  const { run, evidence, meta, t } = useApp();
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  useEffect(() => {
    if (!run) return;
    let alive = true;
    api
      .candidates(run.session_id, { page_size: 1 })
      .then((r) => {
        if (alive) setCandidate(r.items[0] ?? null);
      })
      .catch(() => {});
    return () => {
      alive = false;
    };
  }, [run?.session_id]);
  if (!run) return null;
  const scenario = run.report.manifest.scenario_config;
  const historical =
    run.report.manifest.data_origin === "HISTORICAL_PUBLIC_DATA";
  return (
    <>
      <div className="mission-hero">
        <div className="mission-copy">
          <div className="hero-badges">
            <SourceBadge />
            <Badge>Personal research portfolio</Badge>
          </div>
          <h1>
            {t("Every assay is a decision.", "ทุกการทดสอบ เริ่มจากการตัดสินใจ")}
            <br />
            <span>{t("Make yours reproducible.", "ที่ตรวจสอบซ้ำได้")}</span>
          </h1>
          <p>
            {t(
              `A library of ${scenario.candidate_count.toLocaleString()} candidates. A budget of ${scenario.budget_units} simulated cost units. Which compounds should we test first—and what changes when results arrive?`,
              `จากสาร ${scenario.candidate_count.toLocaleString()} ตัว ภายใต้งบจำลอง ${scenario.budget_units} หน่วย เราควรเลือกทดสอบตัวใดก่อน และปรับการเลือกอย่างไรเมื่อได้รับผลใหม่?`,
            )}
          </p>
          <div className="hero-actions">
            <Button asChild>
              <Link to="/lab">
                {t("Enter simulation lab", "เปิดห้องจำลอง")}
                <ArrowRight size={17} />
              </Link>
            </Button>
            <Button asChild variant="ghost">
              <Link to="/scenario">
                {t("Design a scenario", "ตั้งเงื่อนไขการทดลอง")}
                <ArrowUpRight size={16} />
              </Link>
            </Button>
          </div>
          <div className="hero-footnote">
            <ShieldCheck size={15} />
            {historical
              ? t(
                  "Historical labels. Simulated operations. No claims of drug efficacy.",
                  "ผล assay จริงย้อนหลัง · เงื่อนไขปฏิบัติงานจำลอง · ไม่ใช่หลักฐานประสิทธิผลของยา",
                )
              : t(
                  "Synthetic labels and operations. No biological efficacy meaning.",
                  "ทั้งผลและเงื่อนไขเป็นข้อมูลสังเคราะห์ ไม่มีความหมายเชิงประสิทธิผลทางชีวภาพ",
                )}
          </div>
        </div>
        <div className="hero-specimen">
          <div className="specimen-header">
            <span>
              {t(
                "From the public candidate pool",
                "ตัวอย่างจากกลุ่มสารสาธารณะ",
              )}
            </span>
            <span className="small-mono">
              {candidate?.compound_id ?? "Loading…"}
            </span>
          </div>
          {candidate?.canonical_smiles && meta?.molecule_rendering ? (
            <img
              className="specimen-image"
              src={`/api/v1/runs/${run.session_id}/molecules/${candidate.compound_id}.svg`}
              alt={`RDKit 2D structure of ${candidate.compound_id}`}
            />
          ) : (
            <div className="descriptor-art">
              <Database size={42} />
              <strong>{candidate?.feature_count ?? "—"}</strong>
              <span>public numerical features</span>
            </div>
          )}
          <div className="specimen-footer">
            <div>
              <span>{t("Representation", "รูปแบบข้อมูล")}</span>
              <strong>
                {candidate?.canonical_smiles
                  ? "Morgan fingerprint"
                  : "Synthetic descriptors"}
              </strong>
            </div>
            <Badge className="badge-neutral">
              {candidate?.feature_count ?? "—"} features
            </Badge>
          </div>
          <p className="specimen-note">
            {t(
              historical
                ? "Structure is public. Its assay outcome stays hidden until requested and delivered."
                : "Synthetic numerical descriptors only; no real molecular structure or biological assay.",
              historical
                ? "โครงสร้างเป็นข้อมูลสาธารณะ ส่วนผล assay ถูกซ่อนไว้จนกว่าจะร้องขอและส่งคืนผล"
                : "มีเพียง descriptors สังเคราะห์ ไม่มีโครงสร้างโมเลกุลหรือผล assay ทางชีวภาพจริง",
            )}
          </p>
        </div>
      </div>
      <KpiStrip run={run} />
      <section className="workflow-section">
        <div className="section-heading">
          <div>
            <h2>
              {t(
                "A closed loop, with an open audit trail",
                "วงจรการเลือกสาร พร้อมบันทึกทุกขั้นตอน",
              )}
            </h2>
            <p>
              {t(
                "Live campaign state, not an illustration of laboratory integration.",
                "สถานะจาก campaign จริงในระบบ ไม่ใช่ภาพแทนการเชื่อมต่อห้องปฏิบัติการ",
              )}
            </p>
          </div>
          <GoLink to="/lab">
            {t("Follow the campaign", "ติดตาม campaign")}
          </GoLink>
        </div>
        <Workflow run={run} />
      </section>
      <div className="overview-bottom">
        <section className="surface">
          <div className="section-heading">
            <div>
              <h2>
                {t(
                  "Evidence before ambition",
                  "เริ่มจากหลักฐาน ก่อนขยายข้อกล่าวอ้าง",
                )}
              </h2>
              <p>
                {t(
                  "Recorded HIV benchmark · 10 paired seeds · B = 30",
                  "ผล HIV benchmark ที่บันทึกไว้ · 10 paired seeds · B = 30",
                )}
              </p>
            </div>
            <Badge className="badge-neutral">v0.1 evidence</Badge>
          </div>
          {evidence && (
            <RecordedBenchmarkChart rows={evidence.statistics.summary} />
          )}
          <div className="honesty-note">
            <GitBranch size={17} />
            <p>
              {t(
                "The learned controllers matched Greedy because all 300/300 historical requests used their Greedy fallback. This is not successful learned transfer.",
                "controller ที่ฝึกแล้วได้ผลเท่า Greedy เพราะทั้ง 300/300 คำขอใช้ Greedy fallback จึงยังไม่ใช่หลักฐานว่าเกิด learned transfer",
              )}
            </p>
          </div>
          <GoLink to="/evidence">
            {t("Read methods and limitations", "อ่านวิธีประเมินและข้อจำกัด")}
          </GoLink>
        </section>
        <section className="research-note">
          <BookOpen size={23} />
          <h2>
            {t(
              "A research instrument.\nAn honest portfolio.",
              "เครื่องมือเรียนรู้การวิจัย\nพร้อมข้อจำกัดที่ชัดเจน",
            )}
          </h2>
          <p>
            {t(
              historical
                ? "Explore policy trade-offs with real historical assay data. Inspect every decision, budget reservation and delivered result."
                : "Explore policy trade-offs with synthetic fixtures. Inspect every decision, budget reservation and delivered result.",
              historical
                ? "ศึกษาทางเลือกของนโยบายบนข้อมูล assay จริงย้อนหลัง พร้อมตรวจเหตุผล งบที่จอง และผลที่ส่งคืนได้ทุกขั้น"
                : "ศึกษาทางเลือกของนโยบายด้วยข้อมูลสังเคราะห์ พร้อมตรวจเหตุผล งบที่จอง และผลที่ส่งคืนได้ทุกขั้น",
            )}
          </p>
          <dl>
            <div>
              <dt>Assay</dt>
              <dd>
                {run.report.manifest.data_origin === "HISTORICAL_PUBLIC_DATA"
                  ? "NCI DTP · HIV"
                  : "Synthetic binary"}
              </dd>
            </div>
            <div>
              <dt>Data rights</dt>
              <dd>{run.report.manifest.dataset.terms_status}</dd>
            </div>
            <div>
              <dt>Code revision</dt>
              <dd className="small-mono">
                {short(meta?.repo_git_sha ?? "—", 12)}
              </dd>
            </div>
          </dl>
          <GoLink to="/presentation">
            {t("Open the guided presentation", "เปิดโหมดนำเสนอ")}
          </GoLink>
        </section>
      </div>
    </>
  );
}
