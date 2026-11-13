# Full retrieval pipeline

This document describes my complete Vietnamese LegalIR research system. It is
reconstructed from the preserved source code, manifests and audit reports.
The FastAPI application in this repository is only a serving demo; it is not
the full retrieval backend.

## 1. Data layers

The source data uses a JSON object keyed by question ID. Each labelled row
contains a Vietnamese legal question and one or more relevant document IDs.
Each corpus document contains an ID, name, source link and passage. The
preprocessing run loaded 7,000 labelled questions and 8,532 legal documents.

The project then used several data scopes for different purposes:

- **6,985 labelled training questions** powered fold-safe memory and prior
  retrieval signals.
- A fixed **2,155-question labelled evaluation table** was held out from
  encoder training.
- Of the remaining 4,830 questions, seven had an exactly matching normalized
  question in the evaluation table. Removing those collisions produced the
  **4,823-question clean subset** used to fine-tune the three dense encoders.
- A fixed **CAL512** audit set contained 512 questions and 712 relevant
  question-document pairs. It was the labelled evaluation boundary for the
  final ranking funnel.
- The private test set contained **2,080 unlabelled questions**.
- The prepared corpus cache contained **596,062 text chunks**, each aligned to
  a chunk ID and its parent document ID.

The preserved verifier proves the counts, ID uniqueness, chunk/text/document
alignment, absence of train/evaluation query-ID overlap and absence of exact
normalized question overlap. The split manifest records the encoder-training
rule precisely: start from 6,985 labelled questions, exclude the fixed 2,155
evaluation query IDs, then remove seven normalized exact-question collisions
from the remaining training side (`6,985 - 2,155 - 7 = 4,823`). The earlier
raw-to-clean operation that removed 15 rows from the original 7,000-question
file is not present in the recovered source, so its rationale is not invented
here.

### Structure-aware legal document chunking

The corpus was cleaned by normalizing line endings, collapsing runs of blank
lines and removing trailing whitespace. Chunk length was measured with the
Harrier tokenizer rather than whitespace counts. The target was 500 tokens
with 100-token overlap only when the final fallback required a token window.

The chunker used three ordered strategies:

1. **Legal hierarchy:** detect `Chương`, `Điều` and `Khoản`; keep an article
   intact when possible and split an overlong article by clauses.
2. **Numbered sections:** for standards and technical documents without
   `Điều`, detect at least three mostly increasing numbered sections such as
   `4.1`; split an overlong section by its decimal subsections.
3. **Paragraph fallback:** group adjacent paragraphs up to the token budget,
   retaining one paragraph of overlap. Token-window splitting was used only
   when one paragraph was already too long.

Dense encoders and rerankers received an injected header containing the
document name and detected article/section context. BM25 received the raw
content without this synthetic header so term frequencies were not distorted.
All chunks retained their original parent `document_id`; chunk scores could
therefore be max-pooled back to the document-level labels. Duplicate article
numbers inside attachments were handled by deterministic unique chunk IDs.

The resulting cache contained 596,062 chunks from 8,532 documents, an average
of 69.86 chunks per document. Precomputed embedding matrices were checked for
both exact chunk-ID membership and row ordering before building the search
index.

## 2. Fine-tuning data construction

All three dense encoders were trained from the same document choices so their
results remained comparable.

For each clean training question:

1. encode the question with the base Harrier and base BGE-M3 models;
2. retrieve the best 256 corpus chunks from each model;
3. convert chunk hits to parent documents and combine both lists with RRF
   (`k=60`);
4. remove every labelled relevant document;
5. retain the first seven documents as explicit hard negatives;
6. choose the positive passage as the labelled chunk with the highest
   base-Harrier similarity;
7. assert that no selected negative overlaps the gold document set;
8. render the same one-positive/seven-negative document tuple using each
   model's required prefixes.

The renderer also checks that all 4,823 rows have unique query IDs, identical
query order across models, non-empty text and a valid `1 + 7` tuple.

### Encoder training

