#!/usr/bin/env python3
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "product-landing.html"
TAG = "workflowguide-21"
BASE = "https://sduke510.github.io/workflow-guide-site"

def required(spec, key):
    value = spec.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"missing required field: {key}")
    return value

def escaped(value):
    return html.escape(str(value), quote=True)

def render_alternate_offers(spec):
    offers = spec.get("offers") or []
    if not offers:
        return ""
    cards = []
    for offer in offers:
        label = escaped(required(offer, "label"))
        merchant = escaped(required(offer, "merchant"))
        url = required(offer, "affiliate_url")
        if not str(url).startswith("https://"):
            raise ValueError("alternate offer affiliate_url must use https")
        note = escaped(offer.get("note", "Alternative Bezugsquelle"))
        cards.append(
            f'<a class="offer-card" href="{escaped(url)}" target="_blank" rel="sponsored noopener">'
            f'<span><strong>{merchant}</strong><small>{note}</small></span>'
            f'<b>{label} ↗</b></a>'
        )
    return (
        '<div class="alternate-offers"><div class="alternate-offers-head">'
        '<strong>Weitere Bezugsquellen</strong><span>Nur wenn ein aktiver Partnerlink vorhanden ist</span></div>'
        + "".join(cards) + "</div>"
    )

def structured_data(spec, canonical):
    payload = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": canonical + "#webpage",
                "url": canonical,
                "name": required(spec, "page_title"),
                "description": required(spec, "meta_description"),
                "inLanguage": "de-DE",
                "primaryImageOfPage": {
                    "@type": "ImageObject",
                    "url": required(spec, "editorial_image_url"),
                    "caption": required(spec, "image_disclosure"),
                },
                "isPartOf": {
                    "@type": "WebSite",
                    "@id": BASE + "/#website",
                    "url": BASE + "/",
                    "name": "Workflow Guide",
                },
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Startseite",
                        "item": BASE + "/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": required(spec, "breadcrumb"),
                        "item": canonical,
                    },
                ],
            },
        ],
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return '<script type="application/ld+json">' + raw.replace("</", "<\\/") + "</script>"

def generate(spec_path):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    content_id = required(spec, "content_id")
    slug = required(spec, "slug")
    asin = required(spec, "asin")
    image_url = required(spec, "editorial_image_url")

    if not str(content_id).startswith("C"):
        raise ValueError(f"{spec_path}: content_id must start with C")
    if not slug.endswith(".html"):
        slug += ".html"
    if "/" in slug or ".." in slug:
        raise ValueError(f"{spec_path}: slug must be a filename")
    if not str(image_url).startswith("https://"):
        raise ValueError(f"{spec_path}: editorial_image_url must use https")

    points = required(spec, "points")
    reasons = required(spec, "reasons")
    checks = required(spec, "checks")
    pin = required(spec, "pin")
    if len(points) != 4 or len(reasons) != 3 or len(checks) != 4:
        raise ValueError(f"{spec_path}: expected exactly 4 points, 3 reasons and 4 checks")

    canonical = f"{BASE}/pages/{slug}"
    affiliate = f"https://www.amazon.de/dp/{asin}?tag={TAG}"

    values = {
        "{{CANONICAL_URL}}": canonical,
        "{{EDITORIAL_IMAGE_URL}}": image_url,
        "{{AFFILIATE_URL}}": affiliate,
        "{{ASIN}}": asin,
        "{{POINT_1}}": points[0],
        "{{POINT_2}}": points[1],
        "{{POINT_3}}": points[2],
        "{{POINT_4}}": points[3],
        "{{REASON_1_TITLE}}": reasons[0]["title"],
        "{{REASON_1_TEXT}}": reasons[0]["text"],
        "{{REASON_2_TITLE}}": reasons[1]["title"],
        "{{REASON_2_TEXT}}": reasons[1]["text"],
        "{{REASON_3_TITLE}}": reasons[2]["title"],
        "{{REASON_3_TEXT}}": reasons[2]["text"],
        "{{CHECK_1}}": checks[0],
        "{{CHECK_2}}": checks[1],
        "{{CHECK_3}}": checks[2],
        "{{CHECK_4}}": checks[3],
    }
    mapping = {
        "PAGE_TITLE": "page_title",
        "META_DESCRIPTION": "meta_description",
        "OG_TITLE": "og_title",
        "OG_DESCRIPTION": "og_description",
        "BREADCRUMB": "breadcrumb",
        "EDITORIAL_IMAGE_ALT": "editorial_image_alt",
        "IMAGE_DISCLOSURE": "image_disclosure",
        "BADGE": "badge",
        "H1": "h1",
        "LEAD": "lead",
        "PRODUCT_NAME": "product_name",
        "PRODUCT_SUMMARY": "product_summary",
        "CTA": "cta",
        "REASONS_TITLE": "reasons_title",
    }
    for placeholder, key in mapping.items():
        values[f"{{{{{placeholder}}}}}"] = required(spec, key)

    page = TEMPLATE.read_text(encoding="utf-8")
    for placeholder, value in values.items():
        page = page.replace(placeholder, escaped(value))

    page = page.replace("{{ALTERNATE_OFFERS}}", render_alternate_offers(spec))
    page = page.replace("{{STRUCTURED_DATA}}", structured_data(spec, canonical))

    leftovers = [part for part in page.split() if "{{" in part or "}}" in part]
    if leftovers:
        raise ValueError(f"{spec_path}: unresolved template placeholders: {leftovers[:5]}")

    page_path = ROOT / "pages" / slug
    page_path.write_text(page, encoding="utf-8")

    pin_spec = {
        "id": content_id,
        "image_url": image_url,
        "badge": required(pin, "badge"),
        "title": required(pin, "title"),
        "subtitle": required(pin, "subtitle"),
        "cta": required(pin, "cta"),
        "credit": required(pin, "credit"),
        "output": f"assets/pins/{content_id}.jpg",
        "design_version": "CONVERSION_V2",
    }
    pin_path = ROOT / "pin_specs" / f"{content_id}.json"
    pin_path.write_text(json.dumps(pin_spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {page_path.relative_to(ROOT)} and {pin_path.relative_to(ROOT)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: generate_product_page.py product_specs/*.json")
    for path in sys.argv[1:]:
        generate(path)
