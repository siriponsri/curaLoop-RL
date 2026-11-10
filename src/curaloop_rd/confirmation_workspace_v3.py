"""Additive local C Workspace confirmation tools, sharing the main API adapter."""

import hashlib
import html
import json
import os
import tempfile
from pathlib import Path

from .confirmation_study import ROOT, comparison_brief

LIMITATIONS_TH = (
    "หลักฐานจากชุดพัฒนาที่เคยอ่านผลแล้ว ยังไม่มีการประเมินยืนยันอิสระหรือวิธีเลือกแบบใหม่",
    "ครอบคลุมเฉพาะ primary hits ที่มีข้อมูลยืนยัน ข้อมูลที่หายไปถูกแยกออก ไม่ถือเป็นผลลบ",
    "ผลที่ไม่เป็นบวกในต้นทางรวมทั้งไม่ออกฤทธิ์และยังสรุปไม่ได้",
    "พิสัยจาก seed ทั้งห้าคือการทำซ้ำภายใต้เงื่อนไขเดิม ไม่ใช่ช่วงความเชื่อมั่นของประชากรชีวภาพ",
    "มีแหล่งข้อมูล 4 กลุ่ม แต่เชื่อมกันเป็นองค์ประกอบเดียว ไม่อ้างการทดสอบข้าม family อิสระหรือ chemical OOD",
    "งบชุดนี้ทำให้ round-robin เลือกเพียงหนึ่งสารต่อกลุ่ม D จึงเท่ากับ H ตามวิธีจัดชุด",
    "ชื่อใน SI กับ repository ต่างกัน 13 จาก 17 คู่ จึงยึดเลข AID และรุ่น repository ที่ตรึงไว้",
    "จำนวนต่อการยืนยันไม่ใช่เงินที่ประหยัด เวลาแล็บ หรือประสิทธิผลทางคลินิก",
    "CF1 ไม่ได้ประเมิน RL ผลนโยบาย HIV และ simulator ปัจจุบันเป็นคนละการศึกษา",
    "ใช้รายงานที่ประมวลผลภายในเท่านั้น ยังไม่ยืนยันสิทธิ์แจกข้อมูลดิบหรือใช้ข้อมูลเชิงพาณิชย์",
)

def render_brief(brief):
    th = brief["locale"] == "th"
    def tr(en, thai):
        return thai if th else en

    selection, evidence = brief["selection"], brief["evidence"]
    rows = []
    for arm in evidence["arms"]:
        metrics = arm["metrics"]
        selected = arm["ranker"] == selection["ranker"] and arm["operator"] == selection["operator"]
        rows.append('<tr' + (' class="selected"' if selected else '') + '><th scope="row">' + html.escape(arm["ranker"]) + '</th><td>' + html.escape(arm["operator"]) + '</td>' + ''.join(
            f'<td>{metrics[m]["mean"]:.2f}<small>{metrics[m]["min"]:.2f} – {metrics[m]["max"]:.2f}</small></td>'
            for m in ("confirmed_positives", "positive_structure_groups", "positive_fingerprint_groups")) + '</tr>')
    source_rows = ''.join(f'<li>{html.escape(row["path"])}<code>{row["sha256"]}</code></li>' for row in evidence["source_hashes"])
    title = html.escape(brief["title"])
    scope = html.escape(evidence["source_labels"][brief["locale"]]["scope"])
    limitations = ''.join(f'<li>{html.escape(t)}</li>' for t in (LIMITATIONS_TH if th else evidence["limitations"]))
    return f'''<!doctype html><html lang="{brief['locale']}"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | CuraLoop C Workspace</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f6f4f0;color:#29282b;font:16px/1.6 system-ui,sans-serif}}main{{max-width:1120px;margin:40px auto;padding:24px}}header{{border-bottom:1px solid #d8d3cd;padding-bottom:24px}}nav{{display:flex;gap:18px}}a{{color:#963e2d}}h1{{font-size:clamp(28px,5vw,44px);line-height:1.15}}.label{{font-size:12px;letter-spacing:.12em;color:#963e2d}}section{{background:#fff;border:1px solid #ddd7cf;border-radius:12px;padding:24px;margin:20px 0}}.scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse;white-space:nowrap;text-align:left}}th,td{{padding:10px;border-bottom:1px solid #e8e3dd}}th{{font-weight:600}}small,code{{display:block;font-size:12px;color:#68625e}}code{{overflow-wrap:anywhere}}.selected{{background:#f6e9e1}}.chips{{display:flex;flex-wrap:wrap;gap:12px}}.chips span{{border:1px solid #ddd7cf;padding:6px 12px;border-radius:6px}}:focus-visible{{outline:3px solid #963e2d;outline-offset:3px}}@media(max-width:600px){{main{{margin:0;padding:16px}}section{{padding:16px}}}}
</style><main><header><nav aria-label="Language"><a href="brief-en.html" lang="en">English</a><a href="brief-th.html" lang="th">ไทย</a></nav>
<p class="label">CURALOOP / C WORKSPACE / CF1</p><h1>{title}</h1><p>{scope}</p><p>{tr('Recorded development evidence. No new experiment, model or external delivery.', 'หลักฐานย้อนหลังจากชุดพัฒนา ไม่มีการทดลองใหม่ ฝึกโมเดล หรือส่งออกสู่ระบบภายนอก')}</p></header>
<section><h2>{tr('Your comparison brief','บันทึกการเปรียบเทียบ')}</h2><div class="chips"><span>{html.escape(selection['campaign'])}</span><span>{selection['budget_percent']}%</span><span>{html.escape(selection['ranker'])}</span><span>{html.escape(selection['operator'])}</span></div><p>{tr('Highlighted row: selected historical arm. All 18 arms remain visible. Mean and observed five-seed range.', 'แถวที่เน้นคือวิธีที่เลือก ยังคงแสดงครบ 18 วิธี ค่าเฉลี่ยและพิสัยจาก seed ทั้งห้า')}</p>
<div class="scroll" role="region" tabindex="0" aria-label="Comparison"><table><thead><tr><th>{tr('Ranker','ตัวจัดอันดับ')}</th><th>{tr('Operator','วิธีจัดชุด')}</th><th>H</th><th>D</th><th>D(FP)</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
<section><h2>{tr('Interpretation and limits','การอ่านผลและข้อจำกัด')}</h2><p>{html.escape(evidence['source_labels'][brief['locale']]['confirmation_zero'])}</p><p>{tr('H: confirmed positives. D: positive structure groups. D(FP): fingerprint-group sensitivity. Group counts are assay-specific; seed ranges are not population confidence intervals.', 'H คือผลบวกที่ยืนยันแล้ว D คือกลุ่มโครงสร้างที่มีผลบวก D(FP) คือการตรวจความไวด้วยกลุ่ม fingerprint จำนวนกลุ่มจำเพาะต่อ assay และพิสัย seed ไม่ใช่ช่วงความเชื่อมั่นของประชากร')}</p><ul>{limitations}</ul><strong>NO_GO_QUOTA_ONLY_METHOD_CLAIM</strong></section>
<section><h2>{tr('Source provenance','ที่มาของหลักฐาน')}</h2><p><a href="{evidence['paper_url']}">MVS-A paper</a> · <a href="{evidence['source_url']}">{tr('Pinned author repository','repository ผู้เขียนรุ่นที่ตรึงไว้')}</a></p><ul>{source_rows}</ul></section>
<p>{tr('Internal local report. No compound list, prospective recommendation, clinical claim or commercial data clearance.', 'รายงานภายในเครื่อง ไม่มีรายการสารเพื่อสั่งทดลอง คำแนะนำล่วงหน้า ข้ออ้างทางคลินิก หรือการรับรองสิทธิ์ข้อมูลเชิงพาณิชย์')}</p></main></html>'''