| Encoder | Input convention | Length | Training setup |
|---|---|---:|---|
| VietLegal Harrier 0.6B | instruction-prefixed query; unprefixed passage | 512 | LR `3e-6`, logical batch 16, BF16, FlashAttention2, cached multiple-negatives ranking loss |
| Vietnamese Legal Embedding | `query:` / `passage:` | 512 | LR `2e-5`, logical batch 16, BF16, FlashAttention2, cached multiple-negatives ranking loss |
| BGE-M3 | no prefix | query 192, passage 768 | LR `1e-5`, group size 8, temperature `0.02`, normalized CLS dense output, BF16, FlashAttention2 |

All models ran for one epoch with deterministic seed `20260904`. Smoke tests
selected a memory-safe mini/sub-batch size, but did not change the rows,
positive/negative documents, loss or maximum lengths.

## 3. Eleven candidate-retrieval signals

Every signal produced a document ranking (normally Top-200) for each question.

1. **`harrier_ft`** — direct dense retrieval with the fine-tuned Harrier.
2. **`bge_ft`** — direct dense retrieval with fine-tuned BGE-M3; CLS and mean
   pooling were candidates during tuning.
3. **`legal_embedding_ft`** — direct dense retrieval with the fine-tuned
   Vietnamese Legal Embedding model.
4. **`lexical_memory`** — word/bigram TF-IDF nearest labelled questions;
   neighbor labels contribute `similarity^4 / (10 + neighbor_rank)`.
5. **`semantic_memory`** — the same label-transfer rule using BGE-FT question
   embeddings and cosine-nearest labelled questions.
6. **`corpus_lexical`** — direct word/bigram TF-IDF search over document name
   plus passage (`min_df=2`, `max_df=0.995`, up to 500,000 features).
7. **`bge_prototype`** — cosine similarity to a normalized centroid of the
   BGE-FT embeddings of training questions labelled with each document.
8. **`label_prior`** — query-independent document frequency in the permitted
   labelled training fold.
9. **`legal_dense`** — direct dense retrieval with the original Vietnamese
   Legal Embedding model.
10. **`dek21_direct`** — direct retrieval with the DEK21 encoder/cache.
11. **`citation_graph`** — expands documents appearing in the direct signals'
    Top-30 through the legal citation graph; outgoing neighbors receive full
    weight and incoming neighbors half weight.

Dense retrieval first searched up to 32,768 chunk candidates, then collapsed
them to unique parent documents. Label-dependent signals 4, 5, 7 and 8 were
built out of fold: a CAL query could never retrieve labels derived from its
own held-out fold.

## 4. Weighted RRF to Top-150

The 11 lists were combined with weighted reciprocal-rank fusion:

```text
RRF(d) = sum_i weight_i / (3 + rank_i(d))
```

Only documents within each signal's frozen depth contributed. The selected
full-fit configuration was:

```text
weights = [1.500, 0.668, 0.632, 0.501, 0.093,
           0.747, 0.299, 0.186, 0.620, 0.443, 0.317]
limits  = [30, 50, 30, 50, 50, 100, 100, 50, 20, 50, 100]
```

Configuration search evaluated BGE pooling, RRF `k`, per-signal depths and
weights. A fixed five-fold lock selected a configuration on four folds and
evaluated it on the fifth; the final private configuration was then fitted on
all permitted labelled data. Ties used deterministic document-ID ordering.

## 5. Learned Top-60 selector

The Top-60 stage used two LightGBM LambdaMART rankers rather than a single
global score.

### Candidate selector

- 13 native rank/score features described the RRF position, candidate-stage
  position, FT-BGE full-document score and Vietnamese reranker score.
- Documents in the Section-1 boundary (ranks 21–90) received ten additional
  Section-2, Section-3 and dense-window score/rank features.
- The model used `lambdarank`, NDCG at 5/10/20/30, 300 trees, learning rate
  0.03, 15 leaves, minimum child size 35, L1 0.5 and L2 8.0.
- Query weights depended on the depth at which its hardest gold document was
  found, preventing easy questions from dominating.

Five cross-fitted selector models generated out-of-fold Top-60 lists for
CAL512. A full-fit selector generated the private Top-60.

### Final Top-60 ranker

A second LambdaMART model learned from the cross-fitted selections, using 15
features over the selected candidates. This prevents the second model from
training on an in-sample decision made by the first selector.

The resulting stable Top-60 covered **686/712** CAL512 gold documents
(`Recall@60 = 0.9635`).

