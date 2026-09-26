#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://sduke510.github.io/workflow-guide-site"

targets = sorted((ROOT / "pages").glob("amazon-fund-*.html"))
extra = ROOT / "pages" / "oktoberfest-dirndl-bluse.html"
if extra.exists():
    targets.append(extra)

def extract(text, pattern, default=""):
    m = re.search(pattern, text, re.I | re.S)
    return m.group(1).strip() if m else default

for path in targets:
    text = path.read_text(encoding="utf-8")
    if 'application/ld+json' in text:
        continue
    canonical = extract(text, r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)')
    title = extract(text, r'<title>(.*?)</title>')
    description = extract(text, r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)')
    image = extract(text, r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)')
    if not canonical:
        canonical = f"{BASE}/pages/{path.name}"
    payload = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": canonical + "#webpage",
                "url": canonical,
                "name": title,
                "description": description,
                "inLanguage": "de-DE",
                "isPartOf": {"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": "Workflow Guide"},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Startseite", "item": BASE + "/"},
                    {"@type": "ListItem", "position": 2, "name": title, "item": canonical},
                ],
            },
        ],
    }
    if image:
        payload["@graph"][0]["primaryImageOfPage"] = {"@type": "ImageObject", "url": image}
    markup = '<script type="application/ld+json">' + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + '</script>\n'
    text = text.replace("</head>", markup + "</head>", 1)
    path.write_text(text, encoding="utf-8")
    print(f"Added JSON-LD to {path.relative_to(ROOT)}")
