"""Synthetic data generator (orchestrator). Milestone M1.

Each thread writes its own half:
  generate_spend.py  [SPEND]    products, part_master, bom, builds, production_spend, service_spend
  generate_claims.py [WARRANTY] failure_codes, warranty_claims, truth_spikes (needs bom + builds)
Checklist: docs/research/data-sources.md ("Realism checklist").

Run: python -m afterlife.generate --seed 7
"""
import argparse
import csv
from afterlife.io import GENERATED
from afterlife import generate_spend, generate_claims


def write(tables: dict[str, list[dict]], out_dir=GENERATED) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in tables.items():
        with open(out_dir / f"{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)


def generate(seed: int = 7, out_dir=GENERATED) -> None:
    spend = generate_spend.generate(seed)                 # includes truth_links for spend rows
    claims = generate_claims.generate(seed, spend)         # includes truth_links for claim rows
    truth = spend.pop("truth_links") + claims.pop("truth_links")
    write({**spend, **claims, "truth_links": truth}, out_dir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    generate(ap.parse_args().seed)
