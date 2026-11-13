"""Record the completed author visual inspection and supplementary structural QA."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from pypdf import PdfReader
from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, sha, write


def main():
    documents = [("docs/manual/CuraLoop-Local-Molecular-Workflow-Guide-EN-v3.pdf",5,TASK/"pdf-qa-v3","manual"),("docs/07_publication/CuraLoop-Local-Workflow-Feasibility-EN-v2.pdf",6,TASK/"pdf-qa-v2/CuraLoop-Local-Workflow-Feasibility-EN-v2","page")]
    records = []
    for relative, pages, folder, prefix in documents:
        path = ROOT / relative
        assert len(PdfReader(path).pages) == pages
        assert all((folder/f"{prefix}-{i}.png").is_file() for i in range(1,pages+1))
        records.append({"path":relative,"sha256":sha(path),"pages_inspected":list(range(1,pages+1)),"text_extraction_nonempty":all(p.extract_text().strip() for p in PdfReader(path).pages)})
    package = Path.home()/".codex/plugins/cache/openai-curated-remote/scientific-visual-table-style/2.2.0/skills/scientific-visual-table-style"
    structural = []
    for extension in ("svg","png"):
        figure=PUBLIC/("figures-v2/native-readiness."+extension)
        call=subprocess.run(["rtk","proxy",sys.executable,str(package/"scripts/visual_qa.py"),str(figure),"--target-width-mm","178","--target-height-mm","100","--json"],capture_output=True,text=True)
        write(TASK/("figure-structural-qa-"+extension+"-v1.json"),{"returncode":call.returncode,"stdout":call.stdout,"stderr":call.stderr})
        assert call.returncode==0,call.stdout+call.stderr
        structural.append({"extension":extension,"returncode":call.returncode,"sha256":sha(figure),"report":json.loads(call.stdout)})
    write(PUBLIC/"document-visual-review-v1.json",{"status":"PASS_AUTHOR_ALL_PAGES_AND_FIGURE_REVIEW","utc":datetime.now(timezone.utc).isoformat(),"reviewer_scope":"Implementer's visual self-review; not independent expert validation","documents":records,"figure":{"source":"native-admission-final-v1.json","observed":[1,6,3],"required":[1,6,4],"order":["development tasks","evaluation candidates","evaluation lineages"],"native_mm":[178,100],"formats":["svg","pdf","png"],"full_color_and_grayscale_inspected":True,"legend_and_annotation_collision_resolved":True,"ordinary_text_pt":8,"no_fabricated_uncertainty":True,"structural_checks":structural},"passes":["Scientific value/unit/denominator/NOT_RUN audit","Final rendered-page geometry and legibility"],"corrections":["Preserve list/reference item breaks","Separate chart subtitle and legend","Separate annotation labels from data marks","Add real trace screenshot to sparse guide page"],"limits":"Screenshot labels retain actual UI resolution; no real-user readability study or independent review"})
    print("PASS_AUTHOR_ALL_11_FINAL_PDF_PAGES_AND_COLOR_GRAYSCALE_FIGURE_REVIEW")


if __name__ == "__main__":
    main()
