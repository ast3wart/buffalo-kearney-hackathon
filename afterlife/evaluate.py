"""Accuracy vs planted truth. Owner: shared (each thread scores its own source_table). Milestone M3.

Run: python -m afterlife.evaluate        (every company; spend links, plus claim links once match_claims exists)

precision = correct links / links made         (how often a link is right)
recall    = correct links / records that should be linked   (how much we linked correctly)
Reported per company x source_table, and per method.
"""
import pandas as pd

KEY = ["source_table", "source_id"]


def score(links: pd.DataFrame, truth: pd.DataFrame, by: list[str] | None = None) -> pd.DataFrame:
    """Precision/recall of `links` against `truth` (both with source_table, source_id, part_no).
    by=None -> one row per source_table; by=["method"] -> per source_table x method (recall there is
    'share of all records this method linked correctly')."""
    truth = truth[truth.source_table.isin(links.source_table.unique()) if len(links) else []]
    t = truth[KEY + ["part_no"]].astype(str).rename(columns={"part_no": "true_part"})
    lk = links.copy()
    lk[KEY + ["part_no"]] = lk[KEY + ["part_no"]].astype(str)
    m = lk.merge(t, on=KEY, how="left")
    m["correct"] = m.part_no == m.true_part
    groups = ["source_table"] + (by or [])
    out = m.groupby(groups).agg(linked=("correct", "size"), correct=("correct", "sum")).reset_index()
    totals = t.groupby("source_table").size().rename("records")
    out = out.merge(totals, on="source_table")
    out["precision"] = (out.correct / out.linked).round(3)
    out["recall"] = (out.correct / out.records).round(3)
    return out[groups + ["records", "linked", "correct", "precision", "recall"]]


def evaluate_company(tables: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    from afterlife.match_spend import link_spend
    parts = [link_spend(tables)]
    try:
        from afterlife.match_claims import link_claims
        if "warranty_claims" in tables and len(tables["warranty_claims"]):
            parts.append(link_claims(tables))
    except NotImplementedError:
        pass
    links = pd.concat(parts, ignore_index=True)
    return score(links, tables["truth_links"]), score(links, tables["truth_links"], by=["method"])


if __name__ == "__main__":
    from afterlife.io import companies, load
    pd.set_option("display.width", 140)
    for cid, folder in companies(require_claims=False):
        summary, by_method = evaluate_company(load(folder))
        print(f"\n== {cid}")
        print(summary.to_string(index=False))
        print(by_method.to_string(index=False))
