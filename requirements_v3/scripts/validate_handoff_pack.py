#!/usr/bin/env python3
"""Stdlib-only structural verification of CuraLoop-RL specification bundle.

Examples:
  python scripts/validate_handoff_pack.py .
  python scripts/validate_handoff_pack.py . --zip /path/to/CuraLoopRL_v3.zip

Does not validate domain science, third-party licenses, internet access, the
future application, or any Digital Twin/RL claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

REQUIRED = [
    'START_HERE.md', 'README.md', 'GOAL.md', 'PLAN.md',
    'audit/AUDIT_REPORT.md', 'audit/RELEASE_VALIDATION.md',
    'prompts/01_GPT_WORK_MASTER_PROMPT.md',
    'prompts/02_CODEX_MASTER_PROMPT.md',
    'docs/DATASET_AND_LEAKAGE_PLAYBOOK.md',
    'docs/ACCEPTANCE_TEST_MATRIX.md',
    'docs/TWIN_VALIDATION.md', 'docs/UX_BLUEPRINT_TH.md',
    'papers/papers_manifest.json',
    'papers/PRIORITIZED_READING_WITH_VERIFICATION.md',
    'contracts/policy_observation.schema.json',
    'contracts/experiment_event.schema.json',
    'contracts/run_manifest.schema.json',
]


def verify(root: Path, zip_path: Path | None = None) -> dict:
    errors: list[str] = []
    files = sorted(p for p in root.rglob('*') if p.is_file())
    rels = [p.relative_to(root).as_posix() for p in files]
    for relative in REQUIRED:
        if relative not in rels:
            errors.append(f'missing required file: {relative}')
    if any(p.is_symlink() for p in root.rglob('*')):
        errors.append('symlink found in source tree')
    for p in files:
        if p.suffix == '.json':
            try:
                json.loads(p.read_text(encoding='utf-8'))
            except Exception as exc:
                errors.append(f'invalid json {p.relative_to(root)}: {exc}')
    paper_path = root / 'papers/papers_manifest.json'
    paper_count = None
    if paper_path.exists():
        try:
            d = json.loads(paper_path.read_text(encoding='utf-8'))
            ids = [paper['id'] for paper in d['papers']]
            paper_count = len(ids)
            if len(set(ids)) != paper_count:
                errors.append('paper IDs are not unique')
            if paper_count < 20:
                errors.append('fewer than 20 catalog entries')
            for paper in d['papers']:
                if not paper.get('article_url', '').startswith('https://'):
                    errors.append(f'non-https or missing article_url for {paper["id"]}')
        except Exception as exc:
            errors.append(f'paper catalog validation failed: {exc}')
    pdfs = [r for r in rels if r.lower().endswith('.pdf')]
    if pdfs:
        errors.append('original PDFs present unexpectedly; rights not audited for distribution: ' + str(pdfs[:3]))
    for p in files:
        if p.suffix == '.md':
            text = p.read_text(encoding='utf-8')
            # Only inspect markdown parenthesized local links, not code/fenced references.
            for href in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', text):
                href = href.split('#')[0].strip()
                if not href or '://' in href or href.startswith(('mailto:', '#')):
                    continue
                if '%20' in href or '?' in href or href.startswith('/'):
                    continue
                target = (p.parent / href).resolve()
                if root.resolve() not in [target, *target.parents] or not target.exists():
                    errors.append(f'broken relative Markdown link in {p.relative_to(root)}: {href}')
    archive_count = None
    if zip_path:
        with ZipFile(zip_path, 'r') as z:
            if z.testzip() is not None:
                errors.append('zip CRC failed')
            names = [n for n in z.namelist() if not n.endswith('/')]
            archive_count = len(names)
            if len(set(names)) != len(names):
                errors.append('duplicate ZIP member names')
            if len({PurePosixPath(n).parts[0] for n in names}) != 1:
                errors.append('ZIP contains multiple or missing root folders')
            for n in names:
                pure = PurePosixPath(n)
                if pure.is_absolute() or '..' in pure.parts or '\\' in n:
                    errors.append(f'unsafe ZIP entry: {n}')
            mapped = {str(PurePosixPath(n).relative_to(PurePosixPath(n).parts[0])): n for n in names}
            if sorted(mapped) != sorted(rels):
                errors.append('ZIP file list differs from source tree')
            for relative, archived in mapped.items():
                if relative in rels and hashlib.sha256(z.read(archived)).digest() != hashlib.sha256((root / relative).read_bytes()).digest():
                    errors.append('archive bytes mismatch: ' + relative)
    return {'source_file_count': len(files), 'archive_file_count': archive_count,
            'markdown_file_count': sum(p.endswith('.md') for p in rels),
            'original_article_pdf_count': len(pdfs), 'paper_reference_count': paper_count,
            'errors': errors, 'pass': not errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('root', nargs='?', type=Path, default=Path('.'))
    parser.add_argument('--zip', type=Path, default=None)
    args = parser.parse_args()
    result = verify(args.root.resolve(), args.zip)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
