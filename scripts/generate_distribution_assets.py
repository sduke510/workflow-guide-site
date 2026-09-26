#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://sduke510.github.io/workflow-guide-site"

def required(spec, key):
    value = spec.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"missing required field: {key}")
    return value

def clean(text):
    return re.sub(r"\s+", " ", str(text)).strip()

def generate(spec_path):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    cid = required(spec, "content_id")
    pid = required(spec, "product_id")
    slug = required(spec, "slug")
    if not slug.endswith(".html"):
        slug += ".html"
    landing = f"{BASE}/pages/{slug}"
    pin = required(spec, "pin")
    points = required(spec, "points")
    checks = required(spec, "checks")

    hook = clean(pin.get("title") or spec["h1"])
    seo = {
        "content_id": cid,
        "product_id": pid,
        "landing_url": landing,
        "primary_query": clean(spec["product_name"]),
        "search_intent": "commercial_research",
        "title": clean(spec["page_title"]),
        "meta_description": clean(spec["meta_description"]),
        "canonical": landing,
        "indexable": True,
        "sitemap_required": True,
    }

    script_lines = [
        hook,
        clean(spec["lead"]),
        clean(points[0]).lstrip("✓ ").strip(),
        clean(checks[0]),
        "Den konkreten Fund findest du über die Zielseite. Dort führt der Button direkt zum ausgewählten Artikel auf Amazon.de.",
    ]
    caption = (
        f"Werbung | {hook} "
        f"Auf der Zielseite findest du den konkreten Fund und einen direkten Produktlink zu Amazon.de. "
        "Produktdetails, Preis, Varianten und Lieferzeit bitte beim Shop prüfen."
    )
    short = {
        "video_id": f"V{cid[1:]}",
        "content_id": cid,
        "product_id": pid,
        "image_url": required(spec, "editorial_image_url"),
        "image_disclosure": required(spec, "image_disclosure"),
        "badge": clean(pin.get("badge", "PRODUKT-CHECK")),
        "hook": hook,
        "scenes": [
            {"headline": hook, "body": "Konkreter Fund · schneller Produkt-Check"},
            {"headline": "Warum interessant?", "body": clean(points[0]).lstrip("✓ ").strip() + "\n" + clean(points[1]).lstrip("✓ ").strip()},
            {"headline": "Vor dem Kauf prüfen", "body": clean(checks[0]) + "\n" + clean(checks[1])},
            {"headline": "Produkt ansehen", "body": "Zielseite öffnen → direkter Link zum ausgewählten Artikel auf Amazon.de"},
        ],
        "caption": caption,
        "cta": "Produkt über die Zielseite ansehen",
        "landing_url": landing,
        "output": f"assets/shorts/{cid}.mp4",
        "platforms": ["youtube_shorts", "instagram_reels", "tiktok"],
        "disclosure": "Werbung · Affiliate-Link auf Zielseite",
        "status": "READY_FOR_RENDER",
    }

    ddir = ROOT / "distribution"
    sdir = ROOT / "short_specs"
    ddir.mkdir(parents=True, exist_ok=True)
    sdir.mkdir(parents=True, exist_ok=True)
    (ddir / f"{cid}.json").write_text(json.dumps({"seo": seo, "short": short}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (sdir / f"{cid}.json").write_text(json.dumps(short, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated distribution/{cid}.json and short_specs/{cid}.json")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: generate_distribution_assets.py product_specs/*.json")
    for path in sys.argv[1:]:
        generate(path)
