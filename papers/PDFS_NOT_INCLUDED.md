# Original article PDFs - not yet populated

This audited v3 ZIP does not contain original PDFs. The packaging environment could search and verify article pages but could not fetch the binary PDFs. The curated 25-paper manifest, including direct official article URLs, is provided instead. A legal-aware PDF downloader is bundled in `scripts/fetch_oa_papers.py`.

After unpacking this folder on an internet-connected device, execute from the package root:

```
python -m pip install -r scripts/requirements-download.txt
python scripts/fetch_oa_papers.py --manifest papers/papers_manifest.json --out papers/pdf
```

This helper attempts selected articles through PubMed Central's Open Access service. Metadata rights checks are best-effort only; **manual verification of article identity, current retraction status, attribution and redistribution rights remains required**. Internet access was not available during ZIP creation, so this command was NOT run online. Read the generated report and do not claim missing items are present.

For personal noncommercial **local reading only**, `--include-nc` can enable some `CC BY-NC` downloads; this does NOT automatically grant permission to repackage them in a shared ZIP or public repo. `CC BY-NC-ND` and unidentified licenses remain link-only by default.

A journal's freely readable landing page does not automatically grant redistribution rights. For GLARE / NeurIPS and LIT-PCBA original article, consult the official PDFs through their paper links rather than treating them as redistributable bundled binaries.
