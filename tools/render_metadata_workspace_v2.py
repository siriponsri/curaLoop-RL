"""Prepare a new public metadata view without modifying the v1 evidence export."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from curaloop_rd.workspace_v2 import render_workspace

if __name__=='__main__':
    manifest=render_workspace(ROOT/'docs/05_product/metadata-portfolio-demo',
                              ROOT/'docs/05_product/metadata-workspace-v2',
                              ROOT/'frontend/public/fonts/NotoSansThai.ttf')
    print(json.dumps({'status':'PREPARED_NOT_BROWSER_VERIFIED','report_sha256':manifest['report_sha256'],
                      'files':len(manifest['files'])+1}))