## 6. Six-view Jina listwise scoring

Each of the 60 candidates was represented six ways:

- three query-conditioned lexical sections (`section1`, `section2`,
  `section3`);
- three FT-BGE dense windows (`dense1`, `dense2`, `dense3`).

Passages were capped at 768 tokens and truncated at a nearby sentence/line
boundary; questions were capped at 512 tokens. Jina Reranker v3.5 scored the
complete 60-document list separately for each view.

The private workload was:

```text
2,080 questions × 60 documents × 6 views = 748,800 scores
```

Passages and scores were checkpointed in SQLite at `(query, document, view)`
granularity. The run was split into 694/693/693-query shards across three GPUs
and merged only after validating 2,080 queries, 12,480 completed query-view
calls, 748,800 passages, 748,800 scores and artifact hashes.

## 7. Calibrated hard-negative Top-20

The next stage only reordered the stable Top-30; membership beyond that
boundary remained frozen.

For every Top-60 document it assembled:

- stable and original retrieval positions;
- 12 calibrated FT-BGE/Vietnamese score signals (full document, three
  sections and dense-window aggregates);
- six Jina raw scores, normalized scores, ranks and boundary gaps;
- cross-view agreement and vote aggregates.

Small logistic and regularized LightGBM classifiers estimated relevance on
the Top-30. Their probabilities were sigmoid-calibrated using folds composed
only from the training side of each outer split. A blend of stable-rank
percentile and calibrated relevance percentile reranked the Top-30.

For deployment, five frozen outer-fold policies generated private rankings;
their mean ranks formed the consensus. This stage improved CAL512 Top-20 from
**613 to 616** gold hits while keeping Top-30 and Top-60 membership unchanged.

## 8. Constrained-score Top-5

The final learned selector did not search the whole Top-60. It created 18
experts (12 native score experts plus six Jina views), then learned a
query-level router from label-free agreement and score-distribution features.
Two Ridge heads predicted each expert's possible gain and loss. The router
computed `predicted_gain - loss_weight × predicted_loss`, selected a small
expert subset and fused it with an anchored RRF.

Five frozen router members produced a private consensus guide. The final five
were simply the guide's first five documents that belonged to the calibrated
Hard Top-20. The remaining Hard Top-20 documents stayed in hard-rank order, so
the stage could improve Top-5 without changing Top-20 membership.

On CAL512 this raised Top-5 from **466 to 475** gold hits while Hard Top-20
remained at 616.

## 9. Exact-overlap protection

As the last deterministic rule, private questions were normalized with NFKC,
case-folding, punctuation removal and whitespace collapse. For an exact match
against an already labelled train or warmup question, its known relevant
documents were protected in Top-5. A missing protected document replaced the
lowest-ranked unprotected Top-5 item.

The audit covered 109 exact questions and 119 known relevant documents; all
119 were present after the rule. Semantic-neighbor transfer was examined but
was not treated as equivalent to exact matching.

## 10. Evaluation and deployment safeguards

The final policy had to reproduce the following CAL512 identity before private
inference:

| Checkpoint | Gold hits |
|---|---:|
| Stable Top-5 | 466 |
| Stable Top-20 | 613 |
| Hard-negative Top-20 | 616 |
| Constrained-score Top-5 | 475 |
| Stable Top-60 | 686 |

In addition to raw recall, experiments tracked weighted recall, zero-hit
queries, gained/lost gold cases, outer-fold deltas and query bootstrap
intervals. Private inference was label-free except for the explicit,
pre-audited exact-overlap memory rule. Artifacts carried row counts, schemas,
upstream paths, label-usage flags and SHA-256 identities.

The recorded private leaderboard outcome was **0.9428** on the 2,080-question
held-out set. It is not independently reproducible from this public repository
because the evaluator and labels are unavailable. The benchmark metric averages
per-question Recall; Precision is the secondary tie-break metric. Predictions
are capped at five unique document IDs per question.

## Evidence still needed

The remaining upstream source gap is listed in
[source_gaps.md](source_gaps.md). Until it is supplied, the repository makes
no claim about why the initial 7,000-question file was reduced to 6,985 rows.
The subsequent 6,985-to-4,823 encoder-training split is fully recorded above.
