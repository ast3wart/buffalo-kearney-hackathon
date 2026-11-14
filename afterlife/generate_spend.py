"""[SPEND thread · Asher] Products, BOMs, builds, production + service purchase lines."""
from afterlife.taxonomy import CATEGORIES  # noqa: F401


def generate(seed: int, profile: dict) -> dict[str, list[dict]]:
    """Return {products, part_master, bom, builds, production_spend, service_spend, truth_links}.

    Also return info_records and build_supply. (dataset_info, abbreviations and failure_codes are
    written by generate.py from the profile; SAP formatting for extract_format='sap' too.)
    Read knobs from `profile` (afterlife/profiles.py): n_products, n_parts, shared_part_share,
    category_weights, prod_part_no_fill, service_part_no_fill, spare_markup, build window.

    TODO(SPEND), per CP0:
    - n_parts using taxonomy.CATEGORIES minus profile["exclude_categories"], shared_part_share across products;
      part numbers in profile["pn_format"], descriptions in profile["desc_style"] (erp_shorthand / plain_words)
    - builds: monthly 2025-01 .. 2026-09 per product
    - production_spend: supplier wording + supplier PNs, UoM noise (EA vs BX10),
      part_no filled ~85%, a few lines with price_unit=100 (price is per 100)
    - info_records: part_no <-> supplier_pn for production suppliers only (both suppliers of a dual-sourced part)
    - v3 #13 dual sourcing: profile["dual_source_share"] of parts get 2 production suppliers, and the spike
      part (profile["spike"]["category"], a SHARED part) must be one of them
    - v3 #13 build_supply: one row per (product, build_month, part, supplier) with the PO line (lot) consumed
      and its share (shares sum to 1). THE MIX MUST VARY across products and/or months, or 🛠 can't
      attribute the spike to a supplier (e.g. supplier A on products 1+3, B on product 2, 50/50 later)
    - v3 #12 acquired plant (Ironridge): profile["acquired_plant"] share of production lines at that plant,
      part_no blank, own supplier list + supplier PNs, plain-words descriptions, higher price level
    - service_spend: same parts from a distributor at 1.5-5x, different PNs and wording, part_no ~15%
    - truth_links rows for every spend line
    - products.avg_selling_price (v4): per-unit price, so warranty cost can be shown as % of revenue
    - po_line_id: unique and non-empty across BOTH spend tables. For SAP companies (profile["extract_format"]
      == "sap") mint distinct numeric PO numbers per plant/table (e.g. 45xxxxxxxx production, 46xxxxxxxx
      acquired plant, 47xxxxxxxx service), ideally already in canonical form "##########-#####"
      (sap.canonical_po_id); generate.write() raises on collisions
    """
    raise NotImplementedError
