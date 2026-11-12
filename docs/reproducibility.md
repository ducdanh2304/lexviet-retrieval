# Reproducibility and data governance

## Public versus private artifacts

The original system archive remains private because it contains restricted
questions and derived caches. The GitHub repository must never include:

- `private-official.json`, train labels, or warmup labels;
- submission JSON/ZIP files;
- SQLite score caches;
- embeddings or model weights;
- Kaggle credentials or dataset tokens;
- raw query/document text from restricted datasets.

## Frozen private archive

The final archive was created with:

- 538 artifacts;
- 4,637,899,415 uncompressed bytes;
- SHA-256 inventory for every file;
- streamed `.tar.zst` compression;
- split-part checksums;
- restore verification against the artifact manifest.

## Reproduction levels

### Level A — methodology replay

Use this repository with synthetic or independently licensed data to inspect
and rerun ranking, policy, and audit logic.

### Level B — cache-boundary replay

Authorized users provide the frozen Top-150, score caches, Jina SQLite, policy
bundle, and query identifiers. The pipeline recreates Top-60/20/5 and audits
without rerunning foundation models.

### Level C — full rebuild

Authorized users additionally provide the original corpus, trained model
checkpoints, embedding matrices, and retrieval indexes. This reconstructs all
signals from source.

## Deterministic checks

Every serious run should validate:

```text
query count
candidate count and uniqueness
expected score-row count
fold identity
Top-k membership invariants
public/private-label usage flags
artifact SHA-256
submission ZIP round trip
```

## Expected schemas

Ranking artifacts should expose a mapping:

```json
{
  "documents": {
    "question_id": ["doc_id_1", "doc_id_2"]
  }
}
```

Submission files contain exactly five unique document identifiers per query:

```json
{
  "question_id": {
    "answer": ["doc_1", "doc_2", "doc_3", "doc_4", "doc_5"]
  }
}
```
