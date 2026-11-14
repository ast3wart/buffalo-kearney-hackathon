"""[WARRANTY thread · Brandon] supplier agreement documents -> structured recovery terms (v4).

Recovery terms are NOT ERP fields: in SAP they sit in the supplier quality agreement or the purchasing
contract's long text, so we extract them from the documents in supplier_agreements/ (io.load_documents).
1. regex pass for the easy, table-style documents (method "regex")
2. Claude for prose (AFTERLIFE_LLM_MODEL), structured output: one row per document. The model must quote the
   clause each value came from (evidence), and the LATEST amendment wins over the original clause
3. low confidence or missing fields -> left blank for human review (method "human" once confirmed)
No API key -> regex only. Scored against truth_terms by evaluate.py (field-level accuracy).
Output columns: TERMS_COLUMNS (table `supplier_terms` in results.duckdb).
"""
import pandas as pd

TERMS_COLUMNS = ["doc_file", "supplier_id", "recovery_pct", "labor_covered", "labor_rate_cap",
                 "recovery_window_months", "filing_deadline_days", "method", "confidence", "evidence", "run_id"]


def extract_terms(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    raise NotImplementedError  # TODO(WARRANTY)
