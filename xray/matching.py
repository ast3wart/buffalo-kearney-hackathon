"""Text normalization + fuzzy matching, kept from Afterlife's purchase-line matcher (97.8-100% precision/recall
on held-out data). Use it to match what vision reads off a nameplate ("A-B 1756-L61 SER B") to a
knowledge-base entry ("Allen-Bradley ControlLogix 1756-L61").

Nothing here names a specific manufacturer or part; abbreviations are data passed in by the caller.
"""
import re

import numpy as np
from rapidfuzz import fuzz, process

UNITS = r"MM|IN|V|W|A|HP|KW|KVA|HZ|CC|AH|TON|UF|C|BAR|PSI|MIC|T"
MIN_SCORE = 55.0                        # below this, normally no match ...
WEAK_SCORE, WEAK_MARGIN = 40.0, 15.0    # ... unless it's a weak but clear winner: then a low-confidence match
LOW_CONF = 0.4                          # low-confidence matches go to human review


def normalize(text: str, abbreviations: dict[str, str] | None = None) -> str:
    """Uppercase, split on punctuation, expand abbreviations (e.g. {"AB": "ALLEN BRADLEY"})."""
    abbreviations = abbreviations or {}
    tokens = re.split(r"[^A-Z0-9.]+", str(text).upper())
    return " ".join(abbreviations.get(t, t) for t in tokens if t)


def canon(text: str, abbreviations: dict[str, str] | None = None) -> str:
    """normalize() plus unit/dimension clean-up so '20 mm' == '20MM' and '35 x 47' == '35X47'."""
    s = normalize(text, abbreviations)
    s = re.sub(r"(\d)\s*X\s*(?=\d)", r"\1X", s)
    s = re.sub(rf"(\d)\s+({UNITS})\b", r"\1\2", s)
    return s


def spec_tokens(s: str) -> set[str]:
    """Tokens with a digit (catalog numbers, sizes), also split on '-' so 1756-L61 also yields 1756 and L61."""
    out = set()
    for tok in s.split():
        if any(ch.isdigit() for ch in tok):
            out.add(tok)
            out.update(p for p in tok.split("-") if any(ch.isdigit() for ch in p))
    return out


def numbers(s: str) -> set[str]:
    """Every number in the text, unit-free: '63X300' -> {63, 300}. Robust to word order and formatting."""
    return {n.lstrip("0") or "0" for n in re.findall(r"\d+(?:[./]\d+)?", s)}


class Matcher:
    """Match free text against a fixed list of candidate descriptions (e.g. knowledge-base products)."""

    def __init__(self, candidates: list[str], abbreviations: dict[str, str] | None = None):
        self.abbr = abbreviations or {}
        self.canon = [canon(c, self.abbr) for c in candidates]
        self.nums = [numbers(c) for c in self.canon]
        self.specs = [spec_tokens(c) for c in self.canon]

    def match(self, text: str) -> tuple[int | None, float, dict]:
        """-> (candidate index or None, confidence 0-1, evidence dict)."""
        c = canon(text, self.abbr)
        nums, specs = numbers(c), spec_tokens(c)
        s_set = process.cdist([c], self.canon, scorer=fuzz.token_set_ratio)[0]
        s_sort = process.cdist([c], self.canon, scorer=fuzz.token_sort_ratio)[0]
        spec = np.array([len(nums & pn) / len(nums | pn) if (nums or pn) else 0.0 for pn in self.nums])
        score = 0.40 * s_set + 0.30 * s_sort + 30.0 * spec
        order = np.argsort(-score)
        best, second = int(order[0]), int(order[1] if len(order) > 1 else order[0])
        margin = float(score[best] - score[second])
        ev = {"score": round(float(score[best]), 1), "margin": round(margin, 1),
              "shared_numbers": sorted(nums & self.nums[best]), "shared_specs": sorted(specs & self.specs[best]),
              "runner_up": second}
        if score[best] < MIN_SCORE:
            if score[best] >= WEAK_SCORE and margin >= WEAK_MARGIN:
                return best, LOW_CONF, {**ev, "weak_match": True}
            return None, 0.0, ev
        conf = float(np.clip(0.55 + margin / 40 + (score[best] - MIN_SCORE) / 200, 0.3, 0.95))
        return best, round(conf, 3), ev
