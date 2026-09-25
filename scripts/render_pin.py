#!/usr/bin/env python3
import io
import json
import sys
import textwrap
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1000, 1500
BURGUNDY = "#6f2337"
BURGUNDY_DARK = "#4b1725"
OLIVE = "#7b813f"
CREAM = "#faf7f0"
WHITE = "#ffffff"
MUTED = "#e7ddd4"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font(path, size):
    return ImageFont.truetype(path, size=size)

def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = word if not current else current + " " + word
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def download_image(url):
    req = urllib.request.Request(url, headers={"User-Agent": "WorkflowGuidePinRenderer/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return Image.open(io.BytesIO(resp.read())).convert("RGB")

def render(spec_path):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    image = download_image(spec["image_url"])
    canvas = Image.new("RGB", (W, H), CREAM)

    photo_height = 910
    photo = ImageOps.fit(image, (W, photo_height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.48))
    canvas.paste(photo, (0, 0))

    overlay = Image.new("RGBA", (W, 220), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(220):
        alpha = int(150 * (y / 219))
        od.rectangle((0, y, W, y + 1), fill=(45, 18, 25, alpha))
    canvas.paste(overlay.convert("RGB"), (0, photo_height - 220))

    draw = ImageDraw.Draw(canvas)

    # Badge
    badge = spec.get("badge", "AMAZON-FUND")
    badge_f = font(FONT_BOLD, 28)
    bx1, by1 = 54, 54
    bw = draw.textbbox((0, 0), badge, font=badge_f)[2] + 52
    draw.rounded_rectangle((bx1, by1, bx1 + bw, by1 + 62), radius=31, fill=OLIVE)
    draw.text((bx1 + 26, by1 + 14), badge, font=badge_f, fill=WHITE)

    # Bottom panel
    panel_y = 830
    draw.rectangle((0, panel_y, W, H), fill=BURGUNDY)
    draw.rectangle((0, panel_y, 18, H), fill=OLIVE)

    brand_f = font(FONT_BOLD, 25)
    draw.text((64, panel_y + 54), "WORKFLOW GUIDE", font=brand_f, fill=OLIVE)

    title_f = font(FONT_BOLD, 68)
    title_lines = wrap_text(draw, spec["title"], title_f, 870)
    y = panel_y + 112
    for line in title_lines[:4]:
        draw.text((64, y), line, font=title_f, fill=CREAM)
        y += 82

    subtitle = spec.get("subtitle", "")
    if subtitle:
        sub_f = font(FONT_REGULAR, 31)
        for line in wrap_text(draw, subtitle, sub_f, 860)[:3]:
            draw.text((64, y + 14), line, font=sub_f, fill=MUTED)
            y += 44

    cta = spec.get("cta", "Fund ansehen")
    cta_f = font(FONT_BOLD, 29)
    cta_w = draw.textbbox((0, 0), cta, font=cta_f)[2] + 58
    cta_y = min(max(y + 42, 1290), 1350)
    draw.rounded_rectangle((64, cta_y, 64 + cta_w, cta_y + 62), radius=31, fill=OLIVE)
    draw.text((93, cta_y + 14), cta, font=cta_f, fill=WHITE)

    footer_f = font(FONT_REGULAR, 19)
    credit = spec.get("credit", "")
    disclosure = "Werbung · Affiliate-Link auf Zielseite"
    draw.text((64, H - 62), disclosure, font=footer_f, fill=MUTED)
    if credit:
        credit_w = draw.textbbox((0, 0), credit, font=footer_f)[2]
        draw.text((W - 56 - credit_w, H - 62), credit, font=footer_f, fill=MUTED)

    # Fine border
    draw.rectangle((8, 8, W - 9, H - 9), outline=CREAM, width=3)

    out = Path(spec["output"])
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, format="JPEG", quality=92, optimize=True, progressive=True)
    print(f"Rendered {out}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: render_pin.py pin_specs/*.json")
    for spec in sys.argv[1:]:
        render(spec)
