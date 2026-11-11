"""Complete English research report assembled exclusively from audited outcomes."""

import hashlib
import json
import re
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "docs/evidence/agent-rd-20261110-v1"
TASK = ROOT / ".local/agent-rd-run-20261110-v1"
OUT = ROOT / "docs/07_publication"
PDF = OUT / "CuraLoop-AgentRD-Computational-Report-EN-v1.pdf"
MD = OUT / "CURALOOP_AGENTRD_COMPUTATIONAL_REPORT_EN_V1.md"
EDITION = "v1"
INK, COPPER, RULE = colors.HexColor("#29282b"), colors.HexColor("#a6492d"), colors.HexColor("#ded8d0")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count(value):
    return f"{value:,}"


def percent(value):
    return "NA" if value is None else f"{100 * value:.1f}%"


def fraction(n, d):
    return f"{n}/{d}" + (f" ({100 * n / d:.1f}%)" if d else " (NA)")


def table_md(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |",
                      *("| " + " | ".join(str(v) for v in row) + " |" for row in rows)])


def set_edition(edition):
    global EDITION, PDF, MD
    assert edition in ("v1", "v2")
    EDITION = edition
    PDF = OUT / ("CuraLoop-AgentRD-Computational-Report-EN-" + edition + ".pdf")
    MD = OUT / ("CURALOOP_AGENTRD_COMPUTATIONAL_REPORT_EN_" + edition.upper() + ".md")


