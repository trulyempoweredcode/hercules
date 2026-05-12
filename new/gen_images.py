#!/usr/bin/env python3
"""Generate high-end imagery for Hercules Development bespoke site via Gemini 2.5 Flash Image (nano-banana)."""
import base64, json, os, sys, time, io, urllib.request, urllib.error
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Installing Pillow..."); os.system(f"{sys.executable} -m pip install --quiet Pillow"); from PIL import Image

ROOT = Path(r"D:/claude-custom-projects/Ai-Editor-Sites/hurcules-development.com-bespoke")
IMG_DIR = ROOT / "images"
ENV = Path(r"D:/claude-custom-projects/Ai-Editor/.env")

API_KEY = None
for line in ENV.read_text().splitlines():
    if line.startswith("GEMINI_API_KEY="):
        API_KEY = line.split("=", 1)[1].strip()
        break
assert API_KEY, "No GEMINI_API_KEY"

MODEL = "gemini-2.5-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

# Brand-aligned style anchor used in every prompt
STYLE = (
    "Editorial architectural photography, cinematic, ultra-high-end. "
    "Cool slate-blue and graphite palette with deep shadow. "
    "Late-blue-hour or pre-dawn lighting. "
    "Crisp focus, full-frame DSLR look, low ISO grain. "
    "No people. No logos. No text. "
    "Strictly NO transmission towers, NO overhead utility lines, NO grid pylons, NO substation switchyards visible. "
    "16:9 widescreen, 1600x900."
)

# Each tuple: (filename, aspect-w, aspect-h, prompt)
PROMPTS = [
    (
        "hero-campus.jpg", 1600, 900,
        (
            "Aerial cinematic photograph at pre-dawn blue hour of a remote modern hyperscale data center campus, "
            "self-contained and OFF-GRID. The campus shows: three or four large low-rise data hall buildings with clean white metal cladding and minimal fenestration, "
            "arranged in a precise grid with paved service roads between them; "
            "an adjacent on-site natural-gas powerhouse with industrial turbine exhaust stacks and rectangular generator buildings; "
            "large industrial gas pipework routed along the powerhouse; "
            "a paved central spine road with a perimeter security fence; "
            "soft mist over surrounding pine forest and rolling terrain in the background. "
            "Warm building uplights glow against a deep teal twilight sky. "
            "No utility poles, no transmission lines, no external substation switchyard. "
            f"{STYLE}"
        ),
    ),
    (
        "hero-pattern.jpg", 1600, 900,
        (
            "Abstract macro photograph of a high-tech data infrastructure surface: dense pattern of fibre-optic conduits "
            "and circular cable terminations in clean industrial metal, shot top-down with dramatic raking light. "
            "Subtle cyan and slate accents, deep navy background, soft falloff. "
            "Premium editorial finish, no text, no logos. "
            f"{STYLE}"
        ),
    ),
    (
        "data-hall.jpg", 1600, 900,
        (
            "Ultra-modern empty hyperscale data hall interior: long parallel aisles of dense liquid-cooled AI server racks "
            "with clean black cabinets and aqua status LEDs running in a precise rhythm. "
            "Polished epoxy floor reflects cool blue overhead light strips. Vanishing-point perspective down the central aisle. "
            "Visible coolant manifolds and discreet liquid-cooled distribution units beside the racks. "
            "Spotless, no people, no signage, no visible cables on the floor. "
            f"{STYLE}"
        ),
    ),
    (
        "powerhouse.jpg", 1600, 900,
        (
            "Editorial photograph of a modern on-site natural-gas powerhouse at twilight: parallel modular generator buildings "
            "with industrial exhaust stacks, large gas pipework along the elevation, integrated step-up transformers shielded by "
            "concrete blast walls. Crisp clean architecture, no overhead utility transmission lines, no pylons. "
            "Self-contained behind-the-meter energy plant. Cool industrial palette, dramatic side lighting. "
            f"{STYLE}"
        ),
    ),
    (
        "campus-perspective.jpg", 1600, 900,
        (
            "Ground-level architectural photograph of a hyperscale data hall exterior at dusk: a long, low, modern building with "
            "clean white metal cladding, recessed loading bays, slim horizontal LED accent strips, mirrored entrance vestibule. "
            "Wide paved approach in foreground, perimeter security fence visible in the middle distance, soft mountain silhouette "
            "behind. Premium corporate-architecture finish. No transmission lines or pylons anywhere. "
            f"{STYLE}"
        ),
    ),
    (
        "abstract-power.jpg", 1600, 900,
        (
            "Abstract subtle pattern macro photograph: precision-engineered industrial heat-exchange fins in soft cyan-tinted steel, "
            "shallow depth of field, diagonal repetition, very subtle and dark — usable as a section background. "
            "Cool slate palette, deep negative space, premium editorial quality, no text, no logos. "
            f"{STYLE}"
        ),
    ),
]


def gen(prompt: str, retries: int = 3) -> bytes:
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }).encode("utf-8")
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode("utf-8"))
            for cand in data.get("candidates", []):
                for part in cand.get("content", {}).get("parts", []):
                    inline = part.get("inlineData")
                    if inline and inline.get("data"):
                        return base64.b64decode(inline["data"])
            raise RuntimeError(f"no image in response: {json.dumps(data)[:400]}")
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as e:
            last_err = e
            print(f"  attempt {attempt+1} failed: {e}", flush=True)
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"all {retries} attempts failed: {last_err}")


def save(png_bytes: bytes, fname: str, w: int, h: int):
    img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    # crop to target aspect, center
    tw, th = w, h
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    target_ratio = tw / th
    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    elif src_ratio < target_ratio:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))
    img = img.resize((tw, th), Image.LANCZOS)
    out = IMG_DIR / fname
    img.save(out, "JPEG", quality=84, optimize=True, progressive=True)
    print(f"  saved {out.name}  {out.stat().st_size//1024} KB", flush=True)


def main():
    IMG_DIR.mkdir(exist_ok=True)
    for fname, w, h, prompt in PROMPTS:
        print(f"-> {fname}", flush=True)
        try:
            png = gen(prompt)
            save(png, fname, w, h)
        except Exception as e:
            print(f"  FAILED {fname}: {e}", flush=True)


if __name__ == "__main__":
    main()
