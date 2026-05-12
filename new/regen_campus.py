#!/usr/bin/env python3
"""Regenerate campus-twilight at higher sharpness."""
import base64, json, io, urllib.request, time
from pathlib import Path
from PIL import Image, ImageEnhance

ROOT = Path(r"D:/claude-custom-projects/Ai-Editor-Sites/hurcules-development.com-bespoke-v2")
IMG_DIR = ROOT / "images"
ENV = Path(r"D:/claude-custom-projects/Ai-Editor/.env")
API_KEY = next(l.split("=", 1)[1].strip() for l in ENV.read_text().splitlines() if l.startswith("GEMINI_API_KEY="))
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={API_KEY}"

prompt = (
    "Razor-sharp, tack-sharp cinematic wide-angle photograph of a vast premium hyperscale data center campus at deep twilight. "
    "Multiple long, low, immaculately designed data hall buildings extend across the frame in precise alignment, "
    "clean white metal cladding, slim horizontal aqua LED accent strips at roofline level, recessed entrance bays softly illuminated. "
    "Polished concrete boulevard in foreground with crisp specular reflections. "
    "Distant mountain silhouette and deep teal sky with hint of warm horizon glow. "
    "Hyper-detailed, ultra-high resolution, every panel seam in focus, every reflection crisp. "
    "Shot on 100MP medium-format digital, Phase One IQ4, 80mm lens at f/8, ISO 50, tripod long exposure. "
    "Architectural-Digest editorial. Cool slate-blue and graphite palette. "
    "No people, no logos, no signage. "
    "STRICTLY no transmission towers, no smoke stacks, no overhead utility lines, no industrial pipework. "
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
        # Subtle sharpen pass for crispness
        img = ImageEnhance.Sharpness(img).enhance(1.35)
        out = IMG_DIR / "campus-twilight.jpg"
        img.save(out, "JPEG", quality=92, optimize=True, progressive=True)
        print(f"saved {out.name} {out.stat().st_size//1024} KB")
        break
    except Exception as e:
        print(f"attempt {attempt+1} failed: {e}")
        time.sleep(3 * (attempt + 1))