def assemble():
    a_path, d_path = PUBLIC / "analysis-v1/analysis.json", PUBLIC / "descriptive-v1/descriptive.json"
    a, d = read(a_path), read(d_path)
    assert d["source_pins"]["analysis.json"] == sha(a_path)
    mechanism_path = PUBLIC / "mechanism-audit-v1.json"
    if not mechanism_path.exists():
        project_python = ROOT / ".venv/Scripts/python.exe"
        for command in ([str(project_python), "-m", "ruff", "check", "tools/agent_rd_mechanism_audit_v1.py"],
                        [str(project_python), "tools/agent_rd_mechanism_audit_v1.py"]):
            checked = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            if checked.returncode:
                raise RuntimeError("Descriptive mechanism audit failed without changing study results: " + checked.stdout + checked.stderr)
    mechanism = read(mechanism_path)
    assert mechanism["status"] == "DESCRIPTIVE_FIXED_TRACE_VERIFIER_REPLAY_NO_SCORE_CHANGE"
    assert mechanism["source_pins"]["analysis"] == sha(a_path)
    disposition = read(PUBLIC / "locked-progress-v1.json")
    assert disposition["status"] in ("COMPLETE", "INCOMPLETE") and disposition["stop_reason"] != "OPERATIONAL_BATCH_BOUNDARY"
    assert disposition["attempted_units"] == a["attempted"]
    assert read(TASK / "supervisor-v1/receipts/pdf-marker-20261110.json")["exit_code"] == 0
    assert (PUBLIC / ("result-figures-build-" + EDITION + ".json")).is_file()
    s = {r["system"]: r for r in a["systems"]}
    quality = {r["system"]: r for r in d["quality"]}
    p = a["primary"]
    ci = p["exploratory_paired_case_interval_95_pp"]
    complete = a["status"] == "COMPLETE"
    if complete:
        effect = (f"The prespecified P-minus-B2 task-success difference was {p['difference_pp_all_planned']:+.2f} percentage points "
                  f"(exploratory paired-case 95% interval {ci[0]:+.2f} to {ci[1]:+.2f}).")
        if mechanism["all_case_averaged_primary_differences_zero"]:
            effect += (" All case-averaged paired differences were zero; the degenerate interval describes these authored cases "
                       "and does not establish equivalence in an external population.")
    else:
        effect = (f"The fixed matrix was incomplete after {a['attempted']} of {a['planned']} units "
                  f"(stop reason: {d['stop_reason']}); the primary comparison is inconclusive and has no primary interval.")
    abstract = ("We implemented a localhost pharmaceutical evidence workbench and evaluated whether a deterministic source gate with "
                "bounded repair improves task correctness over the same language model and tools without that gate. The frozen design "
                "crossed 32 author-created interface cases and three decoding seeds with deterministic (B0), evidence-supplied LLM-only "
                "(B1), LLM-plus-tools (B2) and guarded (P) controls, plus an eight-case no-repair ablation. Actual Typhoon 12B CPU-model "
                "responses, failures, fallback and costs were retained. "
                f"B0 completed {s['B0']['successes']}/{s['B0']['planned']} planned tasks, B1 {s['B1']['successes']}/{s['B1']['planned']}, "
                f"B2 {s['B2']['successes']}/{s['B2']['planned']} and P {s['P']['successes']}/{s['P']['planned']}. " + effect +
                " Numerical source agreement was evaluated separately from required fields, scope and refusal. These are exposed-data "
                "authored tasks on one corpus/model, not independent biological or expert-validated tasks. The study establishes an "
                "auditable application result within those limits, not prospective discovery, real-user benefit or general agent superiority.")
    core = (OUT / "AGENTRD_METHODS_AND_INTERPRETATION_V1.md").read_text(encoding="utf-8")
    sections = {}
    for part in core.split("\n## ")[1:]:
        heading, body = part.split("\n", 1)
        sections[heading] = body.strip()
    completion_rows = [(k, str(s[k]["planned"]), str(s[k]["attempted"]), fraction(s[k]["successes"], s[k]["planned"]),
                        percent(s[k]["success_rate_attempted"])) for k in s]
    quality_rows = [(k, fraction(s[k]["appropriate_abstentions"], s[k]["abstention_expected_attempted"]),
                     fraction(s[k]["overrefusals"], s[k]["answer_expected_attempted"]), str(s[k]["deterministic_abstention_fallbacks"]),
                     fraction(s[k]["released_numeric_errors"], s[k]["released_numeric_claims"])) for k in s]
    cost_rows = [(k, count(s[k]["model_calls"]) + " / " + count(quality[k]["tool_calls"]), count(s[k]["recorded_model_tokens"]),
                  f"{s[k]['known_model_cpu_seconds'] / 3600:.3f}" if k != "B0" else "NA (no model)",
                  "NA" if s[k]["median_unit_wall_seconds"] is None else f"{s[k]['median_unit_wall_seconds']:.3f}",
                  str(s[k]["failed_model_calls_unknown_cost"])) for k in s]
    detail_rows = [(r["system"], fraction(r["malformed_model_responses"], r["successful_model_response_count"]),
                    fraction(r["required_numeric_keys_correct"], r["required_numeric_key_instances"]),
                    fraction(r["required_scope_codes_present"], r["required_scope_code_instances"]),
                    fraction(r["source_check_valid_but_task_failed"], r["source_check_valid_count"])) for r in d["quality"]]
    ablation_rows = [(r["system"], str(r["attempted"]) + "/" + str(r["planned"]),
                      fraction(r["task_successes"], r["planned"]), str(r["model_calls"]),
                      f"{r['known_model_cpu_seconds'] / 3600:.3f}") for r in d["matched_ablation"]]
    families = list(dict.fromkeys(r["family"] for r in a["families"]))
    family_rows = []
    for family in families:
        selected = {r["system"]: r for r in a["families"] if r["family"] == family}
        family_rows.append((family.replace("_", " "), *(fraction(selected[k]["successes"], selected[k]["planned"])
                                                       for k in ("B0", "B1", "B2", "P"))))
    numeric_rows = [(k, fraction(s[k]["raw_numeric_errors"], s[k]["raw_numeric_claims"]),
                     fraction(s[k]["released_numeric_errors"], s[k]["released_numeric_claims"]),
                     fraction(s[k]["citations_correct"], s[k]["citations_present"]), str(s[k]["execution_failed"])) for k in s]
    seed_text = "; ".join(f"seed {r['seed']}: {r['difference_pp']:+.2f} pp" for r in a["seed_differences"])
    q_p = next(r for r in d["quality"] if r["system"] == "P")
    findings = (f"The guarded arm produced {s['P']['successes']} successful tasks among {s['P']['attempted']} attempted units "
                f"and {s['P']['planned']} planned units. B2 produced {s['B2']['successes']} successes. " + effect +
                f" The three fixed seed differences were {seed_text}. " +
                ("These are conditional descriptive replications, not additional independent cases." if complete else
                 "These descriptive differences retain all planned denominators, including unattempted units; they are not a complete matched effect estimate."))
    failures = (f"P had {q_p['source_check_valid_but_task_failed']} task failures among {q_p['source_check_valid_count']} source-check-valid releases. "
                "This directly distinguishes a source check from the separately scored task contract. Required-key coverage, scope-code coverage "
                "and malformed responses are shown in Table 4. Wrong-action refusals are not reclassified as actual private-data leaks. "
                "The boundary adapters do not provide protected data to any arm.")
    observed_p = next(row for row in mechanism["arms"] if row["system"] == "P")
    observed_b2 = next(row for row in mechanism["arms"] if row["system"] == "B2")
    mechanism_text = (f"A post-hoc replay of the unchanged verifier found {observed_p['verifier_invalid_terminal_proposals']} invalid "
                      f"terminal proposals among {observed_p['terminal_proposals']} P terminal proposals, and "
                      f"{observed_b2['verifier_invalid_terminal_proposals']} among {observed_b2['terminal_proposals']} B2 terminal proposals. "
                      f"B2/P had identical recorded output sequences in {mechanism['B2_P_identical_recorded_output_sequences']}/"
                      f"{mechanism['comparable_B2_P_seed_case_pairs']} comparable seed-case pairs and equal task-success outcomes in "
                      f"{mechanism['B2_P_equal_task_success_pairs']} pairs. Output-sequence comparison excludes call identities and timings. "
                      "This is descriptive execution evidence, not a new score or hypothesis test.")
    if observed_p["verifier_invalid_terminal_proposals"] == 0:
        mechanism_text += (" The repair branch triggered by an invalid numeric/source check was not exercised by these observed P terminal "
                           "proposals. The study therefore cannot establish its efficacy on a population containing such invalid proposals. "
                           "Malformed JSON and missing task requirements remain separate failures. Component integrity tests do not substitute "
                           "for a model-generated challenge to that branch.")
    cost_text = (f"Across all arms, retained successful responses recorded {count(sum(r['recorded_model_tokens'] for r in a['systems']))} tokens "
                 f"and {sum(r['known_model_cpu_seconds'] for r in a['systems']) / 3600:.3f} known model CPU-hours. "
                 f"There were {sum(r['failed_model_calls_unknown_cost'] for r in a['systems'])} failed calls with potentially unknown actual cost. "
                 "Recorded tokens include prompt and generated tokens. These sums are observed research-model work, not the reserved whole-project budget. Local-controller CPU, per-unit wall times "
                 "and full retained resource caps are different quantities. B0 performs real deterministic computation; NA model CPU does not mean zero total compute.")
    model_mission_text = "; ".join(f"{k}: {quality[k]['missions_with_model_attempts']} missions with a model attempt, "
                                   f"{quality[k]['missions_with_successful_provider_responses']} with a successful provider response"
                                   for k in ("B1", "B2", "P", "A-NOREPAIR"))
    cost_text += (" Actual model participation was " + model_mission_text + ". For constructed source faults, model arms receive an "
                  "unavailable-source observation and still call the real model; B0 handles that condition deterministically. "
                  "These are controlled file/source-unavailability tests, not general security or private-data refusal validation. "
                  "The312 planned model-arm missions are distinct from actual attempt and successful-response counts.")
    cap_text = "; ".join(k + ": " + fraction(quality[k]["responses_reaching_output_cap"], quality[k]["responses_with_output_length"])
                         for k in ("B1", "B2", "P", "A-NOREPAIR"))
    cost_text += (" Post-hoc descriptive provider metadata show responses reaching the fixed256-token output cap: " + cap_text +
                  ". Reaching this cap is not itself a malformed response or proof that the cap caused failure. "
                  "The provider-output-length table retains every observed length and stop reason. The short output cap limits generalization; "
                  "it was not increased or retuned after observing locked results.")
    if d.get("operational_recovery"):
        interrupted = d["operational_recovery"]
        cost_text += (f" Unit {interrupted['unit_id']} was interrupted by a local controller-host exit. Its exact previously recorded response "
                      "was reconciled without regeneration. The frozen unit-wall measurement for this unit is the final controller segment, "
                      "excluding earlier work and the offline gap. Model receipt CPU and token cost remain retained; the full resource reservation "
                      "of the interrupted controller was not refunded. Latency summaries therefore describe recorded execution segments, "
                      "not uninterrupted end-to-end user waiting time.")
    control_path = PUBLIC / "interactive-control-accounting-v1.json"
    if control_path.exists():
        control = read(control_path)
        assert control["status"] == "RETAINED_UNMETERED_ADMINISTRATIVE_CONTROL_ALLOWANCE"
        cost_text += (f" Interactive authoring and read-only monitoring CPU were not separately metered; a full {control['retained_cpu_seconds']} "
                      "CPU-second administrative allowance was retained within the original budget. This is an accounting provision, "
                      "not measured consumption or retroactive proof of a hard cap. Model/test jobs have separate enforcement receipts.")
    discussion = ("The practical decision is whether this application's language interface adds enough value to justify its measured errors and cost. "
                  "B0 is the appropriate reference for tasks whose complete calculation and scope rules are already specified. Its pre-freeze ceiling "
                  "was disclosed and is not evidence of broader reasoning. The B2/P comparison tests this particular source gate and bounded correction "
                  "under a short typed interface; it cannot establish a universal advantage for agents or verification loops. "
                  "The no-repair comparison is restricted to its matched eight anchors. Neither successful file recovery nor source fidelity establishes "
                  "scientific interpretation beyond the required codes. The full negative, tied or incomplete findings remain part of the result.")
    product_note = ""
    policy_path = PUBLIC / "product-policy-acceptance.json"
    if policy_path.exists():
        policy = read(policy_path)
        assert policy["status"] == "PASS_CURRENT_PRODUCT_POLICY_NOT_FROZEN_STUDY"
        product_note = ("After the fixed experiment, the product API received a separate deterministic capability preflight. "
                        "Served-application checks exercised English/Thai controller denials, a real five-budget deterministic sweep, "
                        "explicit import of the original real-model example, local dossiers and restart persistence without new inference. "
                        "Controller denials are labeled as zero-model-call decisions. Conservative lexical rules are not a general intent or "
                        "security guarantee. This service version was not the frozen P research condition; none of its tests replace or "
                        "rescore the original failures. The recorded example retains its original date and actual model calls.")
    current_model_path = PUBLIC / "product-current-model-acceptance-v1.json"
    if current_model_path.exists():
        smoke = read(current_model_path)
        if smoke["status"] == "PASS_ACTUAL_CURRENT_PRODUCT_MODEL_LIFECYCLE":
            product_note += (f" A separate post-study current-product mission completed its technical lifecycle with {smoke['actual_cost']['model_calls']} real model calls. ")
            if smoke["task_required_fields_and_scope_pass"]:
                product_note += "Its required-field and scope check passed. "
            else:
                product_note += "It ended in abstention and failed the requested-field/scope task check; this task failure is retained. "
            product_note += "This engineering observation is outside the comparative matrix and provides no efficacy estimate."
        else:
            product_note += (" A separate current-product model smoke check had disposition " + smoke["status"] +
                             ". No successful current-service model claim is inferred from an unrun or failed check.")
    readiness = ("This is a complete computational application report with actual model evidence, rather than a claim of a new molecular-design method. "
                 "JCAMD's official scope includes molecular analysis/design methods and applications, but this one-corpus typed reliability study has "
                 "limited evidence of a distinct molecular-design advance. Submission readiness as a competitive JCAMD research article is not established. "
                 "A technical/software or negative-results route may be more proportionate to the demonstrated contribution. This assessment does not require "
                 "a customer pilot, external researcher or wet lab to complete the solo project and does not assert that any venue will accept the work. "
                 "JCAMD's subscription route lists no APC; its open-access route is outside the owner's US$300 fee ceiling at the checked price. "
                 "No manuscript was submitted, no fee was paid and no editor or researcher was contacted. Author declarations and venue/rights decisions remain with the owner.")
    text = ("# Source checking, task completion and cost in a local pharmaceutical evidence agent\n\n"
            "Author manuscript / computational application report / not submitted\n\n"
            "Siripon Srihangpiboon\n\nKing Mongkut's Institute of Technology Ladkrabang\n\n"
            "Correspondence: srihangpiboon.siri@gmail.com | ORCID: 0009-0001-0611-5568\n\n"
            "## Abstract\n\n" + abstract + "\n\n## Introduction\n\n" + sections["Introduction"] +
            "\n\n## Methods\n\n" + sections["Methods"] +
            "\n\n![Figure 1. Fixed implementation and matched controls. A source check is distinct from task scoring.](../evidence/agent-rd-20261110-v1/figures-v2/01-control-flow.png)\n\n"
            "## Results\n\n### Fixed-matrix disposition and primary result\n\n" + findings +
            "\n\nTable 1. Task completion, with every planned denominator. A-NOREPAIR has eight fixed cases, not the full32-case roster.\n\n" +
            table_md(["System", "Planned", "Attempted", "Success / planned", "Success / attempted"], completion_rows) +
            "\n\n![Figure 2. All-planned completion. Whiskers are min/max over three decoding seeds, not confidence intervals.](../evidence/agent-rd-20261110-v1/result-figures-v1/02-task-completion.png)\n\n"
            "### Refusal, fallback and released claims\n\n" + failures + "\n\n" + mechanism_text +
            "\n\nTable 2. Appropriate abstention, overrefusal, deterministic abstention fallback and released numerical error. Empty claim denominators are NA.\n\n" +
            table_md(["System", "Appropriate abstention", "Overrefusal", "Fallback n", "Released errors / claims"], quality_rows) +
            "\n\n### Computational cost\n\n" + cost_text +
            "\n\nTable 3. Actual observed cost. Model/tool call counts are separate counts, not a rate. Tool calls include the trusted preflight read, which is not an autonomous model action. Model CPU is a known lower bound if a failed call has unknown cost; wall time includes orchestration and SSH wait. API charges are US$0 throughout.\n\n" +
            table_md(["System", "Model / tool calls", "Tokens", "Model CPU h", "Median unit wall s", "Failed calls, cost unknown"], cost_rows) +
            "\n\n![Figure 3. Task completion and observed median unit latency. B0's actual timing remains visible; CPU is a separate measure.](../evidence/agent-rd-20261110-v1/result-figures-v1/03-cost-completion.png)\n\n"
            "### Task completeness and matched no-repair anchors\n\n"
            "Table 4. Descriptive completeness. Rates use attempted answer-task key/code instances and successful provider responses. Malformed means unparsable JSON or an invalid values-map type under the frozen scorer, not every possible action-schema failure. A source-valid task failure is not a numeric error by definition.\n\n" +
            table_md(["System", "Malformed / responses", "Correct required keys", "Required scope codes", "Task failures / valid checks"], detail_rows) +
            "\n\nTable 5. P and A-NOREPAIR on exactly the same eight fixed anchors and three seeds. Descriptive only, with no full-matrix extrapolation.\n\n" +
            table_md(["System", "Attempted / planned", "Success / planned", "Calls", "Known model CPU h"], ablation_rows) +
            "\n\n### Family results and raw-versus-released fidelity\n\n"
            "Table 6. Task success by prespecified family, with all planned family units retained. These are authored task types, not independent biological families.\n\n" +
            table_md(["Task family", "B0", "B1", "B2", "P"], family_rows) +
            "\n\nTable 7. Raw proposal errors, released numerical errors, citation correctness and failed execution units. Numerical rates use parseable claim instances; malformed responses are separately retained in Table 4. Correct citations alone do not establish task completion.\n\n" +
            table_md(["System", "Raw errors / claims", "Released errors / claims", "Correct / present citations", "Failed units"], numeric_rows) +
            "\n\n### Localhost engineering acceptance\n\n"
            "The actual UI-to-API-to-model acceptance mission used two real calls, 2,054 recorded tokens and 904.552 model CPU seconds. "
            "It passed its separately authored comparison task and explicit five-file dossier reread. An actual API restart recovered the same completed "
            "row without regeneration. EN/TH, mobile and legacy-isolation self-checks passed. The refined screenshot pass reused the same response with "
            "no new inference.46 backend/oracle/source tests and30 frontend tests/type/lint/build passed. These are engineering acceptance records, "
            "not additional locked observations or independent validation.\n\n"
            "## Discussion\n\n" + discussion +
            ("\n\n### Delivered product version\n\n" + product_note if product_note else "") +
            "\n\n## Limitations\n\n" + sections["Interpretive limits"] +
            "\n\n## Reproducibility and availability\n\n" + sections["Reproducibility and availability"] +
            "\n\nThe associated audited JSON/CSV files retain each planned unit, per-family outcomes, seed differences, raw/released numeric counts, "
            "failure reasons, exact traces and source hashes. Figure sources use those records directly. The original study source freeze precedes all locked calls. "
            "Recomputation instructions distinguish offline analysis from newly authorized inference.\n\n"
            "## Publication assessment and author decisions\n\n" + readiness +
            "\n\nOfficial journal pages checked on 10 November 2026: https://link.springer.com/journal/10822/aims-and-scope and "
            "https://link.springer.com/journal/10822/how-to-publish-with-us . Subscription price compatibility is not scientific acceptance.\n\n"
            "## Declarations\n\n"
            "Funding, competing interests and final author approval are not confirmed in this draft. Supplied author details do not constitute signed declarations. "
            "No human-participant, prospective clinical or wet-lab study is reported.\n\n" + sections["Writing-assistance disclosure for the final author to review"] +
            "\n\n## References\n\n" + sections["References"] + "\n")
    for old, new in (("full32", "full 32"), ("The312", "The 312"), ("fixed256", "fixed 256"),
                     ("inference.46", "inference. 46"), ("and30", "and 30")):
        text = text.replace(old, new)
    if EDITION == "v2":
        text = text.replace("/result-figures-v1/", "/result-figures-v2/")
        text = text.replace("CPU is a separate measure.]", "CPU is a separate measure. Leader lines identify displaced labels; P uses an open diamond in the cluster.]")
    return text, a, d


