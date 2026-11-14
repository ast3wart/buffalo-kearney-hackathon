"""[SPEND thread · Asher] Products, BOMs, builds, production + service purchase lines."""


def generate(seed: int) -> dict[str, list[dict]]:
    """Return {products, part_master, bom, builds, production_spend, service_spend, truth_links}.

    TODO(SPEND):
    - ~300 parts, ~40% shared across 3 products; ERP-shorthand descriptions
    - builds: 12 build months per product
    - production_spend: supplier wording + supplier PNs, UoM noise (EA vs BX10)
    - service_spend: same parts from a distributor at 1.5-5x, different PNs and wording
    - truth_links rows for every spend line
    """
    raise NotImplementedError
