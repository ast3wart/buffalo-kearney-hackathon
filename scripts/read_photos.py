"""Read every photo in the demo with Claude vision (cached by image hash).   python scripts/read_photos.py

Needs ANTHROPIC_API_KEY in .env for photos not yet cached. Prints what was read vs. the answer key.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from xray.extract import read_photo  # noqa: E402

SEED = ROOT / "data/seed/demo"


def main():
    truth = pd.read_csv(ROOT / "data/truth/demo/components.csv", dtype=str).fillna("").set_index("component_id")
    rows = []
    for manifest in sorted(SEED.glob("*/photos.csv")):
        photos = pd.read_csv(manifest, dtype=str).fillna("")
        for p in photos.itertuples():
            r = read_photo(manifest.parent / p.file)
            expected = truth.loc[p.component_id, "part_no"] if p.component_id in truth.index else ""
            ok = r["part_no"].replace(" ", "").upper() == expected.replace(" ", "").upper()
            rows.append({"photo": p.photo_id, "quality": p.quality, "read": r["part_no"], "expected": expected,
                         "exact": ok, "conf": r["confidence"], "unclear": ",".join(r["unclear"]), "cached": r["cached"]})
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    print(f"\nexact part-number reads: {df.exact.sum()}/{len(df)}")


if __name__ == "__main__":
    main()
