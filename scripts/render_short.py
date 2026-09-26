#!/usr/bin/env python3
import io
import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
W, H = 720, 1280
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

def download_image(url):
    req = urllib.request.Request(url, headers={"User-Agent": "WorkflowGuideShortRenderer/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return Image.open(io.BytesIO(resp.read())).convert("RGB")

def wrap(draw, text, fnt, width, max_lines=6):
    lines = []
    for paragraph in str(text).split("\n"):
        words = paragraph.split()
        current = ""
        for word in words:
            test = word if not current else current + " " + word
            if draw.textbbox((0, 0), test, font=fnt)[2] <= width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines[:max_lines]

def draw_card(image, scene, badge, disclosure, final=False, platform_safe=False):
    canvas = Image.new("RGB", (W, H), CREAM)
    photo_h = 610
    photo = ImageOps.fit(image, (W, photo_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    canvas.paste(photo, (0, 0))
    overlay = Image.new("RGBA", (W, photo_h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 0, W, photo_h), fill=(40, 14, 22, 45))
    canvas.paste(overlay, (0, 0), overlay)

    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, photo_h - 10, W, H), fill=BURGUNDY_DARK if final else BURGUNDY)
    draw.rectangle((0, photo_h - 10, 12, H), fill=OLIVE)

    badge_f = font(FONT_BOLD, 20)
    badge_text = str(badge).upper()
    bw = min(draw.textbbox((0, 0), badge_text, font=badge_f)[2] + 38, W - 70)
    draw.rounded_rectangle((34, 34, 34 + bw, 82), radius=24, fill=OLIVE)
    draw.text((53, 47), badge_text, font=badge_f, fill=WHITE)

    if not platform_safe:
        brand_f = font(FONT_BOLD, 19)
        draw.text((42, photo_h + 30), "WORKFLOW GUIDE", font=brand_f, fill=OLIVE)
        y = photo_h + 76
    else:
        y = photo_h + 40

    head_f = font(FONT_BOLD, 45 if not final else 49)
    for line in wrap(draw, scene["headline"], head_f, W - 84, 4):
        draw.text((42, y), line, font=head_f, fill=CREAM)
        y += 55

    body_f = font(FONT_REGULAR, 27)
    y += 16
    for line in wrap(draw, scene.get("body", ""), body_f, W - 84, 7):
        draw.text((42, y), line, font=body_f, fill=MUTED)
        y += 38

    if final and not platform_safe:
        cta_f = font(FONT_BOLD, 24)
        draw.rounded_rectangle((42, min(y + 26, 1110), W - 42, min(y + 92, 1176)), radius=28, fill=OLIVE)
        draw.text((70, min(y + 45, 1129)), "LINK AUF DER ZIELSEITE →", font=cta_f, fill=WHITE)

    foot_f = font(FONT_REGULAR, 16)
    draw.text((42, H - 45), disclosure, font=foot_f, fill=MUTED)
    return canvas

def render_variant(image, scenes, out, badge, disclosure, platform_safe=False):
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cards = []
        for idx, scene in enumerate(scenes):
            card = draw_card(
                image,
                scene,
                badge,
                disclosure,
                final=(idx == len(scenes) - 1),
                platform_safe=platform_safe,
            )
            card_path = td / f"card-{idx}.jpg"
            card.save(card_path, "JPEG", quality=92, optimize=True)
            cards.append(card_path)

        concat_path = td / "concat.txt"
        lines = []
        durations = [2.6, 2.6, 2.6, 3.2]
        for card, duration in zip(cards, durations):
            lines.append(f"file '{card.as_posix()}'")
            lines.append(f"duration {duration}")
        lines.append(f"file '{cards[-1].as_posix()}'")
        concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat_path),
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-vf", "fps=25,format=yuv420p",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
            "-c:a", "aac", "-b:a", "64k",
            "-shortest", "-movflags", "+faststart",
            str(out),
        ]
        subprocess.run(cmd, check=True)

def render(spec_path):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    image = download_image(spec["image_url"])
    scenes = spec["scenes"]
    if len(scenes) != 4:
        raise ValueError(f"{spec_path}: expected 4 scenes")

    out = ROOT / spec["output"]
    render_variant(
        image,
        scenes,
        out,
        spec.get("badge", "PRODUKT-CHECK"),
        spec.get("disclosure", "Werbung"),
        platform_safe=False,
    )
    print(f"Rendered {out.relative_to(ROOT)}")

    tiktok_scenes = [dict(scene) for scene in scenes[:3]]
    tiktok_scenes.append({
        "headline": "Kurz zusammengefasst",
        "body": "Produktdetails, Varianten und Verfügbarkeit vor dem Kauf direkt beim Anbieter prüfen.",
    })
    tiktok_out = out.with_name(out.stem + "-tiktok" + out.suffix)
    render_variant(
        image,
        tiktok_scenes,
        tiktok_out,
        spec.get("badge", "PRODUKT-CHECK"),
        "Werbung",
        platform_safe=True,
    )
    print(f"Rendered {tiktok_out.relative_to(ROOT)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: render_short.py short_specs/*.json")
    for path in sys.argv[1:]:
        render(path)
