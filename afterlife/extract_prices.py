"""[SPEND thread · Asher] supplier agreement documents -> contract prices (the price-schedule section).

Contract prices are NOT trusted ERP fields here: they live in the supply agreement's price schedule (and its
"spare parts at series price" clause), so we extract them from supplier_agreements/ (io.load_documents),
the same way extract_terms.py (🛠) extracts the warranty terms.
  1. regex pass for the table-style schedule (method "regex"); the supplier number is read from the text,
     never from the file name
  2. TODO (Tier 2): Claude for prose schedules, quoting the clause each value came from
Output: PRICE_COLUMNS (table `contract_prices` in results.duckdb). Scored against truth_prices (tests).
"""
import json
import os
import re

import pandas as pd

PRICE_COLUMNS = ["doc_file", "supplier_id", "part_no", "supplier_pn", "contract_price_ea", "valid_from", "valid_to",
                 "spares_at_series_price", "method", "confidence", "evidence", "run_id"]

SUPPLIER_NO = re.compile(r"(?:supplier|vendor) no\.\s*([A-Za-z0-9-]+)", re.I)
ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([0-9]+(?:\.[0-9]+)?)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*$")
SERIES_CLAUSE = re.compile(r"spare parts at the (?:current|last) series price", re.I)


def extract_prices(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    docs = tables.get("supplier_agreements")
    run_id = os.environ.get("AFTERLIFE_RUN_ID", "")
    rows = []
    if docs is None or docs.empty:
        return pd.DataFrame(columns=PRICE_COLUMNS)
    for doc_file, text in zip(docs.doc_file, docs.text):
        m = SUPPLIER_NO.search(text)
        sid = m.group(1) if m else ""
        in_schedule = False
        spares = bool(SERIES_CLAUSE.search(text))
        for line in text.splitlines():
            if re.search(r"price schedule|^##\s*5\.\s*prices", line, re.I):
                in_schedule = True
                continue
            r = ROW.match(line.strip()) if in_schedule else None
            if not r:
                continue
            part, spn, desc, price, vf, vt = r.groups()
            rows.append({"doc_file": doc_file, "supplier_id": sid, "part_no": part, "supplier_pn": spn,
                         "contract_price_ea": float(price), "valid_from": vf, "valid_to": vt,
                         "spares_at_series_price": spares, "method": "regex", "confidence": 0.98 if sid else 0.6,
                         "evidence": json.dumps({"row": line.strip()[:200], "spares_clause": spares}), "run_id": run_id})
    return pd.DataFrame(rows, columns=PRICE_COLUMNS)
