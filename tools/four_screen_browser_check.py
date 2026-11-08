"""Verify the four-screen product against a separately started local QA engine.

Uses an isolated browser context. The server must use a disposable storage path.
No protected research data, existing user campaigns, or remote compute are used.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    checks: dict[str, object] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
        page = context.new_page()
        errors: list[str] = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        expect.set_options(timeout=30000)
        base = 'http://127.0.0.1:5173'

        # Start a fresh QA campaign; rerunning this check never consumes another
        # campaign's remaining capacity or alters its pending queue.
        created = context.request.post(base + '/api/v1/runs', data={
            'scenario': {'dataset': 'hiv_moleculenet_replay_v1', 'seed': 42,
                         'candidate_count': 1200, 'initial_count': 48,
                         'budget_units': 30, 'batch_size': 5, 'delay_steps': 2,
                         'assay_cost_units': 1, 'delay_jitter': 0, 'missing_percent': 0},
            'policy': 'greedy'})
        assert created.ok, created.text()
        session_id = created.json()['session_id']
        context.add_init_script('localStorage.setItem("curaloop-session", ' + json.dumps(session_id) + ')')

        def current() -> dict:
            session = page.evaluate('localStorage.getItem("curaloop-session")')
            assert session, 'UI did not retain its current session'
            response = context.request.get(f'{base}/api/v1/runs/{session}')
            assert response.ok
            return response.json()

        def capture(name: str) -> None:
            expect(page.locator('.page-heading h1')).to_be_visible()
            page.wait_for_load_state('networkidle')
            expect(page.locator('.initial-loading, .loading-panel')).to_have_count(0)
            page.evaluate('document.fonts.ready')
            page.locator('img').evaluate_all('(images) => images.forEach(image => image.loading = "eager")')
            page.wait_for_function('Array.from(document.images).every(image => image.complete)', timeout=30000)
            page.screenshot(path=str(out / f'{name}.png'), full_page=True, animations='disabled')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Page overflow: {name}'

        page.goto(base)
        expect(page.get_by_role('heading', name='Discovery overview', exact=True)).to_be_visible()
        expect(page.get_by_role('button', name='Next compound')).to_be_enabled()
        capture('01-discovery-overview-en')
        initial = current()
        checks['initial_metrics'] = initial['report']['metrics']
        page.get_by_role('link', name='Simulation lab', exact=True).click()
        expect(page.get_by_role('heading', name='Digital Twin Simulation Lab', exact=True)).to_be_visible()
        expect(page.get_by_text('Not a Validated Digital Twin', exact=True)).to_be_visible()
        before = current()
        page.get_by_role('button', name='Model update', exact=False).click()
        expect(page.get_by_text('Last selection model status', exact=True)).to_be_visible()
        assert current()['revision'] == before['revision'], 'Inspecting a stage mutated the engine'
        page.get_by_role('button', name='Select next batch', exact=True).click()
        expect(page.get_by_role('button', name='Advance +1 step', exact=True)).to_be_enabled()
        pending = current()
        assert pending['pending'] and pending['report']['metrics']['confirmed_hits'] == before['report']['metrics']['confirmed_hits']
        response = context.request.get(f"{base}/api/v1/runs/{pending['session_id']}/candidates?status=pending&page_size=12")
        assert response.ok
        assert all(c['revealed_active'] is None for c in response.json()['items'])
        checks['pending_labels_hidden'] = True
        capture('02-simulation-lab-pending-en')
        page.get_by_role('link', name='Compound explorer', exact=True).click()
        expect(page.get_by_role('region', name='Compound library table')).to_be_visible()
        page.get_by_label('Compound status', exact=True).select_option('pending')
        row_button = page.locator('.compound-record-link').first
        expect(row_button).to_be_visible()
        row_button.click()
        expect(page.get_by_role('dialog').get_by_text('Unrevealed', exact=True).first).to_be_visible()
        expect(page.get_by_role('dialog').get_by_role('heading', name='Selection history')).to_be_visible()
        capture('04-compound-record-pending-en')
        page.keyboard.press('Escape')
        page.get_by_label('Compound status', exact=True).select_option('all')
        expect(page.locator('.compound-record-link').first).to_be_visible()
        capture('04-compound-explorer-en')
        page.get_by_role('link', name='Simulation lab', exact=True).click()
        for _ in range(2):
            with page.expect_response(lambda response: response.url.endswith('/advance') and response.request.method == 'POST') as response:
                page.get_by_role('button', name='Advance +1 step', exact=True).click()
            assert response.value.ok
            expect(page.get_by_role('button', name='Verify replay', exact=True)).to_be_enabled()
        delivered = current()
        assert delivered['report']['metrics']['delivered_assays'] > 0
        checks['delivered_metrics'] = delivered['report']['metrics']
        capture('02-simulation-lab-delivered-en')
        page.get_by_role('link', name='Benchmark arena', exact=True).click()
        expect(page.get_by_role('heading', name='Recorded HIV research benchmark')).to_be_visible()
        expect(page.get_by_text('Error bars show seed standard deviation, not a confidence interval across biological targets.', exact=True)).to_be_visible()
        capture('03-benchmark-arena-en')
        # A small existing-engine comparison validates presentation plumbing, not research efficacy.
        page.get_by_role('button', name='Compare selected policies', exact=True).click()
        expect(page.get_by_role('heading', name='Comparison complete')).to_be_visible(timeout=120000)
        expect(page.get_by_text('Single seed: variance unavailable', exact=True)).to_be_visible()
        expect(page.get_by_role('columnheader', name='Hits / cost unit', exact=True)).to_be_visible()
        capture('03-benchmark-comparison-en')
        checks['matched_comparison_completed'] = True
        # Language changes retain the same campaign and canonical API values.
        for route, name, heading in [('/', '01-discovery-overview', 'ภาพรวมการค้นพบ'), ('/lab', '02-simulation-lab', 'ห้องจำลอง Digital Twin'), ('/benchmarks', '03-benchmark-arena', 'สนามเปรียบเทียบนโยบาย'), ('/compounds', '04-compound-explorer', None)]:
            page.goto(base + route)
            expect(page.locator('h1')).to_be_visible()
            page.get_by_role('button', name='ไทย', exact=True).click()
            expect(page.locator('html')).to_have_attribute('lang', 'th')
            if heading and route != '/benchmarks':
                expect(page.get_by_role('heading', name=heading, exact=True)).to_be_visible()
            assert current()['session_id'] == delivered['session_id']
            capture(name + '-th')
        checks['language_preserves_campaign'] = True
        for language in ['EN', 'ไทย']:
            page.set_viewport_size({'width': 390, 'height': 844})
            for route, name in [('/', '01-overview'), ('/lab', '02-lab'), ('/benchmarks', '03-arena'), ('/compounds', '04-explorer')]:
                page.goto(base + route)
                expect(page.locator('h1')).to_be_visible()
                page.get_by_role('button', name=language, exact=True).click()
                capture(name + ('-mobile-en' if language == 'EN' else '-mobile-th'))
        checks['page_errors'] = errors
        checks['status'] = 'PASS' if not errors else 'FAIL'
        (out / 'browser-check.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
        assert not errors, errors
        browser.close()
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