def inline(text):
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"https?://[^\s<>]+", lambda match: '<link href="' + match.group(0) + '" color="#a6492d">' + match.group(0) + '</link>', text)
    return text


def pdf_from_markdown(content):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("PaperTitle", fontName="Helvetica-Bold", fontSize=21, leading=25, textColor=INK, spaceAfter=16))
    styles.add(ParagraphStyle("PaperBody", fontName="Helvetica", fontSize=10, leading=14.5, textColor=INK, spaceAfter=8, alignment=TA_LEFT))
    styles.add(ParagraphStyle("PaperCaption", parent=styles["PaperBody"], fontSize=9, leading=12, spaceAfter=9))
    styles.add(ParagraphStyle("PaperCell", fontName="Helvetica", fontSize=8.5, leading=11, textColor=INK))
    styles["Heading1"].textColor = COPPER
    styles["Heading1"].fontSize, styles["Heading1"].leading = 14, 18
    styles["Heading1"].keepWithNext = True
    styles["Heading2"].textColor = INK
    styles["Heading2"].fontSize, styles["Heading2"].leading = 11, 15
    styles["Heading2"].keepWithNext = True
    story, lines, i = [], content.splitlines(), 0
    width = A4[0] - 88
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("!["):
            caption, filename = re.fullmatch(r"!\[(.+)\]\((.+)\)", line).groups()
            path = (OUT / filename).resolve()
            assert path.is_relative_to(PUBLIC) and path.is_file()
            picture = Image(str(path), width=width, height=width * (122 / 178 if "control-flow" in filename else 108 / 178))
            story.append(KeepTogether([Spacer(1, 8), picture, Paragraph(inline(caption), styles["PaperCaption"])]))
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [v.strip() for v in lines[i].strip("|").split("|")]
                if not all(v == "---" for v in cells):
                    rows.append([Paragraph(inline(v), styles["PaperCell"]) for v in cells])
                i += 1
            columns = len(rows[0])
            weights = [1.6] + [1.7] * (columns - 1)
            table = Table(rows, colWidths=[width * w / sum(weights) for w in weights], repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), .7, INK), ("LINEBELOW", (0, 0), (-1, 0), .4, RULE),
                                      ("LINEBELOW", (0, -1), (-1, -1), .6, RULE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                      ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                                      ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
            story.extend([table, Spacer(1, 10)])
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), styles["PaperTitle"]))
            i += 1
            continue
        if line.startswith("## ") or line.startswith("### "):
            level = "Heading2" if line.startswith("### ") else "Heading1"
            story.append(Paragraph(inline(line.lstrip("# ")), styles[level]))
            i += 1
            continue
        paragraph = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "|", "![")):
            if paragraph and re.match(r"^\d+\.\s", lines[i]):
                break
            paragraph.append(lines[i])
            i += 1
        paragraph_text = " ".join(paragraph)
        paragraph_style = styles["PaperBody"]
        if paragraph_text.startswith("Table "):
            paragraph_style = ParagraphStyle("TableCaption", parent=paragraph_style, keepWithNext=True)
        story.append(Paragraph(inline(paragraph_text), paragraph_style))

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(RULE)
        canvas.line(44, 35, A4[0] - 44, 35)
        canvas.setFont("Helvetica", 8.5)
        canvas.setFillColor(INK)
        canvas.drawString(44, 22, "CuraLoop AgentRD | Author computational report " + EDITION + " | Not submitted")
        canvas.drawRightString(A4[0] - 44, 22, str(document.page))
        canvas.restoreState()

    SimpleDocTemplate(str(PDF), pagesize=A4, rightMargin=44, leftMargin=44, topMargin=44, bottomMargin=48,
                      title="Source checking, task completion and cost in a local pharmaceutical evidence agent",
                      author="Siripon Srihangpiboon").build(story, onFirstPage=footer, onLaterPages=footer)


