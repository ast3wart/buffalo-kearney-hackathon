"""Render an in-cabinet photo of EVERY component (RENDERED, not real photos; labeled as such).

    python scripts/render_test_photos.py      # -> data/seed/demo/<plant>/photos/*.jpg + photos.csv

Each image shows the part mounted where it lives: a PLC module on a DIN rail, a drive with keypad and heat sink,
an HMI screen in a door bezel, servo modules, power supplies and relays, with wire ducts and wiring around it, and
the device's own label sticker carrying its real catalog number. Phone-photo wear is added (tilt, blur, noise,
glare, scuffs, cut-off framing). Image recognition then reads them for real (xray/extract.py).
"""
import random
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "data/seed/demo"
R = random.Random(11)
W, H = 900, 600
FONTS = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
         "/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf"]
QUALITY = ["ok"] * 14 + ["glare", "glare", "blurry", "worn", "cut_off"]


def font(size, bold=False):
    for f in (FONTS if bold else FONTS[1:]):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def cabinet(d):
    d.rectangle([0, 0, W, H], fill=R.choice([(214, 210, 196), (200, 204, 206), (226, 222, 210)]))  # backplate
    for y in (40, H - 90):  # slotted wire ducts
        d.rectangle([0, y, W, y + 50], fill=(150, 152, 150))
        for x in range(0, W, 22):
            d.rectangle([x, y, x + 12, y + 50], fill=(128, 130, 128))
    d.rectangle([0, 150, W, 172], fill=(185, 185, 180))  # DIN rail
    for _ in range(14):  # wiring
        x = R.randint(20, W - 20)
        d.line([x, 90, x + R.randint(-30, 30), 150], fill=R.choice([(30, 60, 160), (190, 30, 30), (20, 20, 20), (230, 200, 40)]), width=4)


def sticker(d, x, y, mfr, part, scale=1.0):
    big = font(int(34 * scale), True)
    w, h = max(int(330 * scale), int(big.getlength(part)) + int(24 * scale)), int(118 * scale)
    d.rectangle([x, y, x + w, y + h], fill=(246, 246, 240), outline=(60, 60, 60), width=2)
    d.text((x + 10, y + 6), mfr.upper()[:24], fill=(25, 25, 25), font=font(int(20 * scale), True))
    d.text((x + 10, y + 32), "CAT", fill=(70, 70, 70), font=font(int(15 * scale)))
    d.text((x + 10, y + 50), part, fill=(10, 10, 10), font=font(int(34 * scale), True))
    d.text((x + 10, y + 92), f"SER {R.choice('ABCDE')}  S/N {R.randint(100000, 999999)}", fill=(60, 60, 60), font=font(int(15 * scale)))
    return (x, y + 50, x + w, y + 92)  # catalog-number line (for scuffs)


def device(d, ctype, mfr, part):
    dark = R.choice([(38, 40, 44), (52, 56, 60), (70, 74, 78)])
    if ctype in ("plc", "plc_io", "power_supply", "network", "safety_relay", "other"):
        x0 = R.randint(60, 140)
        for i in range(R.randint(2, 4)):  # neighbouring modules on the rail
            d.rectangle([x0 + i * 95, 120, x0 + i * 95 + 88, 470], fill=dark, outline=(20, 20, 20), width=2)
            for j in range(3):
                d.ellipse([x0 + i * 95 + 12, 140 + j * 22, x0 + i * 95 + 24, 152 + j * 22], fill=R.choice([(40, 200, 60), (40, 200, 60), (230, 160, 30)]))
        mx = x0 + 3 * 95 + 20
        d.rectangle([mx, 110, mx + 360, 480], fill=dark, outline=(15, 15, 15), width=3)  # the device itself
        d.rectangle([mx + 20, 130, mx + 120, 190], fill=(25, 25, 25))
        for j, c in enumerate([(40, 200, 60), (40, 200, 60), (220, 40, 40)]):
            d.ellipse([mx + 30 + j * 28, 150, mx + 46 + j * 28, 166], fill=c)
        return sticker(d, mx + 15, 300, mfr, part, 1.0)
    if ctype in ("drive", "servo_drive"):
        tall = ctype == "servo_drive"
        mx = R.randint(180, 300)
        w = 230 if tall else 330
        d.rectangle([mx, 70, mx + w, 540], fill=dark, outline=(15, 15, 15), width=3)
        for k in range(10):  # heat sink fins
            d.rectangle([mx + w + 6, 90 + k * 42, mx + w + 40, 110 + k * 42], fill=(120, 124, 128))
        d.rectangle([mx + 25, 100, mx + w - 25, 170], fill=(20, 30, 20))  # keypad display
        d.text((mx + 40, 118), "  0.0 Hz" if not tall else " AXIS OK", fill=(90, 230, 120), font=font(30, True))
        for k in range(4):
            d.rectangle([mx + 30 + k * 48, 190, mx + 66 + k * 48, 220], fill=(90, 92, 96))
        return sticker(d, mx + 8, 330, mfr, part, 0.95 if not tall else 0.68)
    # hmi: screen in a door bezel
    d.rectangle([90, 60, W - 90, H - 60], fill=(60, 62, 66), outline=(20, 20, 20), width=4)
    d.rectangle([130, 95, W - 130, 360], fill=(24, 60, 96))
    d.text((160, 120), "LINE STATUS   RUNNING", fill=(220, 230, 240), font=font(30, True))
    d.rectangle([160, 180, 420, 240], fill=(40, 150, 70))
    return sticker(d, 300, 400, mfr, part, 0.9)


