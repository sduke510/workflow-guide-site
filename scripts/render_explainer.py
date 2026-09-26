#!/usr/bin/env python3
import json
import math
import os
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H = 720, 1280
FPS = 20
BG_TOP = (10, 18, 35)
BG_BOTTOM = (28, 18, 42)
CREAM = (249, 246, 238)
WHITE = (255, 255, 255)
MUTED = (184, 190, 205)
CYAN = (75, 214, 210)
PINK = (245, 104, 154)
YELLOW = (246, 205, 90)
GREEN = (110, 214, 142)
RED = (242, 102, 104)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def fnt(path, size):
    return ImageFont.truetype(path, size=size)

def wrap(draw, text, font, width, max_lines=6):
    lines, current = [], ""
    for word in str(text).split():
        test = word if not current else current + " " + word
        if draw.textbbox((0, 0), test, font=font)[2] <= width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:max_lines]

def gradient():
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        p = y / (H - 1)
        c = tuple(int(BG_TOP[i] * (1-p) + BG_BOTTOM[i] * p) for i in range(3))
        for x in range(W):
            px[x, y] = c
    return img

BASE = gradient()

def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1-x) ** 3

def draw_lock(draw, cx, cy, scale=1.0, open_lock=False, color=CYAN):
    w, h = int(180*scale), int(150*scale)
    x0, y0 = cx-w//2, cy-h//2+35
    draw.rounded_rectangle((x0,y0,x0+w,y0+h), radius=int(26*scale), outline=color, width=max(3,int(8*scale)))
    arc_box=(cx-int(65*scale), cy-int(145*scale), cx+int(65*scale), cy+int(10*scale))
    if open_lock:
        draw.arc(arc_box, 195, 330, fill=color, width=max(3,int(8*scale)))
    else:
        draw.arc(arc_box, 180, 360, fill=color, width=max(3,int(8*scale)))
    draw.ellipse((cx-int(12*scale),cy+int(55*scale),cx+int(12*scale),cy+int(79*scale)), fill=color)

def draw_privacy(draw, t):
    cy=610
    draw.rounded_rectangle((90,490,630,730), radius=28, outline=CYAN, width=6)
    draw.text((125,520),"INKOGNITO",font=fnt(FONT_BOLD,36),fill=WHITE)
    draw.line((360,500,360,715),fill=MUTED,width=3)
    draw.text((122,585),"LOKAL",font=fnt(FONT_BOLD,24),fill=GREEN)
    draw.text((405,585),"ONLINE",font=fnt(FONT_BOLD,24),fill=PINK)
    draw.text((120,632),"Verlauf weg",font=fnt(FONT_REGULAR,25),fill=CREAM)
    draw.text((401,632),"IP bleibt",font=fnt(FONT_REGULAR,25),fill=CREAM)
    x = 120 + int(190 * ((math.sin(t*2.1)+1)/2))
    draw.ellipse((x,684,x+18,702),fill=YELLOW)

def draw_battery(draw, t):
    x0,y0,x1,y1=120,520,600,720
    draw.rounded_rectangle((x0,y0,x1,y1),radius=35,outline=WHITE,width=7)
    draw.rounded_rectangle((x1+2,585,x1+28,655),radius=8,fill=WHITE)
    level=min(1.0,0.12+t*0.035)
    fill_w=int((x1-x0-28)*level)
    draw.rounded_rectangle((x0+14,y0+14,x0+14+fill_w,y1-14),radius=24,fill=GREEN if level<.8 else YELLOW)
    draw.text((250,585),f"{int(level*100)}%",font=fnt(FONT_BOLD,48),fill=BG_TOP)
    draw.line((120,790,600,790),fill=MUTED,width=3)
    draw.line((120,790,480,650),fill=CYAN,width=7)
    draw.line((480,650,600,620),fill=YELLOW,width=7)
    draw.text((448,808),"ab ~80 %",font=fnt(FONT_REGULAR,22),fill=YELLOW)

def draw_passkey(draw, t):
    draw_lock(draw, 360, 610, 0.85, False, CYAN)
    draw.text((90,805),"Fake-Seite",font=fnt(FONT_BOLD,26),fill=RED)
    draw.text((492,805),"Echte Seite",font=fnt(FONT_BOLD,26),fill=GREEN)
    draw.line((165,770,300,670),fill=RED,width=5)
    draw.line((555,770,420,670),fill=GREEN,width=5)
    draw.text((123,850),"kein Passkey",font=fnt(FONT_REGULAR,22),fill=MUTED)
    draw.text((498,850),"passt",font=fnt(FONT_REGULAR,22),fill=MUTED)

def draw_generic(draw, t):
    r=100+int(12*math.sin(t*1.8))
    draw.ellipse((360-r,610-r,360+r,610+r),outline=CYAN,width=8)
    draw.ellipse((320,570,400,650),fill=PINK)

