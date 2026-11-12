# CV / résumé bullets

## English

- Built an end-to-end Vietnamese legal retrieval system combining 11-signal
  reciprocal-rank fusion, LightGBM LambdaMART, fine-tuned legal embeddings,
  and six-view Jina reranking; achieved a verified private benchmark score of
  **0.9428** on 2,080 questions.
- Improved audited Recall@5 from **466/712 to 475/712 relevant documents**
  while preserving Top-20/30/60 candidate coverage through constrained
  reranking and hard-negative calibration.
- Designed a nested five-fold evaluation framework with weighted recall,
  per-fold guardrails, bootstrap uncertainty, and gain/loss case auditing to
  prevent unsafe ranking changes.
- Engineered a resumable, three-machine SQLite inference pipeline for
  **748,800 query-view-document scores**, including deterministic sharding,
  merge validation, and SHA-256 artifact lineage.
- Packaged **538 reproducibility artifacts** with checksums and restore
  verification while separating restricted data from public source.

## Tiếng Việt

- Xây dựng hệ thống truy hồi pháp luật tiếng Việt end-to-end kết hợp RRF 11
  tín hiệu, LightGBM LambdaMART, legal embedding fine-tune và Jina reranking 6
  view; đạt **0.9428 trên private benchmark** gồm 2.080 câu hỏi.
- Tăng Recall@5 kiểm định từ **466/712 lên 475/712 gold documents**, đồng thời
  giữ nguyên độ phủ Top-20/30/60 bằng hard-negative calibration và constrained
  reranking.
- Thiết kế nested 5-fold audit với weighted recall, bootstrap, guardrail từng
  fold và phân tích gain/loss để ngăn triển khai các model tăng raw recall
  nhưng làm giảm chất lượng thực tế.
- Xây dựng pipeline inference SQLite có resume, chia 3 máy và merge kiểm định
  cho **748.800 scores**, kèm SHA-256 lineage.

## Interview talking points

1. Why candidate recall and final ranking precision were optimized separately.
2. Why a +2 raw gain was rejected when weighted recall decreased.
3. How SQLite checkpoints enabled safe multi-GPU sharding and resume.
4. How exact overlap differs from unsafe semantic label transfer.
5. How artifact lineage made a complex experimental pipeline reproducible.
