# VSOL Young Tech Talent Program — AI Engineer fit

Applications are open from **11/11 to 18/11/2026**. The official AI Engineer
description emphasizes model training/fine-tuning, dataset preparation,
evaluation, REST deployment, and PyTorch/Hugging Face experience.

Official page: <https://vsol.vn/young-tech-talent-program/>

## Requirement-to-evidence mapping

| VSOL requirement | Evidence in this project |
|---|---|
| Train/fine-tune ML and deep-learning models | FT-BGE/legal embeddings, LambdaMART rankers, reranker experiments |
| Prepare, clean and label datasets | 512-query calibrated audit set, deterministic schemas, exact-overlap audit |
| Evaluate models | Nested 5-fold OOF, bootstrap, weighted recall, gain/loss cases |
| REST APIs or microservices | FastAPI `/v1/retrieve`, `/v1/fuse`, `/health`, `/metrics` |
| PyTorch / Hugging Face | Transformer scoring pipeline and mixed-precision inference |
| NumPy / Scikit-learn | Feature engineering, logistic gates, calibration, evaluation |
| Production mindset | Docker, CI, unit tests, resumable SQLite, sharded GPU inference |
| English technical reading | English README, architecture and reproducibility documentation |

## Strong application narrative

Present this as a personal ML system with four ownership areas:

1. **Problem framing:** high-recall legal search with asymmetric Top-5 risk.
2. **Modeling:** multi-signal retrieval, learning-to-rank, reranking.
3. **Evaluation:** nested audits and safety guardrails, including rejected
   experiments that improved raw recall but hurt weighted recall.
4. **Engineering:** resumable multi-GPU scoring, API deployment, Docker, CI,
   artifact checksums and private-data governance.

## Two-minute interview pitch

> I built an end-to-end Vietnamese legal retrieval system. Eleven retrieval
> signals create a high-recall Top-150 pool, LambdaMART reduces it to Top-60,
> and a six-view transformer reranker scores different sections and dense
> segments of long legal documents. A calibrated hard-negative stage and
> constrained Top-5 selector improved audited relevant-document hits from 466
> to 475 while preserving the Top-20/30/60 universe. The verified private
> private-benchmark score was 0.9428. I also built resumable SQLite inference across
> three GPUs, nested evaluation guardrails, Dockerized FastAPI endpoints, CI,
> and reproducible artifact manifests. The most important lesson was that raw
> recall gains are not enough: I rejected models that increased raw hits but
> reduced weighted recall on difficult queries.

## Before applying

- Put the GitHub repository URL near the top of the CV.
- Add a screenshot of `/docs` Swagger UI to the README after running the API.
- Pin the repository on GitHub.
- Keep the CV to one page if possible.
- Attach the CV manually to the application email; the official page notes
  that email links cannot carry files.
