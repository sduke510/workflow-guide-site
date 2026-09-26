#!/usr/bin/env python3
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://sduke510.github.io/workflow-guide-site"

def canonical_for(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    if re.search(r'<meta\s+name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', text, re.I):
        return None
    match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', text, re.I)
    if match:
        return match.group(1)
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return BASE + "/"
    return BASE + "/" + rel

urls = []
for path in [ROOT / "index.html", *sorted((ROOT / "pages").glob("*.html"))]:
    url = canonical_for(path)
    if url and url not in urls:
        urls.append(url)

body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
body.extend(f"  <url><loc>{html.escape(url)}</loc></url>" for url in urls)
body.append("</urlset>")
(ROOT / "sitemap.xml").write_text("\n".join(body) + "\n", encoding="utf-8")
print(f"Updated sitemap.xml with {len(urls)} indexable URLs.")
