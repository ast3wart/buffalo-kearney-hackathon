"""[SPEND thread · Asher] production_spend + service_spend lines -> part_no.

Steps, cheapest and most certain first (taxonomy.LINK_METHODS). Each line takes the first that applies:
  1. exact_pn     part_no on the line exists in part_master                          (SAP MATNR)
  2. info_record  (supplier_id, supplier_pn) is in info_records                      (SAP EINA/IDNLF)
  3. spec_code    the line shares spec codes with a part (6204, M20X1.5, 35X47X7, 40MM) and that part
                  also wins on text
  4. fuzzy_text   best text match against every part description, after both sides are normalized with
                  this company's abbreviations (abbreviations.csv)
The hard cases are the lines with no part number and no known supplier part number: service "text
items" bought from distributors, and acquired-plant lines on a legacy system.

Every link carries `evidence` (JSON of the signals), `source_system`, and `run_id` ($AFTERLIFE_RUN_ID).
Also provides price_per_each(): price_unit + unit-of-measure pack size -> comparable price per EA.
No company, part or supplier is named in this file (tests/test_no_literals.py).
"""
import json
import os
import re

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

from afterlife.match import abbreviation_map, normalize

SPEND_TABLES = ("production_spend", "service_spend")
CONF = {"exact_pn": 0.99, "info_record": 0.97}
MIN_SCORE = 55.0            # below this best text score a line is normally left unlinked ...
WEAK_SCORE, WEAK_MARGIN = 40.0, 15.0   # ... unless it's a weak but clear winner: then linked at LOW_CONF
LOW_CONF = 0.4             # for human review; recovery only uses links with confidence >= 0.8
UNITS = r"MM|IN|V|W|A|HP|CC|AH|TON|UF|C|BAR|MIC|T"


def canon(text: str, abbreviations: dict[str, str]) -> str:
    """normalize() plus unit/dimension clean-up so '20 mm' == '20MM' and '35 x 47 x 7' == '35X47X7'."""
    s = normalize(text, abbreviations)
    s = re.sub(r"(\d)\s*X\s*(?=\d)", r"\1X", s)                     # 35 X 47 -> 35X47
    s = re.sub(rf"(\d)\s+({UNITS})\b", r"\1\2", s)                   # 20 MM -> 20MM
    return s


def spec_tokens(s: str) -> set[str]:
    """Tokens with a digit (spec codes, sizes), also split on '-' so 6204-2RS also yields 6204 and 2RS."""
    out = set()
    for tok in s.split():
        if any(ch.isdigit() for ch in tok):
            out.add(tok)
            out.update(p for p in tok.split("-") if any(ch.isdigit() for ch in p))
    return out


def numbers(s: str) -> set[str]:
    """Every number in the text, unit-free: '63X300' -> {63, 300}, 'M2' -> {2}, '3/8' -> {3/8}, '24T' -> {24}.
    Robust to word order and to how dimensions are written ('63 MM BORE X 300 MM' == '63X300')."""
    return {n.lstrip("0") or "0" for n in re.findall(r"\d+(?:[./]\d+)?", s)}


def pack_size(uom: str) -> int:
    """'EA' -> 1, 'BX10' -> 10, 'BX100' -> 100 (any trailing number is the pack size)."""
    m = re.search(r"(\d+)$", str(uom))
    return int(m.group(1)) if m else 1


def price_per_each(df: pd.DataFrame) -> pd.Series:
    """unit_price is per `price_unit` of `uom`; return the price of ONE piece."""
    pu = pd.to_numeric(df.price_unit, errors="coerce").fillna(1).replace(0, 1)
    return pd.to_numeric(df.unit_price, errors="coerce") / pu / df.uom.map(pack_size)


def _source_system(table: str, plant) -> str:
    return "SERVICE-PORTAL" if table == "service_spend" else f"ERP-{plant}"