def draw_frame(spec, scene, scene_idx, scene_progress, total_progress, t):
    img=BASE.copy()
    draw=ImageDraw.Draw(img)
    accent=[CYAN,PINK,YELLOW,GREEN][scene_idx%4]

    # subtle moving decoration
    for i in range(7):
        xx=(70+i*105+int(16*math.sin(t*.7+i)))%W
        yy=190+i*132
        rr=4+(i%3)*2
        draw.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill=(42,50,72))

    draw.rounded_rectangle((40,38,680,100),radius=30,fill=(20,28,48))
    draw.text((68,57),spec.get("series","WORKFLOW GUIDE · DIGITAL EINFACH ERKLÄRT"),font=fnt(FONT_BOLD,18),fill=MUTED)

    intro=ease(scene_progress*3)
    yoff=int((1-intro)*28)
    head=fnt(FONT_BOLD,48 if scene_idx else 54)
    y=145+yoff
    for line in wrap(draw,scene["headline"],head,620,4):
        draw.text((50,y),line,font=head,fill=CREAM)
        y+=58

    body=fnt(FONT_REGULAR,27)
    y=max(y+18,340)
    for line in wrap(draw,scene.get("body",""),body,620,5):
        draw.text((50,y),line,font=body,fill=MUTED)
        y+=38

    visual=scene.get("visual","generic")
    if visual=="privacy":
        draw_privacy(draw,t)
    elif visual=="battery":
        draw_battery(draw,t)
    elif visual=="passkey":
        draw_passkey(draw,t)
    else:
        draw_generic(draw,t)

    # lower takeaway
    if scene.get("takeaway"):
        draw.rounded_rectangle((48,950,672,1112),radius=26,fill=(20,29,48),outline=accent,width=3)
        draw.text((76,978),"MERKSATZ",font=fnt(FONT_BOLD,19),fill=accent)
        yy=1012
        for line in wrap(draw,scene["takeaway"],fnt(FONT_BOLD,27),565,3):
            draw.text((76,yy),line,font=fnt(FONT_BOLD,27),fill=WHITE)
            yy+=36

    # scene dots + progress
    n=len(spec["scenes"])
    for i in range(n):
        x=50+i*26
        draw.ellipse((x,1160,x+11,1171),fill=accent if i==scene_idx else (80,86,105))
    draw.rounded_rectangle((50,1200,670,1210),radius=5,fill=(55,62,82))
    draw.rounded_rectangle((50,1200,50+int(620*total_progress),1210),radius=5,fill=accent)

    if scene_idx==len(spec["scenes"])-1:
        q=spec.get("question","")
        if q:
            draw.text((50,1230),q,font=fnt(FONT_BOLD,19),fill=CREAM)
    return img

def synthesize(text, wav_path):
    cmd=["piper","--model","de_DE-thorsten-medium","--length_scale","1.06","--output_file",str(wav_path)]
    subprocess.run(cmd,input=text.encode("utf-8"),check=True)

def wav_duration(path):
    with wave.open(str(path),"rb") as wf:
        return wf.getnframes()/wf.getframerate()

def render(spec_path):
    spec=json.loads(Path(spec_path).read_text(encoding="utf-8"))
    out=ROOT/spec["output"]
    out.parent.mkdir(parents=True,exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        wav=td/"voice.wav"
        synthesize(spec["narration"],wav)
        duration=wav_duration(wav)
        # keep a clean finish and guarantee TikTok > 60 s for rewards-eligible format.
        total=max(duration+2.0,62.0)
        scenes=spec["scenes"]
        weights=[float(s.get("weight",1)) for s in scenes]
        sw=sum(weights)
        durations=[total*w/sw for w in weights]
        starts=[0.0]
        for d in durations[:-1]:
            starts.append(starts[-1]+d)

        cmd=[
            "ffmpeg","-y","-loglevel","error",
            "-f","rawvideo","-vcodec","rawvideo","-pix_fmt","rgb24",
            "-s",f"{W}x{H}","-r",str(FPS),"-i","-",
            "-i",str(wav),
            "-filter_complex",f"[1:a]apad=pad_dur={max(0,total-duration):.3f}[a]",
            "-map","0:v","-map","[a]",
            "-c:v","libx264","-preset","veryfast","-crf","24","-pix_fmt","yuv420p",
            "-c:a","aac","-b:a","128k","-t",f"{total:.3f}","-movflags","+faststart",
            str(out)
        ]
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        frames=int(total*FPS)
        for n in range(frames):
            t=n/FPS
            idx=len(scenes)-1
            for i,start in enumerate(starts):
                if t < start+durations[i]:
                    idx=i
                    break
            sp=(t-starts[idx])/durations[idx]
            img=draw_frame(spec,scenes[idx],idx,sp,t/total,t)
            proc.stdin.write(img.tobytes())
        proc.stdin.close()
        rc=proc.wait()
        if rc:
            raise SystemExit(rc)
    print(f"Rendered {out.relative_to(ROOT)} ({total:.1f}s)")

if __name__=="__main__":
    if len(sys.argv)<2:
        raise SystemExit("Usage: render_explainer.py view_specs/*.json")
    for p in sys.argv[1:]:
        render(p)
