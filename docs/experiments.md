# Experiments and ablations

Unless stated otherwise, results use the fixed five-fold out-of-fold CAL512
audit: 512 questions and 712 relevant question-document pairs. The aggregate
numbers below were rechecked against the hashed private reports listed in
[`../artifacts/cal512_metrics.json`](../artifacts/cal512_metrics.json).

## Ranking funnel

| Variant | R@5 hits | Weighted R@5 | R@20 hits | Decision |
|---|---:|---:|---:|---|
| Stable ranking | 466 | 0.94806 | 613 | Baseline |
| Hard-negative Top-20 | 466 | 0.94806 | 616 | Keep for candidate boundary |
| Constrained router | 473 | 0.94977 | 616 | Useful, not best |
| Constrained score | **475** | **0.95029** | **616** | Selected |

For constrained score versus stable Top-5, the query bootstrap observed `+9`
hits, 95% interval `[1, 18]`, and `P(delta > 0) = 0.9775`. It improved 14
queries and harmed 5 at the relevant-document level. That result was accepted
because the aggregate raw and weighted metrics improved while Top-20/30/60
membership stayed fixed.

## Conservative alternatives

| Variant | R@5 hits | Weighted R@5 | Observation |
|---|---:|---:|---|
| Selective one-swap policy | 469 | 0.94859 | +3 hits over stable, but bootstrap interval included regression |
| Query abstention gate | 470 | 0.94608 | Raw hits improved; weighted recall fell |
| V5-lite nested swap | 474 | 0.94713 | Lost one hit and weighted recall versus constrained score |

These experiments illustrate why raw Recall@5 was not used alone. A policy can
recover more documents overall while dropping a heavily weighted relevant
document on a difficult query.

## Multi-view reranking audit

Jina scoring used six views for every Top-60 candidate: three lexical sections
and three dense windows. Before GPU inference, a token audit inspected 184,320
CAL passage views. At a 768-token document cap, each view had at most 1.31% of
passages above the cap, so the cap was accepted. The private batch workload was
then `2,080 × 60 × 6 = 748,800` scores, checkpointed in SQLite and split across
three machines.

## Acceptance criteria

A candidate policy was considered for private inference only when it met the
following evidence threshold:

1. improve the selected baseline at Top-5;
2. do not decrease difficulty-weighted Recall@5;
3. inspect per-fold deltas and bootstrap uncertainty;
4. account for both gained and lost relevant documents;
5. preserve protected Top-20/30/60 membership;
6. use no private labels during fitting or selection.

The purpose of these guardrails was not to guarantee leaderboard improvement;
it was to prevent a small, noisy audit from justifying a risky ranking change.
