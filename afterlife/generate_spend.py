"""[SPEND thread · Asher] Products, BOMs, builds, production + service purchase lines."""
from afterlife.taxonomy import CATEGORIES  # noqa: F401


def generate(seed: int, profile: dict) -> dict[str, list[dict]]:
    """Return {products, part_master, bom, builds, production_spend, service_spend, truth_links}.

    Also return info_records. (dataset_info is written by generate.py.)
    Read knobs from `profile` (afterlife/profiles.py): n_products, n_parts, shared_part_share,
    category_weights, prod_part_no_fill, service_part_no_fill, spare_markup, build window.

    TODO(SPEND), per CP0:
    - ~300 parts using ONLY taxonomy.CATEGORIES, ~40% shared across 3 products; ERP-shorthand descriptions
    - builds: monthly 2025-01 .. 2026-09 per product
    - production_spend: supplier wording + supplier PNs, UoM noise (EA vs BX10),
      part_no filled ~85%, a few lines with price_unit=100 (price is per 100)
    - info_records: part_no <-> supplier_pn for production suppliers only
    - service_spend: same parts from a distributor at 1.5-5x, different PNs and wording, part_no ~15%
    - truth_links rows for every spend line
    """
    raise NotImplementedError
