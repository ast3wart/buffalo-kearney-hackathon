"""[WARRANTY thread · Brandon] Failure codes, warranty claims, planted spike."""
from afterlife.taxonomy import FAILURE_CODES  # noqa: F401


def generate(seed: int, spend: dict[str, list[dict]], profile: dict) -> dict[str, list[dict]]:
    """Return {failure_codes, warranty_claims, truth_spikes, truth_links}. Uses spend['bom'], spend['builds'].

    failure_codes = this company's subset (profile["failure_codes"], written by generate.py); only use those.
    Claim text uses this company's shorthand (profile["abbreviations"]) and typo_rate.

    TODO(WARRANTY), per CP0:
    - claim volume = profile["warranty_pct_revenue"] of revenue, revenue = sum(units_built x products.net_price)
      (21a; calibrated to SEC filers, see profiles.py)
    - failure dates spread over months-in-service with a hazard curve (more early-life failures),
      cut off at profile data_as_of (profiles.COMMON) so recent builds are genuinely immature
    - failure-system mix shaped like NHTSA data, not uniform
    - causal_part_no blank ~60%, wrong ~10%; messy dealer text (hyd, cyl, brg, repl)
    - spend["_spike_plan"] = {part_no, supplier_id, start_build_month, from_po_line_id, multiplier} (or None):
      the spend generator already picked the dual-sourced shared part and the lot. Copy it into truth_spikes.
    - plant the spike from profile["spike"]: the dual-sourced shared part, ONE supplier's lots only, from a
      specific PO line onward (spend["build_supply"] says which lot each product/month used). Claim rate for a
      product/month = base x (1 + (multiplier-1) x share of the spiking supplier's affected lots).
      truth_spikes gets from_po_line_id. profile["spike"] is None for the control company -> no spike rows.
    - causal_part_no: blank profile["causal_blank_share"], wrong profile["causal_wrong_share"]
    - truth_links rows for every claim
    """
    raise NotImplementedError
