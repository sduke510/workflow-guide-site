# Product specs

One JSON file in this directory is the source of truth for one conversion-first affiliate product page and its Pinterest creative.

The generator derives:
- the canonical GitHub Pages URL;
- the Amazon.de product URL from the ASIN;
- the PartnerNet tag `workflowguide-21`;
- the HTML page from `templates/product-landing.html`;
- a matching `pin_specs/Cxxx.json` entry.

Rules:
- Use only product facts present in Product_DB or another verified source.
- Never hard-code Amazon price, stock, rating or delivery claims.
- Editorial images must be owned/licensed and must be labelled as category/mood imagery, not as the exact Amazon product.
- Every product page must point directly to one concrete Amazon.de product page.
- Comparison/list pages are intentionally not auto-published by the conversion-first queue.
