# System architecture

This is a compact architecture summary. The evidence-backed implementation
walkthrough, including fine-tuning tuple construction and exact model settings,
is in [full_pipeline.md](full_pipeline.md). The FastAPI demo is not part of the
full research ranking path.

## 1. Candidate generation

The first stage maximizes coverage rather than precision. Eleven heterogeneous
rankings are fused by weighted reciprocal-rank fusion into a Top-150 union.
Each source has its own cutoff so weak long tails do not dominate the pool.

The frozen RRF score for document `d` is:

```text
score(d) = Σ_i weight_i / (k + rank_i(d))
```

where a missing document contributes zero for that source.

## 2. Learned Top-60 selector

A learned selector reduces Top-150 to Top-60 using lexical, dense, section,
full-document, candidate-stage, and rank features. A second ranker reorders the
selected candidates. Cross-fitted train selections prevent the final ranker
from learning against its own in-sample decisions.

## 3. Multi-view document representation

Long legal documents are not truncated to one arbitrary prefix. The pipeline
scores three lexical sections and three dense query-conditioned segments. This
raises the chance that the relevant provision survives document length and
boilerplate.

## 4. Jina listwise reranking

The listwise reranker scores all 60 candidates for each of six views. Passage
materialization and model scores are stored separately in SQLite, enabling:

- resume after interruption;
- query sharding across machines;
- deterministic merge validation;
- reuse by later audits without another GPU pass.

## 5. Hard-negative Top-20

The hard-negative stage learns which candidates should remain in the decision
boundary. It improves Top-20 coverage from 613 to 616 relevant documents while
leaving Top-30 and Top-60 coverage unchanged.

## 6. Constrained Top-5 selection

The score router selects five documents only inside the frozen Hard Top-20.
This improves Top-5 from 466 to 475 relevant documents. The policy is rejected
if it changes the protected candidate universe or produces unsafe fold-level
regressions.

## 7. Exact-overlap protection

An exact normalized-query match against previously labeled, legally reusable
examples is handled as a deterministic final rule. Semantic-neighbor transfer
was audited separately and was not trusted as equivalent to exact matching.

## 8. Artifact lineage

Every final artifact records:

- source paths and schema;
- SHA-256 identities;
- number of queries/documents/rows;
- whether labels were used;
- policy configuration;
- upstream artifact identities.

This makes the pipeline auditable even when full model weights are stored in a
separate private artifact registry.
