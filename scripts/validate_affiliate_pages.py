#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAG = "workflowguide-21"

errors = []

product_pages = sorted((ROOT / "pages").glob("amazon-fund-*.html"))
extra = ROOT / "pages" / "oktoberfest-dirndl-bluse.html"
if extra.exists():
    product_pages.append(extra)

required_page_markers = [
    "product-shopline",
    "primary-buy",
    "product-direct-note",
    "Als Amazon-Partner verdiene ich an qualifizierten Verkäufen",
]

for page in product_pages:
    text = page.read_text(encoding="utf-8")
    for marker in required_page_markers:
        if marker not in text:
            errors.append(f"{page}: missing {marker!r}")
    if f"tag={TAG}" not in text:
        errors.append(f"{page}: missing Amazon partner tag")
    if "https://www.amazon.de/dp/" not in text:
        errors.append(f"{page}: missing direct amazon.de product URL")
    if "Stimmungsbild" not in text and "Produktkategorie" not in text:
        errors.append(f"{page}: editorial image is not clearly labelled")

for spec_path in sorted((ROOT / "pin_specs").glob("*.json")):
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    for key in ("id", "image_url", "title", "subtitle", "cta", "output"):
        if not str(spec.get(key, "")).strip():
            errors.append(f"{spec_path}: missing {key}")
    if "placehold.co" in spec.get("image_url", ""):
        errors.append(f"{spec_path}: placeholder image is not publishable")
    if not spec.get("output", "").startswith("assets/pins/"):
        errors.append(f"{spec_path}: output must live below assets/pins/")

queue_docs = ROOT / "docs" / "affiliate-product-pipeline.md"
if queue_docs.exists():
    text = queue_docs.read_text(encoding="utf-8")
    if "Image_URL" not in text:
        errors.append(f"{queue_docs}: image quality gate not documented")

if errors:
    print("Affiliate QA failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(f"Affiliate QA passed: {len(product_pages)} product pages and {len(list((ROOT / 'pin_specs').glob('*.json')))} pin specs checked.")
