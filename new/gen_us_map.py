#!/usr/bin/env python3
"""Generate USA-only topographic style map."""
import base64, json, io, urllib.request, time
from pathlib import Path
from PIL import Image, ImageEnhance

ROOT = Path(r"D:/claude-custom-projects/Ai-Editor-Sites/hurcules-development.com-bespoke-v2")
IMG_DIR = ROOT / "images"
ENV = Path(r"D:/claude-custom-projects/Ai-Editor/.env")
API_KEY = next(l.split("=", 1)[1].strip() for l in ENV.read_text().splitlines() if l.startswith("GEMINI_API_KEY="))
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={API_KEY}"

prompt = (
    "A premium architectural-blueprint map of just the contiguous United States, lower 48 states only. "
    "NO Alaska, NO Hawaii, NO Canada, NO Mexico, NO Caribbean — just the contiguous US silhouette centred in the frame. "
    "The US shape is filled with a fine-grained pattern of intersecting topographic contour lines and a faint hexagonal grid mesh, "
    "rendered in cool cyan-teal (#1a3a4a to #2a6478) on a pure black background (#000). "
    "Outside the US silhouette is pure black — empty space, no other landmasses. "
    "Soft inner glow along the US perimeter outline in slightly brighter cyan. "
    "Subtle scattered slightly-brighter cyan-teal dot accents inside the US shape suggesting infrastructure nodes "
    "(but no specific city markers, no labels, no text). "
    "Premium fintech/dataviz/architectural-drawing aesthetic. Editorial Bloomberg-Reuters infographic quality. "
    "Strictly NO text, NO labels, NO state borders visible, NO country names, NO graticule, NO compass, NO legend, NO logos. "
    "16:9 widescreen, 2000x1125."
)

body = json.dumps({
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
}).encode()
for attempt in range(3):
    try:
        req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read())
        png_b64 = None
        for c in data.get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                if p.get("inlineData", {}).get("data"):
                    png_b64 = p["inlineData"]["data"]; break
        if not png_b64: raise RuntimeError("no image")
        img = Image.open(io.BytesIO(base64.b64decode(png_b64))).convert("RGB")
        w, h = img.size; tr = 16/9
        if w/h > tr:
            nw = int(h*tr); l = (w-nw)//2
            img = img.crop((l, 0, l+nw, h))
        else:
            nh = int(w/tr); t = (h-nh)//2
            img = img.crop((0, t, w, t+nh))
        img = img.resize((2000, 1125), Image.LANCZOS)
        img = ImageEnhance.Sharpness(img).enhance(1.2)
        out = IMG_DIR / "us-map.jpg"
        img.save(out, "JPEG", quality=92, optimize=True, progressive=True)
        print(f"saved {out.name} {out.stat().st_size//1024} KB")
        break
    except Exception as e:
        print(f"attempt {attempt+1} failed: {e}")
        time.sleep(3 * (attempt + 1))
