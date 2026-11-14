"""Accuracy vs planted truth. Owner: Role A. Milestone M3.

Run: python -m afterlife.evaluate
Prints precision / recall per source_table and per method.
"""
import pandas as pd


def score(links: pd.DataFrame, truth: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError  # TODO(A)


if __name__ == "__main__":
    from afterlife.io import load
    from afterlife.match import link_all
    t = load()
    print(score(link_all(t), t["truth_links"]))
