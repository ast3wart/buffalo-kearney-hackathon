"""Supplier brief. Owner: Role B. Milestone M6.

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


def make_brief(supplier_id: str, alerts, markups, tables) -> str:
    raise NotImplementedError  # TODO(B)
