#!/usr/bin/env python3
import html
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=(ROOT/"templates"/"explainer.html").read_text(encoding="utf-8")
BASE="https://sduke510.github.io/workflow-guide-site"

def render(path):
    spec=json.loads(Path(path).read_text(encoding="utf-8"))
    slug=spec["slug"]
    title=spec["title"]
    description=spec.get("description") or spec["scenes"][0].get("takeaway") or title
    summary=spec.get("summary") or spec["scenes"][-1].get("takeaway") or description
    canonical=f"{BASE}/pages/{slug}.html"
    video_url=f"{BASE}/{spec['output']}"
    sources=[]
    for url in spec.get("sources",[]):
        label=url.split("//",1)[-1].split("/",1)[0]
        sources.append(f'<li><a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(label)}</a></li>')
    page=TEMPLATE
    replacements={
        "{{TITLE}}":html.escape(title),
        "{{DESCRIPTION}}":html.escape(description),
        "{{CANONICAL}}":html.escape(canonical),
        "{{VIDEO_URL}}":html.escape(video_url),
        "{{SUMMARY}}":html.escape(summary),
        "{{SOURCES}}":"\n".join(sources)
    }
    for key,val in replacements.items():
        page=page.replace(key,val)
    out=ROOT/"pages"/f"{slug}.html"
    out.write_text(page,encoding="utf-8")
    print(f"Generated {out.relative_to(ROOT)}")

if __name__=="__main__":
    for p in sys.argv[1:]:
        render(p)