def photo(ctype, mfr, part, quality):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    cabinet(d)
    cat = device(d, ctype, mfr, part)
    if quality == "worn":
        for _ in range(R.randint(5, 9)):
            x, y = R.randint(cat[0] + 10, cat[2] - 40), R.randint(cat[1], cat[3] - 4)
            d.line([x, y, x + R.randint(15, 50), y + R.randint(-5, 5)], fill=(246, 246, 240), width=R.randint(3, 6))
    img = img.rotate(R.uniform(-6, 6) if quality != "glare" else R.uniform(-12, 12), fillcolor=(90, 90, 90))
    if quality == "cut_off":
        img = img.crop((0, 0, int(W * 0.68), H)).resize((int(W * 0.68), H))
    img = img.filter(ImageFilter.GaussianBlur(R.uniform(0.5, 1.0) if quality != "blurry" else R.uniform(2.2, 2.8)))
    px = img.load()
    for _ in range(img.width * img.height // 30):
        x, y = R.randrange(img.width), R.randrange(img.height)
        r, g, b = px[x, y]
        n = R.randint(-18, 18)
        px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)))
    if quality == "glare" or R.random() < 0.25:
        m = Image.new("L", img.size, 0)
        gx, gy = cat[0] + R.randint(40, 220), cat[1] + R.randint(-10, 30)
        ImageDraw.Draw(m).ellipse([gx - 130, gy - 70, gx + 130, gy + 70], fill=165 if quality == "glare" else 80)
        img = Image.composite(Image.new("RGB", img.size, (255, 255, 250)), img, m.filter(ImageFilter.GaussianBlur(40)))
    return img


def main():
    kb = pd.read_csv(ROOT / "data/reference/kb.csv", dtype=str).fillna("").set_index("kb_id")
    truth = pd.read_csv(ROOT / "data/truth/demo/components.csv", dtype=str).fillna("")
    reads = pd.concat(pd.read_csv(f, dtype=str) for f in SEED.glob("*/readings.csv")).set_index("component_id")
    critical = set(pd.read_csv(ROOT / "data/truth/demo/spof.csv", dtype=str).component_id)
    rows = []
    for i, t in enumerate(truth.itertuples()):
        pid = t.component_id[:2]
        if t.kb_id:
            k = kb.loc[t.kb_id]
            mfr, part, ctype = k.manufacturer, k.part_no, k.component_type
        else:  # commodity part: its own label text, e.g. "PHOENIX CONTACT QUINT-PS/1AC/24DC/10"
            text = reads.loc[t.component_id, "raw_text"].replace("CAT ", "").replace("…", "")
            words = text.split()
            mfr, part, ctype = " ".join(words[:2]), " ".join(words[2:]) or words[-1], reads.loc[t.component_id, "component_type_hint"]
        q = "ok" if t.component_id in critical else R.choice(QUALITY)
        photo_id = f"{pid}-IMG{i + 1:04d}"
        out = SEED / pid / "photos" / f"{photo_id}.jpg"
        out.parent.mkdir(parents=True, exist_ok=True)
        photo(ctype, mfr, part, q).save(out, quality=82)
        rows.append({"photo_id": photo_id, "plant_id": pid, "machine_id": t.component_id.rsplit("-C", 1)[0],
                     "component_id": t.component_id, "file": f"photos/{photo_id}.jpg", "photo_kind": "component_in_cabinet",
                     "taken_on": "2026-11-14", "quality": q, "rendered": "yes"})
    df = pd.DataFrame(rows)
    for pid, g in df.groupby("plant_id"):
        g.to_csv(SEED / pid / "photos.csv", index=False)
    print(f"rendered {len(df)} in-cabinet photos:", df.quality.value_counts().to_dict())


if __name__ == "__main__":
    main()
