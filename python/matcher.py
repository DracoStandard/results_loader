"""Fuzzy-name matching, equivalent to the FuzzierSharp Fuzz.Ratio usage in
the original nameSort/compResults classes.
"""
from rapidfuzz import fuzz


def top_matches(name, candidates, limit=11):
    """candidates: iterable of (id, label). Returns the `limit` closest
    matches to `name`, sorted by fuzzy ratio descending, as (id, label, score).
    """
    scored = [(cid, label, fuzz.ratio(name, label)) for cid, label in candidates]
    scored.sort(key=lambda item: item[2], reverse=True)
    return scored[:limit]
