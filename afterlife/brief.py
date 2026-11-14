"""Supplier brief. Milestone M6. Shared file, split by section:
  Ask 1 (warranty recovery)  -> [WARRANTY thread] warranty_section()
  Ask 2 (price harmonization) -> [SPEND thread] pricing_section()


Fill TEMPLATE from numbers first (works with no API key); optionally
polish with an LLM (ANTHROPIC_API_KEY in .env). Never let the LLM invent numbers.
"""

TEMPLATE = """# Supplier brief: {supplier_name} ({supplier_id})

## Ask 1: Warranty recovery
{part_no} claims rose {ratio:.1f}x across {products_affected} products for builds from {start_build_month}.
Estimated exposure: **${exposure_usd:,.0f}**.

## Ask 2: Spare-part price harmonization
{markup_lines}

## Talking points
{talking_points}
"""


def warranty_section(supplier_id: str, alerts, tables) -> dict:
    raise NotImplementedError  # TODO(WARRANTY)


def pricing_section(supplier_id: str, markups, tables) -> dict:
    raise NotImplementedError  # TODO(SPEND)


def make_brief(supplier_id: str, alerts, markups, tables) -> str:
    """Template first (no API key needed); optional Claude polish streams via POST /brief."""
    raise NotImplementedError  # TODO(shared)
