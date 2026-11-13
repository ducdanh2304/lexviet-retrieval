# Reproducibility and data governance

## What can be reproduced from this repository

With Python 3.10+, a reviewer can install the package and run:

```bash
python -m pip install -e ".[api,test]"
pytest -q
python -m uvicorn legalir_api.app:app
```

This exercises:

- reciprocal-rank fusion;
- constrained Top-5 selection and membership preservation;
- recall, weighted recall, and zero-hit metrics;
- submission JSON/ZIP validation;
- synthetic BM25 retrieval and FastAPI schemas;
- the sanitized aggregate metrics artifact.

## What requires private artifacts

The following stages are not runnable from the public repository alone:

- data cleaning and the fixed research split;
- three dense-encoder fine-tuning jobs;
- generation of all eleven retrieval signals;
- LightGBM selector/ranker training;
- six-view Jina passage materialization and scoring;
- private Top-60/20/5 inference and submission generation.

An authorized replay requires the original corpus and labels, fold identities,
model checkpoints, embedding/index files, Top-150 rankings, feature caches,
Jina SQLite scores, and frozen policy bundles. The code paths described in the
case study were preserved privately with artifact hashes, but those inputs are
not redistributable.

## Aggregate evidence

[`../artifacts/cal512_metrics.json`](../artifacts/cal512_metrics.json) contains
only public-safe aggregate values and SHA-256 identities of the source reports.
It intentionally contains no query/document text, IDs, labels, rankings, or
predictions.

## Deterministic checks used in the research pipeline

```text
query count
candidate count and uniqueness
fold identity
expected passage/score row count
Top-k membership invariants
label-usage flags
upstream and output SHA-256
submission ZIP round trip
```

## Data policy

Do not commit:

- train, warmup, or private benchmark questions/labels;
- raw legal corpus files unless their license explicitly permits it;
- submission JSON/ZIP files;
- SQLite score caches, embeddings, indexes, or model weights;
- API keys, Kaggle credentials, or local filesystem manifests.

The repository `.gitignore` blocks common forms of these artifacts. Reviewers
should still inspect `git status` and staged diffs before every push.
