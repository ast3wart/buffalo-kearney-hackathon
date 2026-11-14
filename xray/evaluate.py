"""Accuracy vs a planted answer key (kept from Afterlife). E.g. what vision + matching identified for each
machine/component vs the test factory's truth.

precision = correct predictions / predictions made
recall    = correct predictions / records in the answer key
"""
import pandas as pd


def score(pred: pd.DataFrame, truth: pd.DataFrame, key: list[str], value: str,
          by: list[str] | None = None) -> pd.DataFrame:
    """Compare pred[value] with truth[value], joined on `key`. by=["field"] -> one row per group."""
    t = truth[key + [value]].astype(str).rename(columns={value: "_true"})
    p = pred.copy()
    p[key + [value]] = p[key + [value]].astype(str)
    m = p.merge(t, on=key, how="left")
    m["correct"] = m[value] == m["_true"]
    groups = by or []
    if groups:
        out = m.groupby(groups).agg(predicted=("correct", "size"), correct=("correct", "sum")).reset_index()
        totals = truth.groupby(groups).size().rename("records").reset_index()
        out = out.merge(totals, on=groups)
    else:
        out = pd.DataFrame([{"predicted": len(m), "correct": int(m.correct.sum()), "records": len(truth)}])
    out["precision"] = (out.correct / out.predicted).round(3)
    out["recall"] = (out.correct / out.records).round(3)
    return out[groups + ["records", "predicted", "correct", "precision", "recall"]]
