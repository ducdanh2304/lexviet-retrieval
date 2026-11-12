# Experiment and ablation log

All values below come from the fixed 512-query calibration audit unless marked
as private-benchmark results.

## Successful components

| Experiment | Recall@5 hits | Delta | Weighted R@5 | Decision |
|---|---:|---:|---:|---|
| Stable Top-5 | 466 | — | 0.94806 | Baseline |
| Constrained router | 473 | +7 | 0.94977 | Useful |
| Constrained score | **475** | **+9** | **0.95029** | Deployed |

Hard-negative mining improved Top-20 from `613` to `616` without reducing
Top-30 or Top-60 coverage.

## Conservative swap audits

| Method | Before → after | Gains | Losses | Weighted effect | Decision |
|---|---:|---:|---:|---|---|
| Selective swap | 466 → 469 | 4 | 1 | positive raw audit | Diagnostic only |
| Query abstention gate | 466 → 470 | 6 | 2 | uncertain | Diagnostic only |
| V5 strict nested | 475 → 476 | 1 | 0 | non-negative | Experimental deploy |
| Native V15 accept-all | 475 → 477 | 7 | 5 | **decreased** to 0.94161 | Rejected as safe default |
| Segment seed expansion | 475 → 474 | 0 | 1 | decreased | Rejected |
| V15 + segment two-head | 475 → 474 | 0 | 1 | decreased | Rejected |

## V15 abstention audits

The 99 original V15 swaps contained only 7 gain, 5 loss, and 87 neutral
examples. Two gates were evaluated with the original five folds:

| Gate | Accepted | Gains | Losses | Top-5 | Weighted R@5 | Result |
|---|---:|---:|---:|---:|---:|---|
| Threshold gate | 24 | 2 | 3 | 474 | 0.94411 | Revert baseline |
| Utility heads | 8 | 2 | 2 | 475 | 0.94727 | Revert baseline |

This was an important negative result: reducing the number of swaps did not
make the learned gate safe. The rare losses carried disproportionately large
weights.

## Document-level gold-probability audit

A later experiment trained `P(document is relevant)` using all
`512 × 20 = 10,240` Hard-Top-20 examples with 616 positive labels, then locked
Top-1/2/3 and allowed only rank-6–20 candidates to replace slot 4 or 5.

Despite the larger training set, early outer folds lost relevant documents.
This demonstrated that more labels alone do not solve distribution shift at a
very narrow ranking boundary.

## Evaluation principles

An experiment was eligible for private deployment only if:

1. Top-5 improved over 475;
2. weighted Recall@5 did not decrease;
3. no outer fold regressed;
4. gained cases exceeded lost cases, preferably with zero loss;
5. Top-20/30/60 invariants remained fixed;
6. no private labels entered training or selection.

The final verified private-benchmark run used the strongest stable policy,
not the experiment with the largest raw offline gain.
