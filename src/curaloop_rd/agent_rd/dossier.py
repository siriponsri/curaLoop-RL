"""Local immutable bilingual dossiers; never export unsupported model claims as facts."""

import hashlib
import html
import json
import os
import tempfile
from pathlib import Path

from .contracts import LIMITS, MissionSpec, canonical, digest
from .evidence import collect, comparisons
from .verifier import verify

TITLES = {"en": "Pharmaceutical evidence dossier", "th": "รายงานหลักฐานเพื่อการวิจัยเภสัชกรรม"}
TH_LIMITS = {
    "development_only": "ข้อมูลพัฒนาที่เปิดเผยแล้ว ยังไม่ใช่ผลยืนยันทางชีววิทยาจากชุดอิสระ",
    "missing_excluded": "ตัดรายการที่ไม่มีผลยืนยันออก ไม่ถือเป็นผล inactive",
    "nonpositive_mixed": "กลุ่ม nonpositive ของแหล่งข้อมูลรวมทั้ง inactive และ inconclusive",
    "seed_range_not_ci": "ช่วงค่าจาก seed ห้าค่าเป็นการทำซ้ำภายใต้เงื่อนไขเดิม ไม่ใช่ช่วงความเชื่อมั่นทางชีววิทยา",
    "one_component": "หก campaigns อยู่ในกลุ่มเชื่อมโยง annotation เดียวกัน",
    "mechanical_d_equals_h": "ค่า D=H ของ round-robin เกิดจากกลไกการเลือกที่งบเหล่านี้",
    "no_lab_or_clinical_value": "ยังไม่ได้วัดการประหยัดแล็บ ประสิทธิผลในการทดลองล่วงหน้า หรือประโยชน์ทางคลินิก",
    "aggregate_only": "มีเฉพาะข้อมูลรวม ไม่มีรายการสารรายตัวหรือผลที่ซ่อนและผลที่ยังไม่ออก",
    "commercial_rights_unconfirmed": "ยังไม่ยืนยันสิทธิ์เชิงพาณิชย์หรือการเผยแพร่ข้อมูลดิบต่อ",
    "no_rl_result": "CF1 ไม่ได้ประเมิน RL ส่วน simulator เป็นงานย้อนหลังอีกการศึกษาหนึ่ง",
}


def render(row, locale):
    def tr(en, th):
        return en if locale == "en" else th
    report = row["released"]
    values = report.get("values", {})
    cells = "".join("<tr><th scope='row'>" + html.escape(k) + "</th><td>" + html.escape(str(v)) + "</td></tr>" for k, v in values.items())
    evidence = row["evidence"]
    sources = "".join("<li><code>" + html.escape(r["path"]) + "</code><br><code>" + r["sha256"] + "</code></li>" for r in evidence.get("source_hashes", []))
    limits = "".join("<li>" + html.escape(v) + "</li>" for v in (LIMITS if locale == "en" else TH_LIMITS).values())
    arms = " · ".join("a" + str(i) + " = " + html.escape(arm) for i, arm in enumerate(row["spec"]["arms"]))
    return f'''<!doctype html><html lang="{locale}"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLES[locale]}</title><style>body{{margin:0;background:#f7f4ef;color:#29282b;font:16px/1.6 system-ui,sans-serif}}main{{max-width:1050px;margin:40px auto;padding:24px}}h1{{font-size:38px;line-height:1.2}}h2{{font-size:22px}}section{{padding:24px;background:white;border:1px solid #ddd6ce;border-radius:12px;margin:20px 0}}code{{overflow-wrap:anywhere;font-size:13px}}table{{border-collapse:collapse;width:100%}}th,td{{padding:10px;border-bottom:1px solid #ddd6ce;text-align:left}}td{{text-align:right;font-variant-numeric:tabular-nums}}.label,a{{color:#a6492d}}.scroll{{overflow:auto}}li{{margin:8px 0}}@media(max-width:600px){{main{{margin:0;padding:16px}}h1{{font-size:30px}}section{{padding:16px}}}}</style>
<main><nav><a href="report-en.html">English</a> · <a href="report-th.html">ไทย</a></nav><p class="label">CURALOOP / AGENT RD / LOCAL DOSSIER</p>
<h1>{TITLES[locale]}</h1><p>{html.escape(row['spec']['goal'])}</p><p><strong>{html.escape(row['state'])}</strong> · {html.escape(row['system'])}</p>
<p>{tr('Recorded retrospective evidence. Author computational checks, not independent expert or user validation.', 'หลักฐานย้อนหลังและการตรวจเชิงคำนวณโดยผู้พัฒนา ไม่ใช่การรับรองจากผู้เชี่ยวชาญอิสระหรือผู้ใช้จริง')}</p>
<section><h2>{tr('Released result', 'ผลที่ระบบปล่อยให้แสดง')}</h2><p>{html.escape(report.get('reason','none'))}</p><p>{arms}</p><div class="scroll"><table><thead><tr><th>{tr('Source value / derived comparison','ค่าจากแหล่งข้อมูล / การเปรียบเทียบ')}</th><th>{tr('Value','ค่า')}</th></tr></thead><tbody>{cells}</tbody></table></div>
<p>{tr('Deltas use right-minus-left over the first two selected arms; sweep uses last-minus-first selected budget. Source operands are rounded to three decimals. HB/DB are fractions.', 'ผลต่างใช้ค่าขวาลบซ้ายของวิธีสองรายการแรก ส่วนการเทียบงบใช้รายการงบสุดท้ายลบรายการแรก ปัดค่าต้นทางเป็นทศนิยมสามตำแหน่ง HB/DB เป็นสัดส่วน')}</p></section>
<section><h2>{tr('Execution and fallback','การทำงานและ fallback')}</h2><p>{tr('Model proposals and tool receipts are preserved in trace.json. Only the released result is shown above.', 'เก็บข้อเสนอโมเดลและหลักฐานการเรียกเครื่องมือไว้ใน trace.json ด้านบนแสดงเฉพาะผลที่ระบบปล่อย')}</p>
<p>{tr('Fallback','Fallback')}: {html.escape(str(row.get('fallback') or 'none'))}</p><pre>{html.escape(json.dumps(row['cost'],indent=2))}</pre></section>
<section><h2>{tr('Scope and limitations','ขอบเขตและข้อจำกัด')}</h2><ul>{limits}</ul><p>{tr('English limitation statements are the canonical scientific scope. Numeric values and source identity are identical in both languages.', 'ข้อจำกัดภาษาอังกฤษคือขอบเขตทางวิทยาศาสตร์อ้างอิง ค่าตัวเลขและแหล่งข้อมูลตรงกันทั้งสองภาษา')}</p></section>
<section><h2>{tr('Provenance','ที่มาของหลักฐาน')}</h2><p><code>{html.escape(str(evidence.get('evidence_id')))}</code></p><ul>{sources}</ul>
<p>{tr('No private compound rows, hidden outcomes, new assay, paid API, clinical claim, external delivery or commercial data clearance.', 'ไม่มีรายการสารส่วนตัว ผลที่ซ่อน การทดลอง assay ใหม่ API เสียเงิน ข้ออ้างทางคลินิก การส่งระบบภายนอก หรือการรับรองสิทธิ์ข้อมูลเชิงพาณิชย์')}</p></section></main></html>'''


