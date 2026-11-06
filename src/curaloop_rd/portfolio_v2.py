"""Add a bilingual view to the frozen v1 export; keep its original files intact."""
import hashlib
import json
import tempfile
from pathlib import Path
from .portfolio_v1 import Portfolio as Base
from .workspace_v2 import render_workspace

class Portfolio(Base):
    def __init__(self, source_root, registry_path, workspace, font):
        self.font=Path(font)
        if not self.font.is_file() or not (self.font.parent/'OFL.txt').is_file():
            raise ValueError('Local licensed CuraThai font required')
        super().__init__(source_root, registry_path, workspace)

    def call(self, name, arguments):
        result=super().call(name, arguments)
        if name!='local_export':return result
        source=Path(result['local_folder']);target=source/'view-v2'
        if target.is_symlink() or (target.exists() and not target.is_dir()):
            raise ValueError('Bilingual view must be an owned directory')
        if not target.exists():render_workspace(source,target,self.font)
        manifest=json.loads((target/'handoff-manifest.json').read_text())
        # Re-derive authority from validated frozen export bytes and this renderer.
        # The editable view manifest cannot authenticate its own copied report.
        with tempfile.TemporaryDirectory(prefix='.view-verify-',dir=source) as temporary:
            expected=render_workspace(source,Path(temporary)/'expected',self.font)
            if manifest!=expected or manifest['report_sha256']!=arguments['report_sha256']:
                raise ValueError('Bilingual view differs from the validated original export')
            if {p.name for p in target.iterdir()}!={'handoff-manifest.json'}|{r['path'] for r in expected['files']}:
                raise ValueError('Bilingual view inventory changed')
            for row in expected['files']:
                p=target/row['path']
                if p.parent!=target or not p.is_file() or p.is_symlink() or p.stat().st_size!=row['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:
                    raise ValueError('Bilingual view artifact changed')
        return dict(result, workspace_v2={'local_folder':str(target),'manifest':manifest,'external_delivery':False})