class ConfirmationWorkspace:
    """Two local tools; the host owns the export root, never a tool argument."""

    def __init__(self, workspace, *, source_root=ROOT):
        self.workspace = Path(workspace).absolute()
        self.source_root = source_root

    def call(self, name, arguments):
        allowed = {"campaign", "budget_percent", "ranker", "operator", "locale"}
        if not isinstance(arguments, dict) or set(arguments) - allowed:
            raise ValueError("Unexpected confirmation tool arguments")
        if name not in ("confirmation_inspect", "confirmation_export"):
            raise ValueError("Unknown confirmation tool")
        brief = comparison_brief(**arguments, root=self.source_root)
        if name == "confirmation_inspect":
            return brief
        for parent in (self.workspace, *self.workspace.parents):
            if parent.is_symlink():
                raise ValueError("Export root must not contain symlinks")
        canonical = json.dumps(brief["selection"], sort_keys=True, separators=(",", ":")).encode()
        key = hashlib.sha256(canonical).hexdigest()[:20]
        target = self.workspace / "confirmation-v3" / key
        if target.is_symlink() or target.parent.is_symlink():
            raise ValueError("Export must not follow a symlink")
        files = {}
        for locale in ("en", "th"):
            localized = comparison_brief(**{**arguments, "locale": locale}, root=self.source_root)
            files[f"brief-{locale}.html"] = render_brief(localized).encode("utf-8")
            files[f"brief-{locale}.json"] = (json.dumps(localized, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
        manifest = {"schema": "curaloop.confirmation.local-export.v3", "selection": brief["selection"],
                    "external_delivery": False, "files": [{"path": k, "bytes": len(v), "sha256": hashlib.sha256(v).hexdigest()} for k, v in files.items()]}
        files["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
        if target.exists():
            if not target.is_dir() or {p.name for p in target.iterdir()} != set(files):
                raise ValueError("Existing confirmation export inventory differs")
            for name, data in files.items():
                p = target / name
                if p.is_symlink() or not p.is_file() or p.read_bytes() != data:
                    raise ValueError("Existing confirmation export was altered")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            staging = Path(tempfile.mkdtemp(prefix=".confirmation-staging-", dir=target.parent))
            for name, data in files.items():
                with (staging / name).open("xb") as f:
                    f.write(data)
                    f.flush()
                    os.fsync(f.fileno())
            # A failed write leaves a retained staging attempt, never a partial
            # final report that a later invocation could mistake for completion.
            os.rename(staging, target)
        return {"schema": "curaloop.confirmation.local-export-result.v3", "local_folder": str(target),
                "entrypoints": {"en": "brief-en.html", "th": "brief-th.html"}, "manifest": manifest, "external_delivery": False}
