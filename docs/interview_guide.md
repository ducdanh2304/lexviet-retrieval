# Interview guide — keep it simple

The public demo is intentionally smaller than the full research system. Be able
to explain these four ideas clearly; do not try to memorize every experiment.

## The four things to own

### 1. Candidate retrieval

**Simple explanation:** Different retrievers make different mistakes, so I
combine their ranked lists with weighted reciprocal-rank fusion.

**Formula:** `score(d) = sum(weight_i / (k + rank_i(d)))`.

### 2. Learning to rank

**Simple explanation:** Retrieval finds a broad candidate pool. LambdaMART then
learns from rank and model-score features to move likely relevant documents
upward.

### 3. Safe Top-5 selection

**Simple explanation:** I only choose the final five documents from a fixed
Top-20 pool. This prevents the final model from accidentally destroying the
candidate coverage built by earlier stages.

### 4. Evaluation and deployment

**Simple explanation:** I use five-fold out-of-fold evaluation, weighted recall
and gained/lost cases. The demo exposes the retrieval interface with FastAPI
and packages it with Docker.

## Likely questions and short answers

### Why not use one embedding model?

Legal queries may match exact terminology, paraphrases, citations, or a small
section of a long document. Lexical and dense methods are complementary.

### Why Recall@5?

The task returns at most five documents. Missing a relevant document from that
small list is the main failure mode.

### Why weighted recall?

Raw recall treats every query equally. Weighted recall exposes cases where a
model gains easy examples but loses difficult, important ones.

### Why LambdaMART?

The data is naturally grouped by query and contains heterogeneous numeric rank
features. Tree-based learning-to-rank is strong, fast and interpretable for
this setting.

### What does Jina reranking do?

It reads the query and selected document passages jointly and provides a
strong semantic relevance signal after cheaper retrieval has reduced the
candidate set.

### Why six views?

Legal documents are long. Relevant content may appear in different sections,
so I score three lexical sections and three dense query-conditioned segments.

### What was your biggest engineering challenge?

Scoring 748,800 query-view-document combinations reliably. I used SQLite
checkpoints, deterministic shards, resume support and merge validation.

### Tell me about a failed experiment.

One V15 policy improved raw Top-5 hits from 475 to 477 but reduced weighted
recall. I rejected it as the safe default. This taught me to audit the type of
queries being lost, not only the aggregate score.

### Is the GitHub demo the full research model?

No. Restricted data and weights cannot be published. The demo uses synthetic
documents but preserves the API, fusion, validation and deployment patterns.

### What would you improve next?

Add a licensed public legal corpus, replace the demo backend with a compact
dense encoder, measure latency/recall trade-offs, and deploy on a small cloud
service with monitoring.

## Do not claim

- Do not claim V5/V15 scores that were never verified on the private benchmark.
- Do not say the synthetic demo reproduces the 0.9428 score.
- Do not say the private dataset is public.
- Do not claim production traffic; call it a production-style deployment demo.
