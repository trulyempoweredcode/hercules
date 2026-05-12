#!/usr/bin/env python3
"""Round 2: replace rubbish powerhouse.jpg + add premium campus exterior + interior shots."""
import base64, json, os, sys, time, io, urllib.request, urllib.error
from pathlib import Path
from PIL import Image

ROOT = Path(r"D:/claude-custom-projects/Ai-Editor-Sites/hurcules-development.com-bespoke-v2")
IMG_DIR = ROOT / "images"
ENV = Path(r"D:/claude-custom-projects/Ai-Editor/.env")
API_KEY = next(l.split("=", 1)[1].strip() for l in ENV.read_text().splitlines() if l.startswith("GEMINI_API_KEY="))
MODEL = "gemini-2.5-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

STYLE = (
    "Architectural-Digest grade editorial photography. Cinematic, premium, prestigious. "
    "Cool slate-blue and deep-graphite palette with warm accent uplight. "
    "Late blue-hour / dusk lighting. Anamorphic widescreen feel, shallow grain, ultra-sharp. "
    "Full-frame Sony A1, 24mm or 50mm, low ISO, long exposure where appropriate. "
    "Strictly NO transmission towers, NO overhead utility lines, NO grid pylons, NO substation switchyards. "
    "No people, no logos, no signage with text. "
    "16:9 widescreen, 1600x900."
)

PROMPTS = [
    (
        "campus-twilight.jpg", 1600, 900,
        (
            "Cinematic ground-level wide-angle photograph of a vast, premium hyperscale data center campus at deep twilight. "
            "Multiple long, low, immaculately designed data hall buildings extend across the frame, with clean white metal cladding, "
            "horizontal LED accent strips glowing aqua at building roofline level, and recessed entrance bays softly illuminated. "
            "A precise paved boulevard with crisp linear lighting runs through the middle distance, perimeter security fence on the left. "
            "Wet, polished concrete foreground reflecting the building lights. "
            "Distant mountain silhouette and deep teal sky with a hint of warm horizon glow. "
            "Sense of immense scale, quiet power, billion-dollar infrastructure. "
            "Empty of people. Absolutely NO smoke stacks, NO chimneys, NO industrial exhaust pipework in view. "
            f"{STYLE}"
        ),
    ),
    (
        "racks-detail.jpg", 1600, 900,
        (
            "Cinematic close-up photograph of two facing rows of premium liquid-cooled AI server racks inside a hyperscale data hall. "
            "Tall black cabinets with smoked glass doors, dense vertical lines of aqua and white status LEDs glowing in precise rhythm, "
            "polished stainless coolant manifolds and translucent liquid-cooling tubes running along the rack tops, "
            "subtle reflections on the immaculate epoxy floor. Cool blue overhead light strips, dramatic chiaroscuro. "
            "Sharp focus on the nearest rack, gentle bokeh on the further racks. "
            "Empty of people. Hyper-modern, premium, billion-dollar AI infrastructure. "
            f"{STYLE}"
        ),
    ),
    (
        "noc-room.jpg", 1600, 900,
        (
            "Cinematic photograph of an empty modern network operations centre inside a hyperscale data center. "
            "A long curved console with multiple ergonomic operator stations faces a vast wall of seamless display panels, "
            "showing abstract telemetry dashboards, world map of dark fibre, and real-time campus power graphs (no readable text, no logos). "
            "Soft cool-blue ambient light, warm amber accent on the console surface, recessed LED strips on the ceiling. "
            "Empty chairs, immaculate, contemplative. Premium command-centre atmosphere, brushed metal and dark glass surfaces. "
            "Empty of people. "
            f"{STYLE}"
        ),
    ),
]


def gen(prompt: str, retries: int = 3) -> bytes:
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }).encode("utf-8")
    last = None
    for a in range(retries):
        try:
            req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode("utf-8"))
            for c in data.get("candidates", []):
                for p in c.get("content", {}).get("parts", []):
                    if p.get("inlineData", {}).get("data"):
                        return base64.b64decode(p["inlineData"]["data"])
            raise RuntimeError(f"no image: {json.dumps(data)[:300]}")
        except Exception as e:
            last = e; print(f"  retry {a+1}: {e}", flush=True); time.sleep(3 * (a + 1))
    raise RuntimeError(f"all retries failed: {last}")


def save(png: bytes, fname: str, w: int, h: int):
    img = Image.open(io.BytesIO(png)).convert("RGB")
    sw, sh = img.size; sr = sw / sh; tr = w / h
    if sr > tr:
        nw = int(sh * tr); l = (sw - nw) // 2
        img = img.crop((l, 0, l + nw, sh))
    elif sr < tr:
        nh = int(sw / tr); t = (sh - nh) // 2
        img = img.crop((0, t, sw, t + nh))
    img = img.resize((w, h), Image.LANCZOS)
    out = IMG_DIR / fname
    img.save(out, "JPEG", quality=85, optimize=True, progressive=True)
    print(f"  saved {out.name}  {out.stat().st_size // 1024} KB", flush=True)


for fname, w, h, prompt in PROMPTS:
    print(f"-> {fname}", flush=True)
    try:
        save(gen(prompt), fname, w, h)
    except Exception as e:
        print(f"  FAILED {fname}: {e}", flush=True)
