"""Final guide layout adds the actual saved trace to the formerly sparse page."""
import json
import shutil
import subprocess
from pypdf import PdfReader
from reportlab.platypus import Image, Paragraph, PageBreak, Spacer
from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, sha, write
from dc2_local_documents_v1 import markdown, paragraph, image, build_pdf


def main():
    screens = PUBLIC / "model-product-screens-v1"
    flow = markdown((ROOT / "docs/08_agent_rd/LOCAL_WORKFLOW_GUIDE_EN_20261113.md").read_text(encoding="utf-8"))
    flow += [paragraph("Follow the saved execution trail", "HeadingLocal"), image(screens / "trace-en.png",height=420),Spacer(1,10),paragraph("This is the actual saved plan, tool execution, verification and export trace. Two provider attempts produced genuine responses. Reopening it starts no inference. Technical messages retain their original English text.","NoteLocal")]
    flow += [PageBreak(), paragraph("A saved actual model request", "TitleLocal"), paragraph("The model translated MW <=100 while other defaults stayed unchanged. This capture was made after the lease stopped; the disabled button correctly shows the model is offline.","NoteLocal"), image(screens / "request-en.png",width=245,height=640)]
    flow += [PageBreak(), paragraph("Inspect and collect actual results", "TitleLocal"), paragraph("Seven input rows yield five valid structures, two rejected rows and two within-limit compounds. The molecule drawing and table come from the completed RDKit process."),image(screens / "compounds-en.png",height=350),Spacer(1,18), image(screens / "status-en.png",height=100),Spacer(1,10),paragraph("Choose a compound ID to inspect its 2D structure. Review report.html, selected.csv, rejected.csv, evidence.json and manifest.json, then download bundle.zip. Reopening a saved result does not repeat inference.","NoteLocal")]
    output = ROOT / "docs/manual/CuraLoop-Local-Molecular-Workflow-Guide-EN-v3.pdf"
    build_pdf(output,flow)
    renders = TASK / "pdf-qa-v3"
    renders.mkdir(exist_ok=False)
    subprocess.run(["rtk","proxy",shutil.which("pdftoppm"),"-scale-to","1500","-png",str(output),str(renders/"manual")],check=True,timeout=120)
    receipt = {"status":"PASS_CREATED_AND_RENDERED_PENDING_AUTHOR_VISUAL_REVIEW","path":output.relative_to(ROOT).as_posix(),"sha256":sha(output),"pages":len(PdfReader(output).pages),"renders":str(renders),"scope":"Layout-only guide revision; model cases and research results unchanged"}
    write(PUBLIC / "manual-build-v3.json",receipt)
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
