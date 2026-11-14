"""Accuracy vs planted truth. Owner: shared (each thread scores its own source_table). Milestone M3.

Run: python -m afterlife.evaluate
Prints precision / recall per source_table and per method.
"""
import pandas as pd


def score(links: pd.DataFrame, truth: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError  # TODO(shared)


if __name__ == "__main__":
    from afterlife.io import load
    from afterlife.match import link_all
    t = load()
    try:
        print(score(link_all(t), t["truth_links"]))
    except NotImplementedError:
        print("accuracy: matching or scoring not built yet")
