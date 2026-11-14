"""v3 #11: the matching/detection/cost logic must never mention a specific company, part or supplier.

Turns "not overfit to our own fake data" into an enforced fact. Comments and docstrings are
stripped first (tokenize), so explaining an example in a comment is fine; using it in code is not.
Category names are NOT checked (they're the shared taxonomy, legitimately used).
"""
import io
import tokenize
from pathlib import Path

import pandas as pd

from afterlife.io import ROOT, SAMPLE, companies
from afterlife.profiles import PROFILES

LOGIC_FILES = ["match.py", "match_spend.py", "match_claims.py", "detect.py", "cost.py", "evaluate.py"]


def code_only(path: Path) -> str:
    """Source with comments and string literals (incl. docstrings) removed."""
    out = []
    for tok in tokenize.generate_tokens(io.StringIO(path.read_text()).readline):
        if tok.type not in (tokenize.COMMENT, tokenize.STRING):
            out.append(tok.string)
    return " ".join(out)


def strings_in_code(path: Path) -> list[str]:
    """String literals that are NOT docstrings (a docstring is a STRING right after a NEWLINE/INDENT at statement start)."""
    toks = list(tokenize.generate_tokens(io.StringIO(path.read_text()).readline))
    found = []
    for i, tok in enumerate(toks):
        if tok.type == tokenize.STRING:
            prev = next((t for t in reversed(toks[:i]) if t.type not in (tokenize.NL, tokenize.COMMENT)), None)
            is_doc = prev is None or prev.type in (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT)
            if not is_doc:
                found.append(tok.string)
    return found


def forbidden_terms() -> set[str]:
    terms = set()
    for p in PROFILES:
        terms |= {p["company_id"], p["company_name"]}
    folders = [d for _, d in companies()] + [SAMPLE]
    for d in folders:
        for table, cols in [("part_master", ["part_no"]), ("production_spend", ["supplier_id", "po_line_id"]),
                            ("products", ["product_id"])]:
            f = d / f"{table}.csv"
            if f.exists():
                df = pd.read_csv(f, dtype=str, keep_default_na=False)
                for c in cols:
                    if c in df.columns:
                        terms |= set(df[c])
    return {t for t in terms if t and len(t) >= 4}


def test_logic_mentions_no_company_part_or_supplier():
    terms = forbidden_terms()
    hits = []
    for name in LOGIC_FILES:
        path = ROOT / "afterlife" / name
        text = " ".join(strings_in_code(path)) + " " + code_only(path)
        hits += [(name, t) for t in terms if t.lower() in text.lower()]
    assert not hits, f"hardcoded company/part/supplier in logic: {hits[:10]}"
