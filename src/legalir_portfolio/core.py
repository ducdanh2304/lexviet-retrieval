"""Small, dependency-light versions of the core ranking operations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[str]],
    *,
    weights: Sequence[float] | None = None,
    limits: Sequence[int] | None = None,
    k: float = 60.0,
) -> list[str]:
    """Fuse rankings with weighted reciprocal-rank fusion.

    Duplicate documents inside one ranking are counted only at their first
    position. Ties are resolved by first appearance, making the result stable.
    """
    if weights is None:
        weights = [1.0] * len(rankings)
    if limits is None:
        limits = [len(row) for row in rankings]
    if not (len(rankings) == len(weights) == len(limits)):
        raise ValueError("rankings, weights, and limits must have equal length")
    if k < 0:
        raise ValueError("k must be non-negative")

    scores: dict[str, float] = {}
    first_seen: dict[str, int] = {}
    cursor = 0
    for ranking, weight, limit in zip(rankings, weights, limits):
        seen: set[str] = set()
        for rank, document in enumerate(ranking[: int(limit)], start=1):
            document = str(document)
            if document in seen:
                continue
            seen.add(document)
            if document not in first_seen:
                first_seen[document] = cursor
                cursor += 1
            scores[document] = scores.get(document, 0.0) + float(weight) / (
                float(k) + rank
            )
    return sorted(scores, key=lambda doc: (-scores[doc], first_seen[doc], doc))


def constrained_top5(
    hard_top20: Mapping[str, Sequence[str]],
    score_guide: Mapping[str, Sequence[str]],
) -> dict[str, list[str]]:
    """Select five guide documents inside each frozen Hard Top-20 universe.

    The remainder preserves the hard-negative order, so Top-20 membership is
    invariant by construction.
    """
    if set(hard_top20) != set(score_guide):
        raise ValueError("hard_top20 and score_guide must cover identical queries")
    output: dict[str, list[str]] = {}
    for qid, hard in hard_top20.items():
        hard = [str(doc) for doc in hard]
        if len(hard) < 20 or len(set(hard[:20])) != 20:
            raise ValueError(f"query {qid!r} does not have 20 unique hard candidates")
        universe = set(hard[:20])
        selected: list[str] = []
        for document in score_guide[qid]:
            document = str(document)
            if document in universe and document not in selected:
                selected.append(document)
            if len(selected) == 5:
                break
        if len(selected) < 5:
            selected.extend(
                document for document in hard[:20] if document not in selected
            )
            selected = selected[:5]
        chosen = set(selected)
        output[qid] = selected + [doc for doc in hard if doc not in chosen]
        if set(output[qid][:20]) != universe:
            raise AssertionError("constrained selection changed Top-20 membership")
    return output