def build():
    assert not PDF.exists() and not MD.exists(), "Preserve earlier editions; no silent report replacement"
    text, a, d = assemble()
    MD.write_text(text, encoding="utf-8", newline="\n")
    pdf_from_markdown(text)
    reader = PdfReader(PDF)
    extracted = "\n".join(p.extract_text() for p in reader.pages)
    assert len(reader.pages) >= 8 and "\ufffd" not in extracted
    assert all(value in extracted for value in ("Abstract", "Results", "Declarations", "References", "not established", "final16"))
    receipt = {"status": "COMPLETE_REPORT_CREATED_AWAITING_ALL_PAGE_VISUAL_REVIEW",
               "matrix_status": a["status"], "planned": a["planned"], "attempted": a["attempted"], "pages": len(reader.pages),
               "pdf": PDF.relative_to(ROOT).as_posix(), "pdf_sha256": sha(PDF), "markdown": MD.relative_to(ROOT).as_posix(),
               "markdown_sha256": sha(MD), "analysis_sha256": sha(PUBLIC / "analysis-v1/analysis.json"),
               "descriptive_sha256": sha(PUBLIC / "descriptive-v1/descriptive.json"), "stop_reason": d["stop_reason"],
               "manuscript_submitted": False, "independent_expert_validation": False}
    with (PUBLIC / ("manuscript-build-" + EDITION + ".json")).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(receipt, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps(receipt))


def render():
    target = TASK / ("manuscript-render-" + EDITION)
    target.mkdir(exist_ok=False)
    poppler = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe"
    result = subprocess.run([str(poppler), "-r", "110", "-png", str(PDF), str(target / "page")], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert len(list(target.glob("page-*.png"))) == len(PdfReader(PDF).pages)
    print(json.dumps({"status": "ALL_MANUSCRIPT_PAGES_RENDERED_REVIEW_PENDING", "folder": str(target)}))
