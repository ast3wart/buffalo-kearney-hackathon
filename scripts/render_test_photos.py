"""Render realistic component-label test images (RENDERED, not real photos; labeled as such).

    python scripts/render_test_photos.py      # -> data/seed/demo/<plant>/photos/*.jpg + photos.csv

Each image shows the real catalog number of a component in the demo registry, with the wear a phone photo of a
cabinet label has: tilt, blur, sensor noise, glare, scuffed characters. Claude's vision then reads them for real
(xray/extract.py), so the accuracy number covers genuine image reading. Real photos taken on site replace them.
"""
import random
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "data/seed/demo"
R = random.Random(11)
FONTS = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
         "/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf"]
HOW_MANY = 12


def font(size, bold=False):
    for f in (FONTS if bold else FONTS[1:]):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def label(kb, serial, year, quality):
    W, H = 1000, 560
    bg = R.choice([(236, 236, 230), (212, 214, 216), (245, 242, 225)])
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([12, 12, W - 12, H - 12], outline=(40, 40, 40), width=5)
    d.text((40, 36), kb.manufacturer.upper(), fill=(25, 25, 25), font=font(54, True))
    d.text((40, 110), kb.description[:44], fill=(40, 40, 40), font=font(30))
    d.line([40, 160, W - 40, 160], fill=(60, 60, 60), width=3)
    d.text((40, 190), "CAT NO.", fill=(60, 60, 60), font=font(26))
    d.text((40, 222), kb.part_no, fill=(10, 10, 10), font=font(70, True))
    d.text((40, 330), f"SER {R.choice('ABCDEF')}   FRN {R.randint(1, 30)}.{R.randint(0, 9):03d}", fill=(40, 40, 40), font=font(32))
    d.text((40, 382), f"S/N {serial}", fill=(40, 40, 40), font=font(32))
    d.text((40, 434), f"MFG DATE {year}-{R.randint(1, 12):02d}", fill=(40, 40, 40), font=font(32))
    d.text((W - 300, 434), R.choice(["24VDC  1.2A", "480VAC 3PH", "120/240VAC", "380-480V 50/60Hz"]), fill=(40, 40, 40), font=font(28))
    if quality in ("worn", "cut_off"):  # scuffs across the catalog number
        for _ in range(R.randint(4, 9)):
            x, y = R.randint(40, 700), R.randint(225, 290)
            d.line([x, y, x + R.randint(20, 90), y + R.randint(-8, 8)], fill=bg, width=R.randint(3, 7))
    # photo realism: background, tilt, blur, noise, glare
    canvas = Image.new("RGB", (W + 240, H + 240), R.choice([(70, 72, 76), (110, 112, 108), (50, 55, 60)]))
    canvas.paste(img, (120, 120))
    canvas = canvas.rotate(R.uniform(-9, 9) if quality != "angled" else R.uniform(14, 20), expand=False, fillcolor=(60, 60, 60))
    if quality == "cut_off":
        canvas = canvas.crop((0, 0, int(canvas.width * 0.62), canvas.height))
    canvas = canvas.filter(ImageFilter.GaussianBlur(R.uniform(0.6, 1.2) if quality != "blurry" else R.uniform(2.6, 3.4)))
    px = canvas.load()
    for _ in range(canvas.width * canvas.height // 25):
        x, y = R.randrange(canvas.width), R.randrange(canvas.height)
        r, g, b = px[x, y]
        n = R.randint(-22, 22)
        px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)))
    if quality == "glare" or R.random() < 0.3:
        glare = Image.new("L", canvas.size, 0)
        gx, gy = R.randint(200, canvas.width - 200), R.randint(150, canvas.height - 150)
        ImageDraw.Draw(glare).ellipse([gx - 160, gy - 90, gx + 160, gy + 90], fill=170 if quality == "glare" else 90)
        canvas = Image.composite(Image.new("RGB", canvas.size, (255, 255, 250)), canvas, glare.filter(ImageFilter.GaussianBlur(45)))
    return canvas


def main():
    kb = pd.read_csv(ROOT / "data/reference/kb.csv", dtype=str).fillna("").set_index("kb_id")
    truth = pd.read_csv(ROOT / "data/truth/demo/components.csv", dtype=str).fillna("")
    years = pd.concat(pd.read_csv(f, dtype=str) for f in SEED.glob("*/readings.csv")).set_index("component_id").date_code
    spof = pd.read_csv(ROOT / "data/truth/demo/spof.csv", dtype=str)
    known = truth[truth.kb_id != ""]
    picks = list(spof.component_id)  # both line-stopping parts first
    rest = known[~known.component_id.isin(picks)]
    for status in ("discontinued", "active", "end_of_life"):  # spread across lifecycle states and plants
        picks += rest[rest.lifecycle_status == status].groupby(rest.component_id.str[:2]).head(1).component_id.tolist()
    picks = list(dict.fromkeys(picks))[:HOW_MANY]
    qualities = ["ok", "ok", "ok", "ok", "ok", "glare", "angled", "blurry", "worn", "cut_off", "ok", "ok"]
    rows = []
    for i, cid in enumerate(picks):
        pid = cid[:2]
        k = kb.loc[truth.set_index("component_id").loc[cid, "kb_id"]]
        q = qualities[i % len(qualities)] if i >= 2 else "ok"  # keep the two demo-critical labels clean
        photo_id = f"{pid}-IMG{i + 1:04d}"
        out = SEED / pid / "photos" / f"{photo_id}.jpg"
        out.parent.mkdir(parents=True, exist_ok=True)
        label(k, R.randint(1000000, 9999999), int(years[cid]), q).save(out, quality=88)  # label date = install year in the data
        rows.append({"photo_id": photo_id, "plant_id": pid, "machine_id": cid.rsplit("-C", 1)[0], "component_id": cid,
                     "file": f"photos/{photo_id}.jpg", "photo_kind": "component_label", "taken_on": "2026-11-14",
                     "quality": q if q != "angled" else "ok", "rendered": "yes"})
    df = pd.DataFrame(rows)
    for pid in sorted({r.split("-")[0] for r in df.photo_id}):
        df[df.plant_id == pid].to_csv(SEED / pid / "photos.csv", index=False)
    print(f"rendered {len(df)} labels:", df.groupby("plant_id").size().to_dict(), "qualities:", df.quality.value_counts().to_dict())


if __name__ == "__main__":
    main()
