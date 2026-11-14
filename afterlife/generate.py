"""Synthetic data generator. Owner: Role A. Milestone M1.

Writes every input + truth table in docs/build/data-contract.md to data/generated/.
Checklist: docs/research/data-sources.md ("Realism checklist").

Run: python -m afterlife.generate --seed 7
"""
import argparse
from afterlife.io import GENERATED


def generate(seed: int = 7, out_dir=GENERATED) -> None:
    # TODO(A): products + part_master (~300 parts, ~40% shared)
    # TODO(A): bom, builds (12 build months)
    # TODO(A): production_spend (ERP shorthand vs supplier wording, UoM noise)
    # TODO(A): service_spend (same parts at 1.5–5x price, different supplier PNs)
    # TODO(A): failure_codes + warranty_claims (blank/wrong causal_part_no, messy text)
    # TODO(A): plant ONE spike -> truth_spikes.csv ; all true links -> truth_links.csv
    raise NotImplementedError


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    generate(ap.parse_args().seed)
