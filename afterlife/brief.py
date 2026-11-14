"""Supplier brief. Milestone M6. Shared file, split by section:
  Ask 1 (warranty recovery review) -> [WARRANTY thread] warranty_section()
  Ask 2 (price harmonization) -> [SPEND thread] pricing_section()


Fill TEMPLATE from numbers first (works with no API key); optionally
polish with an LLM (ANTHROPIC_API_KEY in .env). Never let the LLM invent numbers.

Wording rule (after Velocity review, Sat Nov 14): claims are LINKED to a candidate part/supplier;
never say the supplier "caused" them or "owes" money. $ are recovery OPPORTUNITIES (scenario range).
"""

TEMPLATE = """# Supplier brief: {supplier_name} ({supplier_id})

## Ask 1: Warranty recovery review
{n_claims} warranty claims across {products_affected} products (builds from {start_build_month}) are **linked to** {part_no},
supplied by you. The claim rate at {mis_window} months in service rose {ratio:.1f}x vs. earlier builds.
Linked claim cost: **${exposure_usd:,.0f}**. Match confidence: {confidence_summary}.
**Request:** returned-part analysis and a joint engineering review, then cost allocation per our supply agreement.
Recovery opportunity (scenario, 25–50% capture): ${opportunity_low:,.0f}–${opportunity_high:,.0f}.

_Status: claims linked to a candidate part/supplier. Exposure pending engineering and contract review._

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
