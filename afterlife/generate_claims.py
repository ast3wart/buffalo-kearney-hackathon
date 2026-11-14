"""[WARRANTY thread · Brandon] Failure codes, warranty claims, planted spike."""
from afterlife.taxonomy import FAILURE_CODES  # noqa: F401


def generate(seed: int, spend: dict[str, list[dict]], profile: dict) -> dict[str, list[dict]]:
    """Return {failure_codes, warranty_claims, truth_spikes, truth_links}. Uses spend['bom'], spend['builds'].

    Use taxonomy.FAILURE_CODES as failure_codes.

    TODO(WARRANTY), per CP0:
    - claim volume = profile["warranty_pct_revenue"] (calibrated to SEC filers, see profiles.py)
    - failure dates spread over months-in-service with a hazard curve (more early-life failures),
      cut off at profile data_as_of (profiles.COMMON) so recent builds are genuinely immature
    - failure-system mix shaped like NHTSA data, not uniform
    - causal_part_no blank ~60%, wrong ~10%; messy dealer text (hyd, cyl, brg, repl)
    - plant the spike from profile["spike"] (pick a SHARED part in that category, one supplier);
      profile["spike"] is None for the control company -> truth_spikes is empty, alerts should be too
    - truth_links rows for every claim
    """
    raise NotImplementedError
