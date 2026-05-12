#!/usr/bin/env python3
"""Regenerate the Capacity Crunch pattern — isometric wireframe blocks, grey outlines on white."""
import base64, json, io, urllib.request, time
from pathlib import Path
from PIL import Image

ROOT = Path(r"D:/claude-custom-projects/Ai-Editor-Sites/hurcules-development.com-bespoke-v3")
IMG_DIR = ROOT / "images"
ENV = Path(r"D:/claude-custom-projects/Ai-Editor/.env")
API_KEY = next(l.split("=", 1)[1].strip() for l in ENV.read_text().splitlines() if l.startswith("GEMINI_API_KEY="))
MODEL = "gemini-3-pro-image-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

prompt = (
    "An ultra-minimalist isometric geometric pattern composition. "
    "Pure white background (#ffffff). "
    "Thin line-drawing wireframes of stacked isometric 3D cubes and rectangular blocks, "
    "rendered as outline-only architectural blueprints. "
    "Each cube shows three visible faces with crisp single-pixel edges in light cool grey (#c9d0d9 to #b8c0cc), "
    "no fill, no shading. The cubes are arranged in a sparse, refined cluster — varying sizes, gently overlapping, "
    "stepping at isometric angles like an architectural diagram. "
    "Some cubes are small, some larger, with negative space between them. "
    "The cluster occupies the upper-right portion of the frame and fades gradually to pure white toward the left and bottom. "
    "Premium fintech / enterprise-tech infographic aesthetic. Editorial Bloomberg/Reuters quality. "
    "Strictly NO text, NO labels, NO logos, NO numbers, NO solid fills. Only clean grey wireframe outlines. "
    "1600x1200 pixels."
)

body = json.dumps({
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
}).encode()

for attempt in range(3):
    try:
        req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=240) as r:
            data = json.loads(r.read())
        png_b64 = None
        for c in data.get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                if p.get("inlineData", {}).get("data"):
                    png_b64 = p["inlineData"]["data"]; break
            if png_b64: break
        if not png_b64:
            raise RuntimeError(f"no image: {json.dumps(data)[:300]}")
        img = Image.open(io.BytesIO(base64.b64decode(png_b64))).convert("RGB")
        out = IMG_DIR / "pattern-isometric.png"
        img.save(out, "PNG", optimize=True)
        print(f"saved {out.name} {out.stat().st_size//1024} KB")
        break
    except Exception as e:
        print(f"attempt {attempt+1} failed: {e}")
        time.sleep(3 * (attempt + 1))
