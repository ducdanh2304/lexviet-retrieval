"""Recall metrics and non-regression checks used by the audit pipeline."""

from __future__ import annotations

from collections.abc import Mapping, Sequence, Set


def evaluate_ranking(
    rankings: Mapping[str, Sequence[str]],
    gold: Mapping[str, Set[str]],
    *,
    cutoff: int,
    weights: Mapping[str, float] | None = None,
) -> dict[str, float | int]:
    """Compute micro recall, weighted recall, and zero-hit query count."""
    if set(rankings) != set(gold):
        raise ValueError("rankings and gold must cover identical queries")
    hits = total = zero = 0
    weighted_hits = weighted_total = 0.0
    for qid, relevant in gold.items():
        relevant = {str(doc) for doc in relevant}
        found = len(set(map(str, rankings[qid][:cutoff])) & relevant)
        weight = 1.0 if weights is None else float(weights[qid])
        hits += found
        total += len(relevant)
        zero += found == 0
        weighted_hits += weight * found
        weighted_total += weight * len(relevant)
    if total == 0 or weighted_total == 0:
        raise ValueError("gold set is empty")
    return {
        "hits": hits,
        "gold": total,
        "recall": hits / total,
        "weighted_recall": weighted_hits / weighted_total,
        "zero_hit_queries": zero,
    }


def membership_is_preserved(
    baseline: Mapping[str, Sequence[str]],
    candidate: Mapping[str, Sequence[str]],
    cutoff: int,
) -> bool:
    """Return True when both rankings contain the same Top-k documents."""
    return set(baseline) == set(candidate) and all(
        set(map(str, baseline[qid][:cutoff]))
        == set(map(str, candidate[qid][:cutoff]))
        for qid in baseline
    )
