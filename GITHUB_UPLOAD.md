# Publish to GitHub

## Recommended repository metadata

- **Repository name:** `legalir-vietnamese-retrieval`
- **Description:** `High-recall Vietnamese legal retrieval with 11-signal fusion, LambdaMART, six-view reranking, nested audits, and reproducible ML infrastructure.`
- **Topics:** `information-retrieval`, `learning-to-rank`, `legal-nlp`,
  `vietnamese-nlp`, `lightgbm`, `reranking`, `machine-learning`, `mlops`
- **Visibility:** Public, after completing the checklist below.

## Final public-data checklist

```bash
git status --short
git grep -n -Ei 'private-official|KAGGLE_KEY|api[_-]?key|password|token=' || true
find . -type f -size +50M -print
python -m unittest discover -s tests -v
```

Confirm that there are no private queries, labels, caches, weights,
submissions, credentials, or restricted dataset URLs.

## Create the repository locally

```bash
git init
git branch -M main
git add .
git commit -m "Publish LegalIR retrieval portfolio"
```

## Push with GitHub CLI

Replace `YOUR_GITHUB_USERNAME`:

```bash
gh repo create YOUR_GITHUB_USERNAME/legalir-vietnamese-retrieval \
  --public \
  --source . \
  --remote origin \
  --push
```

Pin the repository on the GitHub profile and add the verified private-benchmark
score, architecture, and evaluation methodology to the repository About box.

## Suggested LinkedIn/GitHub post

> Built a personal Vietnamese legal information retrieval system combining
> 11-signal candidate fusion, LambdaMART, domain-tuned embeddings, and six-view
> listwise reranking. The verified private-benchmark score was 0.9428. Beyond
> the score, I focused on rigorous nested evaluation,
> weighted-recall guardrails, resumable multi-GPU inference, and reproducible
> artifact lineage. Source and technical report: [repository link].
