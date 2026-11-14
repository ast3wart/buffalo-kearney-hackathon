"""Supplier agreements for GENERATED companies: one document per production supplier (contract v4 + price schedule).

Ownership (agreed by Asher; Brandon to confirm):
  - warranty_terms() + the warranty section wording   -> 🛠 Brandon's to own and tune (mirrors his sample
    agreements in scripts/make_sample.py: formal / table / amended styles, latest amendment wins)
  - price_schedule() + section "5. Prices"            -> 💲 Asher (contract prices + "spares at series price")
generate_spend.py calls render_agreement() for every production supplier and returns
  supplier_agreements [{doc_file, text}], truth_terms (his answer key), truth_prices (new answer key).
The pipeline never reads the truth files: terms and prices are EXTRACTED from the text
(extract_terms.py 🛠, extract_prices.py 💲).

Why a price schedule: real supply agreements set the contract price and often require spares at the
series (production) price, e.g. DRÄXLMAIER's terms: last series price for 5 years after end of production
(Velocity research, docs/research/velocity.md). So a spare bought at 2x from a distributor is a contract-
compliance question, and paid prices drifting above the contract price is "price leakage".
"""
import random

TERMS_STYLES = ["formal", "table", "amended"]


def warranty_terms(rng: random.Random) -> dict:
    """🛠 Recovery terms for one supplier (distribution mirrors the sample's 9 agreements)."""
    labor = rng.random() < 0.7
    return {"recovery_pct": rng.choice([0.5, 0.6, 0.75, 0.8, 1.0, 1.0]), "labor_covered": labor,
            "labor_rate_cap": rng.choice([75, 85, 90, 95, 100]) if labor else None,
            "recovery_window_months": rng.choice([12, 18, 24, 24]), "filing_deadline_days": rng.choice([30, 45, 60, 90]),
            "style": rng.choice(TERMS_STYLES)}


def _warranty_section(company: str, name: str, sid: str, country: str, t: dict) -> str:
    """🛠 Same wording as scripts/make_sample.py agreement_doc() (formal / table / amended)."""
    pct, labor, cap, window, filing = (t["recovery_pct"], t["labor_covered"], t["labor_rate_cap"],
                                       t["recovery_window_months"], t["filing_deadline_days"])
    cover = (f"parts and dealer labor, labor at the hours actually claimed and capped at USD {cap} per hour"
             if labor else "the parts only; dealer labor is excluded")
    if t["style"] == "table":
        return (f"{company.upper()} · SUPPLIER WARRANTY TERMS\nVendor: {name} (vendor no. {sid}), {country}\n\n"
                f"| Term | Value |\n|---|---|\n| Warranty period | {window} months from end-unit build date |\n"
                f"| Recovery share | {pct:.0%} |\n| Labor reimbursed | {'yes, max $' + str(cap) + '/hr' if labor else 'no'} |\n"
                f"| Claim filing deadline | {filing} days after dealer claim is paid |\n"
                f"| Freight / handling | not recoverable |\n")
    body = (f"# Supplier Quality Agreement\n{company} (\"Buyer\") and {name}, supplier no. {sid} "
            f"(\"Supplier\"), {country}. Effective 2025-01-01.\n\n## 4. Quality\n4.1 Supplier maintains IATF 16949 "
            f"certification and ships with a certificate of conformance per lot.\n\n## 7. Warranty\n"
            f"7.1 Supplier warrants each part for {window} months from the date of manufacture of the end unit "
            f"in which it is installed.\n")
    if t["style"] == "amended":
        return (body + f"7.2 For field failures attributable to Supplier's parts, Supplier reimburses 100% of {cover}.\n"
                f"7.3 Recovery claims are submitted within 90 days after Buyer pays the dealer claim.\n"
                f"7.4 Freight, handling and administrative fees are not recoverable.\n\n"
                f"## Amendment No. 1 (effective 2025-06-01)\nSections 7.2 and 7.3 are replaced as follows. "
                f"Supplier reimburses {pct:.0%} of {cover}. Recovery claims must be submitted within {filing} days "
                f"after Buyer pays the dealer claim; late claims are void. All other terms are unchanged.\n")
    return (body + f"7.2 For field failures attributable to Supplier's parts, Supplier reimburses {pct:.0%} of {cover}.\n"
            f"7.3 Recovery claims are submitted within {filing} days after Buyer pays the dealer claim.\n"
            f"7.4 Freight, handling and administrative fees are not recoverable.\n")


def _price_section(rows: list[dict], spares_at_series: bool, style: str) -> str:
    """💲 Contract price schedule. rows: part_no, supplier_pn, description, price_ea, valid_from, valid_to."""
    lines = ["", "## 5. Prices" if style != "table" else "PRICE SCHEDULE (per piece, USD)", ""]
    if style != "table":
        lines.append("5.1 Prices per piece in USD, firm for the validity period below, DDP Buyer's plant.")
        lines.append("5.2 Price schedule:")
        lines.append("")
    lines += ["| Buyer part no. | Supplier part no. | Description | Price per piece (USD) | Valid from | Valid to |",
              "|---|---|---|---|---|---|"]
    lines += [f"| {r['part_no']} | {r['supplier_pn']} | {r['description']} | {r['price_ea']:.4f} | {r['valid_from']} | {r['valid_to']} |"
              for r in rows]
    lines.append("")
    if spares_at_series:
        lines.append("5.3 Spare parts. Supplier supplies the parts above as spare parts at the current series price "
                     "during the term of this agreement and at the last series price for five years after end of "
                     "series production; special spare-parts packaging may be charged at cost.")
    else:
        lines.append("5.3 Spare parts are priced separately by quotation.")
    return "\n".join(lines) + "\n"


def doc_file_name(supplier_name: str) -> str:
    return "sqa_" + "".join(ch if ch.isalnum() else "-" for ch in supplier_name.lower()).strip("-").replace("--", "-") + ".md"


def render_agreement(company: str, supplier: dict, terms: dict, price_rows: list[dict], spares_at_series: bool) -> str:
    text = _warranty_section(company, supplier["supplier_name"], supplier["supplier_id"], supplier["country"], terms)
    return text + _price_section(price_rows, spares_at_series, terms["style"])
