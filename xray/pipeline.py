"""Readings + storeroom text -> matched to the knowledge base -> component, evidence, spare_match tables.

No manufacturer or part names here: abbreviations come from data/reference/abbreviations.csv.
"""
import json
import re

import pandas as pd

from xray.matching import Matcher

REVIEW_BELOW = 0.8  # registry-format §9


def kb_text(kb: pd.DataFrame) -> list[str]:
    """What we match against: part number + every alias (descriptions only help messy storeroom text)."""
    return [f"{r.part_no} {str(r.aliases).replace(';', ' ')}" for r in kb.itertuples()]


def kb_text_long(kb: pd.DataFrame) -> list[str]:
    return [f"{r.part_no} {str(r.aliases).replace(';', ' ')} {r.family} {r.description}" for r in kb.itertuples()]


def compact(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(text).upper())


class ExactIndex:
    """Exact hit on a KB part number or a known alias (aliases grow with every scan: the flywheel).
    Returns a KB row index only when exactly one KB entry is hit; ambiguous or worn reads fall through to fuzzy matching."""

    def __init__(self, kb: pd.DataFrame, min_len: int = 6):
        self.keys = []
        for i, r in enumerate(kb.itertuples()):
            for k in [r.part_no] + str(r.aliases).split(";"):
                c = compact(k)
                if len(c) >= min_len:
                    self.keys.append((c, i))

    def hit(self, text: str):
        t = compact(text)
        hits = {i for c, i in self.keys if c in t}
        return hits.pop() if len(hits) == 1 else None


def build_components(readings: pd.DataFrame, kb: pd.DataFrame, abbreviations: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    m, exact = Matcher(kb_text(kb), abbreviations), ExactIndex(kb)
    kb_ids, statuses = kb.kb_id.tolist(), kb.lifecycle_status.tolist()
    comps, ev = [], []
    for i, r in enumerate(readings.itertuples()):
        idx = exact.hit(r.raw_text)
        if idx is not None:
            conf, evidence = 0.97, {"exact": True}
        else:
            idx, conf, evidence = m.match(r.raw_text)
        read_conf = float(r.confidence)
        conf_all = round(min(conf, read_conf), 3) if idx is not None else 0.0
        review = idx is None or conf_all < REVIEW_BELOW
        reason = "no KB match" if idx is None else ("low confidence" if conf_all < REVIEW_BELOW else "")
        eid = f"EV-{i + 1:05d}"
        comps.append({"component_id": r.component_id, "machine_id": r.machine_id, "kb_id": kb_ids[idx] if idx is not None else "",
                      "part_no_read": r.raw_text, "component_type": r.component_type_hint,
                      "lifecycle_status": statuses[idx] if idx is not None else "unknown", "date_code": r.date_code,
                      "confidence": conf_all, "method": r.method, "needs_review": "yes" if review else "no",
                      "review_reason": reason, "evidence_id": eid})
        ev.append({"evidence_id": eid, "entity_type": "component", "entity_id": r.component_id, "photo_id": r.photo_id,
                   "reading_json": json.dumps({"raw_text": r.raw_text, "read_confidence": read_conf, "match": evidence}),
                   "source_url": kb.source_url.iloc[idx] if idx is not None else "", "confidence": conf_all,
                   "reviewer": "", "reviewed_on": ""})
    return pd.DataFrame(comps), pd.DataFrame(ev)


def match_spares(spares: pd.DataFrame, kb: pd.DataFrame, abbreviations: dict[str, str]) -> pd.DataFrame:
    m, exact = Matcher(kb_text_long(kb), abbreviations), ExactIndex(kb)
    rows = []
    for r in spares.itertuples():
        text = f"{r.part_no} {r.description}" if isinstance(r.part_no, str) and r.part_no else str(r.description)
        idx = exact.hit(text)
        conf = 0.97 if idx is not None else 0.0
        if idx is None:
            idx, conf, _ = m.match(text)
        rows.append({"spare_id": r.spare_id, "kb_id": kb.kb_id.iloc[idx] if idx is not None else "", "confidence": conf})
    return pd.DataFrame(rows)
