"""Unit tests for structural static pack audit; not a runnable-app test suite."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from scripts.validate_handoff_pack import verify, REQUIRED

class PackStructureTest(unittest.TestCase):
    def create_minimal(self, root):
        for name in REQUIRED:
            p = root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            if name == 'papers/papers_manifest.json':
                p.write_text(json.dumps({'papers': [
                    {'id': f'P{i:02}', 'article_url': f'https://example.test/{i}'}
                    for i in range(1, 21)]}), encoding='utf8')
            elif name.endswith('.json'):
                p.write_text('{}', encoding='utf8')
            else:
                p.write_text('# Test\n', encoding='utf8')

    def test_minimal_pack_passes_without_zip(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); self.create_minimal(root)
            self.assertTrue(verify(root)['pass'])

    def test_detect_missing_file(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); self.create_minimal(root)
            (root / REQUIRED[0]).unlink()
            self.assertFalse(verify(root)['pass'])

    def test_detect_wrong_paper_count(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); self.create_minimal(root)
            f=root/'papers/papers_manifest.json'; f.write_text('{"papers": []}')
            self.assertFalse(verify(root)['pass'])

    def test_detect_duplicate_paper_id(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); self.create_minimal(root)
            f=root/'papers/papers_manifest.json'; d=json.loads(f.read_text())
            d['papers'][1]['id']=d['papers'][0]['id']; f.write_text(json.dumps(d))
            self.assertFalse(verify(root)['pass'])

    def test_detect_accidental_article_pdf(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); self.create_minimal(root)
            (root/'papers/not_a_rights_cleared_article.pdf').write_bytes(b'%PDF')
            self.assertFalse(verify(root)['pass'])

    def test_detect_broken_relative_link(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); self.create_minimal(root)
            (root/'README.md').write_text('[missing](docs/nope.md)')
            self.assertFalse(verify(root)['pass'])

    def test_verify_archive_integrity(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/'src'; root.mkdir(); self.create_minimal(root)
            zpath=Path(t)/'bundle.zip'
            with ZipFile(zpath,'w') as z:
                for p in root.rglob('*'):
                    if p.is_file(): z.write(p, 'bundle/'+p.relative_to(root).as_posix())
            self.assertTrue(verify(root,zpath)['pass'])

if __name__ == '__main__':
    unittest.main()
