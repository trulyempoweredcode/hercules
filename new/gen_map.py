#!/usr/bin/env python3
"""Generate dotted world map background image."""
import base64, json, io, urllib.request, time
from pathlib import Path
from PIL import Image

ROOT = Path(r"D:/claude-custom-projects/Ai-Editor-Sites/hurcules-development.com-bespoke-v2")
IMG_DIR = ROOT / "images"
ENV = Path(r"D:/claude-custom-projects/Ai-Editor/.env")
API_KEY = next(l.split("=", 1)[1].strip() for l in ENV.read_text().splitlines() if l.startswith("GEMINI_API_KEY="))
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={API_KEY}"

prompt = (
    "World map rendered as a precise, ultra-minimal dot-matrix pattern. "
    "Pure black background (#000000). "
    "All continents and major landmasses (North America, South America, Europe, Africa, Asia, Australia) "
    "are rendered as densely-packed small circular dots in medium grey (#3a3a3a to #4d4d4d). "
    "Each dot is uniform size, approximately 6 pixels diameter, arranged on a strict regular grid with about 12 pixels spacing. "
    "Strict equirectangular projection covering the full frame edge to edge. "
    "Antarctica visible at the bottom but small. "
    "No text, no labels, no country borders, no graticule lines, no legend, no compass, no logos. "
    "Premium dataviz aesthetic, very clean, very minimal, professional fintech / enterprise feel. "
    "16:9 aspect ratio, 2000x1100. The dots are the ONLY element on the black background."
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
        if not png_b64: raise RuntimeError("no image returned")
        img = Image.open(io.BytesIO(base64.b64decode(png_b64))).convert("RGB")
        # crop to 16:9
        w, h = img.size; tr = 16/9
        if w/h > tr:
            nw = int(h*tr); l = (w-nw)//2
            img = img.crop((l, 0, l+nw, h))
        else:
            nh = int(w/tr); t = (h-nh)//2
            img = img.crop((0, t, w, t+nh))
        img = img.resize((2000, 1125), Image.LANCZOS)
        out = IMG_DIR / "dot-world.jpg"
        img.save(out, "JPEG", quality=88, optimize=True, progressive=True)
        print(f"saved {out.name} {out.stat().st_size//1024} KB")
        break
    except Exception as e:
        print(f"attempt {attempt+1} failed: {e}")
        time.sleep(3 * (attempt + 1))