def link_spend(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    abbr = abbreviation_map(tables)
    pm = tables["part_master"]
    parts = pm.part_no.astype(str).tolist()
    part_set = set(parts)
    part_canon = [canon(d, abbr) for d in pm.description]
    part_specs = [spec_tokens(c) for c in part_canon]
    part_nums = [numbers(c) for c in part_canon]
    ir = tables.get("info_records")
    crosswalk = {} if ir is None else {(str(s), str(p)): str(n) for s, p, n in zip(ir.supplier_id, ir.supplier_pn, ir.part_no)}
    run_id = os.environ.get("AFTERLIFE_RUN_ID", "")
    text_cache: dict[str, tuple] = {}

    def text_match(desc: str):
        """-> (part_no, method, confidence, evidence) for a free-text description (cached per text)."""
        c = canon(desc, abbr)
        if c in text_cache:
            return text_cache[c]
        specs, nums = spec_tokens(c), numbers(c)
        # two text scores: token_set rewards overlap, token_sort penalizes extra words (variants)
        s_set = process.cdist([c], part_canon, scorer=fuzz.token_set_ratio)[0]
        s_sort = process.cdist([c], part_canon, scorer=fuzz.token_sort_ratio)[0]
        # spec similarity = overlap of the NUMBERS (sizes, codes), which survives reworded dimensions
        spec = np.array([len(nums & pn) / len(nums | pn) if (nums or pn) else 0.0 for pn in part_nums])
        score = 0.40 * s_set + 0.30 * s_sort + 30.0 * spec
        order = np.argsort(-score)
        best, second = order[0], order[1] if len(order) > 1 else order[0]
        margin = float(score[best] - score[second])
        if score[best] < MIN_SCORE and not (score[best] >= WEAK_SCORE and margin >= WEAK_MARGIN):
            out = (None, "fuzzy_text", 0.0, {"best_score": round(float(score[best]), 1)})
        elif score[best] < MIN_SCORE:   # weak but clear winner -> review queue, never used for recovery
            out = (parts[best], "fuzzy_text", LOW_CONF,
                   {"weak_match": True, "score": round(float(score[best]), 1), "margin": round(margin, 1),
                    "shared_numbers": sorted(nums & part_nums[best]), "runner_up": parts[second]})
        else:
            method = "spec_code" if spec[best] >= 0.5 and nums else "fuzzy_text"
            conf = float(np.clip(0.55 + margin / 40 + (score[best] - MIN_SCORE) / 200, 0.3, 0.95))
            out = (parts[best], method, round(conf, 3),
                   {"text_set": round(float(s_set[best]), 1), "text_sort": round(float(s_sort[best]), 1),
                    "spec_overlap": round(float(spec[best]), 2), "shared_numbers": sorted(nums & part_nums[best]),
                    "shared_specs": sorted(specs & part_specs[best]),
                    "margin": round(margin, 1), "runner_up": parts[second]})
        text_cache[c] = out
        return out

    rows = []
    for table in SPEND_TABLES:
        df = tables.get(table)
        if df is None:
            continue
        for r in df.itertuples(index=False):
            pn = None if pd.isna(r.part_no) else str(r.part_no)
            key = (str(r.supplier_id), str(r.supplier_pn))
            if pn and pn in part_set:
                part, method, conf, ev = pn, "exact_pn", CONF["exact_pn"], {"part_no_on_line": True}
            elif key in crosswalk and crosswalk[key] in part_set:
                part, method, conf, ev = crosswalk[key], "info_record", CONF["info_record"], {"supplier_pn": key[1]}
            else:
                part, method, conf, ev = text_match(r.description)
            if part is None:
                continue
            rows.append({"source_table": table, "source_id": str(r.po_line_id), "part_no": part, "method": method,
                         "confidence": conf, "source_system": _source_system(table, r.plant),
                         "evidence": json.dumps(ev), "run_id": run_id})
    from afterlife.taxonomy import LINK_COLUMNS
    return pd.DataFrame(rows, columns=LINK_COLUMNS)
