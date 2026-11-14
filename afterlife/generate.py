"""Synthetic data generator (orchestrator). Milestone M1.

Each thread writes its own half:
  generate_spend.py  [SPEND]    products, part_master, bom, builds, production_spend, service_spend
  generate_claims.py [WARRANTY] failure_codes, warranty_claims, truth_spikes (needs bom + builds)
Checklist: docs/research/data-sources.md ("Realism checklist").

Writes one folder per company: data/generated/<company_id>/ (profiles in afterlife/profiles.py).

Run: python -m afterlife.generate --seed 7
"""
import argparse
import csv
from afterlife.io import GENERATED
from afterlife import generate_spend, generate_claims
from afterlife.profiles import PROFILES, dataset_info, abbreviations_rows, failure_code_rows
from afterlife.adapters import sap
import pandas as pd


def write(tables: dict[str, list[dict]], out_dir=GENERATED, extract_format: str = "contract") -> None:
    """Write every table as CSV. extract_format='sap' writes the SAP-mappable tables with raw SAP
    field names and quirks (adapters/sap.py), as a real client extract would arrive."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in tables.items():
        if extract_format == "sap" and name in sap.MAPS and rows:
            sap.from_contract(name, pd.DataFrame(rows)).to_csv(out_dir / f"{name}.csv", index=False)
            continue
        with open(out_dir / f"{name}.csv", "w", newline="") as f:
            fields = list(rows[0].keys()) if rows else []
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)


def generate(seed: int = 7, out_dir=GENERATED) -> None:
    for i, profile in enumerate(PROFILES):
        s = seed + i  # different but reproducible per company
        spend = generate_spend.generate(s, profile)               # includes truth_links for spend rows
        claims = generate_claims.generate(s, spend, profile)      # includes truth_links for claim rows
        truth = spend.pop("truth_links") + claims.pop("truth_links")
        info = [{"key": k, "value": v} for k, v in dataset_info(profile).items()]
        vocab = {"abbreviations": abbreviations_rows(profile), "failure_codes": failure_code_rows(profile)}
        write({**spend, **claims, **vocab, "truth_links": truth, "dataset_info": info},
              out_dir / profile["company_id"], profile["extract_format"])
        print(f"wrote {profile['company_id']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    generate(ap.parse_args().seed)
