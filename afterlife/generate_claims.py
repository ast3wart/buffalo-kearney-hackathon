"""[WARRANTY thread · Brandon] Failure codes, warranty claims, planted spike."""
from afterlife.taxonomy import FAILURE_CODES  # noqa: F401


def generate(seed: int, spend: dict[str, list[dict]], profile: dict) -> dict[str, list[dict]]:
    """Return {failure_codes, warranty_claims, truth_spikes, truth_links, supplier_agreements, truth_terms}.
    Uses spend['bom'], spend['builds'], spend['build_supply'], spend['production_spend'] (suppliers).

    failure_codes = this company's subset (profile["failure_codes"], written by generate.py); only use those.
    Claim text uses this company's shorthand (profile["abbreviations"]) and typo_rate.

    TODO(WARRANTY), per CP0:
    - claim volume = profile["warranty_pct_revenue"] of revenue, revenue = sum(units_built x products.avg_selling_price)
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
    v4 (accounting fields, docs/build/data-contract.md "v4"), scripts/make_sample.py shows the pattern:
    - claim_date = failure_date + reporting lag (days); drop claims whose claim_date > data_as_of
    - paid_date = claim_date + days to pay; blank if after data_as_of. other_cost = handling/freight/sublet
    - claim_type: mostly warranty, a few goodwill / campaign (never recovered)
    - recovery_status / recovered_usd only on paid warranty claims, valued with the supplier's terms (truth_terms)
      and only inside the supplier's recovery window
    - supplier_agreements = [{doc_file, text}] for every production supplier, in this company's style
      (some superseded by an amendment, some as a terms table); truth_terms = the terms each doc states
    """
    raise NotImplementedError
