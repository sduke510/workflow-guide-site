#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAG = "workflowgui02-21"
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
    if page.name.startswith("amazon-fund-") and "application/ld+json" not in text:
        errors.append(f"{page}: missing structured data")

pin_specs = sorted((ROOT / "pin_specs").glob("*.json"))
for spec_path in pin_specs:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    for key in ("id", "image_url", "title", "subtitle", "cta", "output"):
        if not str(spec.get(key, "")).strip():
            errors.append(f"{spec_path}: missing {key}")
    if "placehold.co" in spec.get("image_url", ""):
        errors.append(f"{spec_path}: placeholder image is not publishable")
    if not spec.get("output", "").startswith("assets/pins/"):
        errors.append(f"{spec_path}: output must live below assets/pins/")

short_specs = sorted((ROOT / "short_specs").glob("*.json"))
for spec_path in short_specs:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    for key in ("video_id", "content_id", "product_id", "image_url", "hook", "scenes", "caption", "landing_url", "output"):
        if not spec.get(key):
            errors.append(f"{spec_path}: missing {key}")
    if len(spec.get("scenes", [])) != 4:
        errors.append(f"{spec_path}: expected 4 scenes")
    if not str(spec.get("output", "")).startswith("assets/shorts/"):
        errors.append(f"{spec_path}: output must live below assets/shorts/")

for dist_path in sorted((ROOT / "distribution").glob("*.json")):
    dist = json.loads(dist_path.read_text(encoding="utf-8"))
    seo = dist.get("seo", {})
    if not seo.get("canonical") or not seo.get("meta_description") or not seo.get("primary_query"):
        errors.append(f"{dist_path}: incomplete SEO payload")

sitemap = ROOT / "sitemap.xml"
if sitemap.exists():
    sitemap_text = sitemap.read_text(encoding="utf-8")
    for page in product_pages:
        page_text = page.read_text(encoding="utf-8")
        marker = 'rel="canonical" href="'
        if marker in page_text:
            canonical = page_text.split(marker, 1)[1].split('"', 1)[0]
            if canonical not in sitemap_text:
                errors.append(f"sitemap.xml: missing {canonical}")

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

print(
    "Affiliate QA passed: "
    f"{len(product_pages)} product pages, {len(pin_specs)} pin specs, "
    f"{len(short_specs)} short specs checked."
)
