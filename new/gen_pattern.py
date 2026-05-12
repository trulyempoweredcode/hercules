#!/usr/bin/env python3
"""Generate a subtle geometric pattern for the Capacity Crunch section (top-right)."""
import base64, json, io, urllib.request, time
from pathlib import Path
from PIL import Image

ROOT = Path(r"D:/claude-custom-projects/Ai-Editor-Sites/hurcules-development.com-bespoke-v3")
IMG_DIR = ROOT / "images"
ENV = Path(r"D:/claude-custom-projects/Ai-Editor/.env")
API_KEY = next(l.split("=", 1)[1].strip() for l in ENV.read_text().splitlines() if l.startswith("GEMINI_API_KEY="))

# "nano banana 2" → gemini-3-pro-image-preview
MODEL = "gemini-3-pro-image-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

prompt = (
    "An ultra-minimalist premium geometric pattern composition. "
    "Pure white background (#ffffff). "
    "The pattern is composed of: large thin concentric circle arcs in light teal (#00b8d9 at 20-35% opacity) "
    "emanating from the top-right corner, intersecting with a sparse refined dotted grid in soft slate-grey "
    "and a few angled thin diagonal lines in light teal. "
    "The pattern is positioned in the upper-right portion of the frame and gradually fades to pure white "
    "on the left and bottom. "
    "Clean, refined, dataviz / fintech infographic aesthetic, premium editorial quality. "
    "Strictly no text, no labels, no logos, no numbers, no people. "
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
                    png_b64 = p["inlineData"]["data"]
                    break
            if png_b64: break
        if not png_b64:
            err_text = json.dumps(data)[:400]
            raise RuntimeError(f"no image returned: {err_text}")
        img = Image.open(io.BytesIO(base64.b64decode(png_b64))).convert("RGB")
        out = IMG_DIR / "pattern-geometric.png"
        img.save(out, "PNG", optimize=True)
        print(f"saved {out.name} {out.stat().st_size//1024} KB (model: {MODEL})")
        break
    except Exception as e:
        print(f"attempt {attempt+1} failed: {e}")
        time.sleep(3 * (attempt + 1))
