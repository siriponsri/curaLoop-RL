"""Render the skill-authored diagrams using a real offline Chromium browser."""

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 900}, device_scale_factor=2)
        page.route("http://**/*", lambda route: route.abort())
        page.route("https://**/*", lambda route: route.abort())
        for name in ("architecture", "screening-loop"):
            path = ROOT / "docs/diagrams" / f"{name}.html"
            page.goto(path.as_uri())
            page.evaluate("document.fonts.ready")
            page.locator("svg").screenshot(path=str(path.with_suffix(".png")), omit_background=True)
            geometry = page.locator("svg").evaluate("""svg => ({
                viewBox: svg.getAttribute('viewBox'),
                labels: [...svg.querySelectorAll('text')].map(t=>({
                  text:t.textContent, x:t.getBBox().x, y:t.getBBox().y,
                  right:t.getBBox().x+t.getBBox().width,
                  bottom:t.getBBox().y+t.getBBox().height,
                  family:getComputedStyle(t).fontFamily
                }))
            })""")
            assert all(
                t["x"] >= 0 and t["right"] <= 1120 and t["y"] >= 0 and t["bottom"] <= 792
                for t in geometry["labels"]
            )
            page.set_viewport_size({"width": 390, "height": 844})
            assert not page.evaluate("document.documentElement.scrollWidth>innerWidth")
            assert page.locator(".diagram-container").evaluate("e=>e.scrollWidth>e.clientWidth")
            page.set_viewport_size({"width": 1200, "height": 900})
            results.append({"name": name, "status": "PASS", **geometry})
        browser.close()
    out = ROOT / "docs/evidence/readme-manual-v1"
    out.mkdir(parents=True, exist_ok=True)
    (out / "diagram-render.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("PASS: two offline diagrams; labels in bounds and local mobile scrolling.")


if __name__ == "__main__":
    main()
