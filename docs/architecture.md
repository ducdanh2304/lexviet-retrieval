# Architecture

This document separates model development, research batch inference, stored
artifacts, and the small public API demo. Only the last path is directly
runnable from this repository without private inputs.

```mermaid
flowchart LR
  classDef artifact fill:#fff4d6,stroke:#8a6d1d
  classDef model fill:#e8f0fe,stroke:#3455a4
  classDef private fill:#fdeaea,stroke:#a33
  classDef public fill:#e7f7ed,stroke:#287a46

  subgraph train[Offline training]
    Q[Labelled questions]:::private --> SPLIT[Clean split + exact-collision removal]
    CORPUS[Legal corpus]:::private --> CHUNK[Hierarchy-aware chunker]
    SPLIT --> TUPLES[1 positive + 7 hard negatives]
    CHUNK --> TUPLES
    TUPLES --> ENC[Fine-tune Harrier, Vietnamese Legal Embedding, BGE-M3]:::model
    SPLIT --> OOF[Five-fold OOF feature construction]
    OOF --> LTR[Train selector, LambdaMART, calibrated policies]:::model
    ENC --> CKPT[(Checkpoints)]:::artifact
    CHUNK --> INDEX[(Chunk IDs, vectors, indexes)]:::artifact
    LTR --> POLICY[(Frozen fold models + policies)]:::artifact
  end

  subgraph batch[Research batch inference]
    QUESTION[Question] --> SIGNALS[11 independent rankings]
    CKPT --> SIGNALS
    INDEX --> SIGNALS
    SIGNALS --> RRF[Weighted RRF, Top-150]
    RRF --> SELECT[Learned Top-60 selector]
    POLICY --> SELECT
    SELECT --> SIX[3 lexical sections + 3 dense windows]
    SIX --> JINA[Jina listwise scoring]:::model
    JINA --> CACHE[(SQLite passage + score cache)]:::artifact
    CACHE --> HARD[Calibrated hard-negative Top-20]
    HARD --> FINAL[Constrained-score Top-5]
    FINAL --> EXACT[Exact normalized-query protection]
    EXACT --> OUTPUT[Five document IDs]
  end

  subgraph demo[Public demo]
    DEMO[(8 synthetic documents)]:::public --> BM25[BM25 retrieval]:::public
    BM25 --> FASTAPI[FastAPI /v1/retrieve]:::public
    RRFLIB[Tested RRF utility]:::public --> FUSE[FastAPI /v1/fuse]:::public
  end
```

## Ranking funnel

1. **Candidate generation:** eleven heterogeneous rankings produce complementary
   evidence. Weighted reciprocal-rank fusion forms a Top-150 union.
2. **Top-60 selection:** a cross-fitted learned selector concentrates expensive
   scoring on candidates near the decision boundary.
3. **Multi-view scoring:** long documents are represented by three lexical
   sections and three dense query-conditioned windows.
4. **Top-20 calibration:** relevance probabilities and stable-rank evidence
   reorder only the protected Top-30 boundary.
5. **Top-5 decision:** a constrained router chooses five documents from the
   frozen Hard Top-20; deeper membership cannot change.
6. **Deterministic protection:** exact normalized matches may protect known
   relevant documents. Semantic similarity alone is insufficient.

## Artifact contract

Long-running stages exchange immutable artifacts rather than hidden process
state. Each serious output records its schema, upstream path/hash, row or query
count, label-usage flag, and policy configuration. SQLite separates materialized
passages from model scores so reranking can resume and shards can be merged with
count and hash checks.

## Public code boundary

The repository includes implementations and tests for RRF, constrained Top-5,
metrics, membership invariants, submission validation, and the synthetic API.
The private training and inference scripts are documented from preserved source
reports but are not repackaged here because their required inputs cannot be
distributed.
