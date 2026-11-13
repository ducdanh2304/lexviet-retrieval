# LexViet — Vietnamese Legal Retrieval

LexViet retrieves the Vietnamese legal documents most relevant to a natural-language question. The research system combines eleven lexical, dense, memory, prior, and graph rankings with weighted reciprocal-rank fusion, learning-to-rank, and six-view transformer reranking. Its final constrained selector improved internal five-fold Recall@5 without reducing the frozen Top-20/30/60 candidate sets.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](pyproject.toml)
[![Tests](https://github.com/ducdanh2304/lexviet-retrieval/actions/workflows/tests.yml/badge.svg)](https://github.com/ducdanh2304/lexviet-retrieval/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/Code-MIT-2EA44F.svg)](LICENSE)

## My contributions

- Designed and integrated the ranking funnel from 11-signal retrieval and weighted RRF through LambdaMART, six-view Jina scoring, calibrated hard-negative selection, and constrained Top-5 selection.
- Built five-fold out-of-fold evaluation and membership guardrails; the selected policy increased internal CAL512 Top-5 hits from 466 to 475 while preserving Top-20/30/60 membership.
- Implemented resumable SQLite materialization, three-way GPU sharding, deterministic merging, and SHA-256 lineage checks for 748,800 private reranker score rows.
- Packaged the public-safe core utilities, tests, FastAPI interface, aggregate evidence, and architecture documentation without publishing restricted benchmark data or model caches.

The project uses third-party pretrained models and open-source libraries credited below. Competition work also included teammate-provided experiments; the preserved public artifacts do not provide a complete teammate-by-teammate contribution ledger, so this repository does not claim sole authorship of every experiment.

## Results at a glance

### Internal evaluation

Five-fold out-of-fold evaluation on **CAL512: 512 questions and 712 labeled relevant question-document pairs**.

| Pipeline checkpoint | Recall@K numerator | Recall@K | Weighted recall | Zero-hit queries |
|---|---:|---:|---:|---:|
| Stable Top-5 | 466 / 712 | 0.6545 | 0.9481 | 92 |
| Stable Top-20 | 613 / 712 | 0.8610 | 0.9861 | 25 |
| Calibrated hard-negative Top-20 | 616 / 712 | 0.8652 | 0.9865 | 25 |
| **Constrained-score Top-5** | **475 / 712** | **0.6671** | **0.9503** | **86** |
| Stable Top-60 coverage | 686 / 712 | 0.9635 | 0.9965 | 5 |

The final Top-5 policy recovered **9 additional relevant documents** over the stable Top-5. Its query bootstrap reported a 95% hit-delta interval of `[1, 18]` and `P(delta > 0) = 0.9775`. See [experiments and ablations](docs/experiments.md) for scope and caveats.

### Competition evaluation

Developed and evaluated in the context of the **UIT Data Science Challenge, Task 1: Legal Retrieval**. A submission over 2,080 private questions received a **reported competition score of 0.9428**. The private evaluator and labels are unavailable, so this number is not presented as accuracy, Recall@K, or an independently reproducible benchmark.

## System architecture

<picture>
  <source srcset="docs/assets/inference-pipeline.svg" type="image/svg+xml">
  <img src="docs/assets/inference-pipeline.png" alt="LexViet vertical inference pipeline from a Vietnamese legal query to five document identifiers" width="900">
</picture>

Editable source: [`docs/diagrams/inference-pipeline.mmd`](docs/diagrams/inference-pipeline.mmd).

| Stage | Model / method | Purpose |
|---|---|---|
| Candidate retrieval | Fine-tuned `mainguyen9/vietlegal-harrier-0.6b`, `BAAI/bge-m3`, `bqbbao6/vietnamese-legal-embedding`; TF-IDF memory/corpus; `huyydangg/DEk21_hcmute_embedding_v2`; label/prototype/graph signals | Build complementary document rankings |
| Fusion | Weighted reciprocal-rank fusion, `k=3` | Merge 11 rankings into Top-150 without calibrating incompatible score scales |
| Learned selection | Two-stage LightGBM LambdaMART | Select and reorder the stable Top-60 |
| Passage scoring | FT BGE-M3 view selection + `jinaai/jina-reranker-v3.5` | Score 3 lexical sections and 3 dense windows per document |
| Hard boundary | Sigmoid-calibrated logistic/LightGBM ranking | Improve Top-20 while freezing Top-30/60 membership |
| Final selection | 18 experts + Ridge gain/loss router | Choose five documents only inside Hard Top-20 |
| Protection | Exact normalized-query match | Protect known relevant documents only for exact matches |

The diagram describes research **batch inference**, not the public API. Training, checkpoint, embedding, and index lineage are documented in [architecture](docs/architecture.md).

## Key engineering decisions

| Decision | Why it was chosen | Evidence / trade-off |
|---|---|---|
| Fuse heterogeneous rankings before learned reranking | Lexical, dense, memory, and graph methods fail differently | Stable Top-60 retained 686/712 relevant documents |
| Use legal-structure-aware chunks | Relevant provisions may occur deep inside long legal documents | 596,062 chunks preserve document IDs and section context; higher storage cost |
| Score six query-conditioned views | A single prefix can miss the answering article | 3 lexical + 3 FT BGE-M3 windows; 6× reranking workload |
| Cross-fit learned stages | Prevent selector decisions from becoming in-sample ranker features | Fixed five-fold OOF audit; more models and artifacts to manage |
| Constrain Top-5 to Hard Top-20 | Improve precision without destroying candidate coverage | Top-5 466→475 while Top-20/30/60 membership stayed fixed |
| Cache passages and scores in SQLite | Long reranking jobs must survive interruption | Resume/shard/merge validation; additional artifact governance |

## Quick start

The public repository contains tested ranking utilities and an eight-document **synthetic BM25 API demo**. It does **not** run the research models or reproduce the reported research/competition results.

```bash
git clone https://github.com/ducdanh2304/lexviet-retrieval.git
cd lexviet-retrieval
python -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\activate
python -m pip install -e ".[api,test]"
python -m pytest -q
python -m uvicorn legalir_api.app:app --reload
```

Open <http://127.0.0.1:8000/docs>, or send a request:

```bash
curl -X POST http://127.0.0.1:8000/v1/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query":"thủ tục thay đổi họ tên","top_k":1}'
```

Response observed from the local smoke test (the timing field is intentionally omitted because this synthetic demo does not represent research-pipeline latency):

```json
{
  "query": "thủ tục thay đổi họ tên",
  "hits": [{
    "document_id": "demo_002",
    "score": 9.412696,
    "title": "Thay đổi họ tên"
  }],
  "backend": "public-demo-bm25"
}
```

The public package also exposes weighted RRF, constrained Top-5, ranking metrics, membership invariants, and submission validation. Docker users can run `docker compose up --build`.

## Repository structure

```text
artifacts/              sanitized aggregate metrics and source-report hashes
configs/                public-safe frozen research configuration
data/                   eight-document synthetic API corpus
docs/                   architecture, experiments, pipeline, limitations
src/legalir_portfolio/  RRF, constrained selection, metrics, validation
src/legalir_api/        synthetic BM25/FastAPI demo
tests/                  unit, artifact, and API smoke tests
```

## Documentation, limitations, and attribution

- [Architecture and training artifacts](docs/architecture.md)
- [Full pipeline walkthrough](docs/full_pipeline.md)
- [Experiments and ablations](docs/experiments.md)
- [Reproducibility and data governance](docs/reproducibility.md)
- [Known source gap](docs/source_gaps.md)
- [Portfolio audit report](docs/audit_report.md)

**Limitations.** The restricted corpus, labels, trained checkpoints, embeddings, and caches are not distributed. CAL512 is a small internal audit split. Exact-match protection is intentionally narrow, and the public synthetic demo is only an interface/packaging example.

**Pretrained models.** [`mainguyen9/vietlegal-harrier-0.6b`](https://huggingface.co/mainguyen9/vietlegal-harrier-0.6b), [`BAAI/bge-m3`](https://huggingface.co/BAAI/bge-m3), [`bqbbao6/vietnamese-legal-embedding`](https://huggingface.co/bqbbao6/vietnamese-legal-embedding), [`huyydangg/DEk21_hcmute_embedding_v2`](https://huggingface.co/huyydangg/DEk21_hcmute_embedding_v2), [`AITeamVN/Vietnamese_Reranker`](https://huggingface.co/AITeamVN/Vietnamese_Reranker), and [`jinaai/jina-reranker-v3.5`](https://huggingface.co/jinaai/jina-reranker-v3.5) retain their respective licenses and authorship.

Original public code and documentation in this repository are released under the [MIT License](LICENSE). External datasets, benchmark material, pretrained models, and teammate contributions retain their original ownership and terms.
