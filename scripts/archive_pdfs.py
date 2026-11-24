"""Archive only the explicitly listed, version-specific public arXiv PDFs."""
import hashlib
import html
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
data = json.loads((DOCS / "papers.json").read_text(encoding="utf-8"))
papers = data["papers"] if isinstance(data, dict) else data
out = DOCS / "pdfs"
out.mkdir(exist_ok=True)
manifest = []
page = (DOCS / "index.html").read_text(encoding="utf-8")

for paper in papers:
    version = paper["latest_version_id"]
    if not re.fullmatch(r"\d{4}\.\d{4,5}v[1-9]\d*", version):
        raise ValueError("Invalid version identifier")
    url = "https://arxiv.org/pdf/" + version
    if paper["version_pdf_url"] != url:
        raise ValueError("Only the recorded arXiv version URL may be fetched")
    target = out / (version + ".pdf")
    if target.exists():
        content = target.read_bytes()
    else:
        for attempt in range(3):
            try:
                request = urllib.request.Request(url, headers={
                    "User-Agent": "SrinivasaRaghavaResearchArchive/1.0 (+https://github.com/SRINIVASARAGHAVA/research-papers-srinivasa-raghava)"
                })
                with urllib.request.urlopen(request, timeout=90) as response:
                    content = response.read(20 * 1024 * 1024 + 1)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(5 * (attempt + 1))
        time.sleep(3)
    if not content.startswith(b"%PDF-") or b"%%EOF" not in content[-4096:]:
        raise ValueError("The response is not a complete PDF: " + version)
    if not 1000 < len(content) <= 20 * 1024 * 1024:
        raise ValueError("Unexpected PDF size: " + version)
    target.write_bytes(content)
    relative = "pdfs/" + version + ".pdf"
    page = page.replace('href="' + html.escape(url, quote=True) + '"', 'href="' + relative + '"')
    manifest.append({
        "arxiv_id": paper["arxiv_id"], "version": version,
        "title": paper["title"], "source_url": url,
        "file": relative, "size_bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "license_url": paper["license_url"]
    })
    print(version, len(content), "bytes")

(DOCS / "index.html").write_text(page, encoding="utf-8")
(out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print("Archived", len(manifest), "public paper versions.")