def export_dossier(row, root):
    if row["state"] not in ("COMPLETED", "ABSTAINED") or row["released"] is None:
        raise ValueError("No completed result to export")
    if not row["spec"]["export_requested"]:
        raise ValueError("The mission has no explicit local export intent")
    if row["system"] not in ("P", "B0"):
        raise ValueError("Unverified research controls cannot be exported as product reports")
    evidence = collect(MissionSpec.model_validate(row["spec"]))
    if evidence["evidence_id"] != row["evidence"].get("evidence_id"):
        raise ValueError("Source changed; preserve the earlier mission without re-exporting")
    checked = verify(row["released"], evidence, comparisons(evidence))
    if not checked["valid"]:
        raise ValueError("Released claims failed source verification")
    root = Path(root).absolute()
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError("Dossier root must not follow symlinks")
    root.mkdir(parents=True, exist_ok=True)
    key = row["mission_id"] + "-" + digest(row["released"])[:16]
    target = root / key
    if target.is_symlink():
        raise ValueError("Dossier must not follow a symlink")
    document = {"schema": "curaloop.agent-rd.dossier.v1", "mission_id": row["mission_id"], "spec": row["spec"],
                "spec_sha256": row["spec_sha256"], "released": row["released"], "fallback": row["fallback"],
                "source": row["evidence"], "verification": checked, "cost": row["cost"],
                "external_delivery": False, "independent_expert_validation": False, "publication_ready": False}
    files = {"dossier.json": canonical(document), "trace.json": canonical(row),
             "report-en.html": render(row, "en").encode(), "report-th.html": render(row, "th").encode()}
    manifest = {"schema": "curaloop.agent-rd.dossier-manifest.v1", "files": {k: {"bytes": len(v), "sha256": hashlib.sha256(v).hexdigest()} for k, v in files.items()}}
    files["manifest.json"] = canonical(manifest)
    if target.exists():
        if {p.name for p in target.iterdir()} != set(files) or any((target / k).is_symlink() or (target / k).read_bytes() != v for k, v in files.items()):
            raise ValueError("Existing dossier content or inventory changed; no silent overwrite")
    else:
        stage = Path(tempfile.mkdtemp(prefix=".dossier-", dir=root))
        for name, content in files.items():
            with (stage / name).open("xb") as output:
                output.write(content)
                output.flush()
                os.fsync(output.fileno())
        os.rename(stage, target)
    return {"folder": str(target), "files": list(files), "manifest": manifest, "external_delivery": False}
