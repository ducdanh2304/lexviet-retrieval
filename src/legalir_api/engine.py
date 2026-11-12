"""A lightweight public demo engine with the same retrieval interfaces.

The research corpus and trained checkpoints are private, so the demo uses a
small synthetic corpus. The service boundary is intentionally compatible with
a dense/LambdaMART backend: replace `search()` while keeping API schemas fixed.
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

from legalir_portfolio.core import reciprocal_rank_fusion


TOKEN = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(character for character in text
                   if not unicodedata.combining(character))
    return " ".join(TOKEN.findall(text))


def tokenize(text: str) -> list[str]:
    return normalize(text).split()


class DemoRetrievalEngine:
    """BM25 demo backend plus weighted-RRF fusion endpoint support."""

    def __init__(self, corpus_path: str | Path):
        raw = json.loads(Path(corpus_path).read_text(encoding="utf-8"))
        self.documents = {str(row["id"]): row for row in raw}
        if not self.documents:
            raise ValueError("corpus is empty")
        self.term_frequencies = {
            doc_id: Counter(tokenize(row["text"]))
            for doc_id, row in self.documents.items()
        }
        self.lengths = {
            doc_id: sum(counter.values())
            for doc_id, counter in self.term_frequencies.items()
        }
        self.average_length = sum(self.lengths.values()) / len(self.lengths)
        self.document_frequency = Counter()
        for counter in self.term_frequencies.values():
            self.document_frequency.update(counter.keys())

    def _bm25(self, query: str, document: str, k1: float = 1.5,
              b: float = 0.75) -> float:
        query_terms = Counter(tokenize(query))
        frequencies = self.term_frequencies[document]
        length = self.lengths[document]
        total_documents = len(self.documents)
        score = 0.0
        for term, query_count in query_terms.items():
            frequency = frequencies.get(term, 0)
            if not frequency:
                continue
            containing = self.document_frequency[term]
            inverse_frequency = math.log(
                1.0 + (total_documents - containing + 0.5) / (containing + 0.5)
            )
            denominator = frequency + k1 * (
                1.0 - b + b * length / self.average_length
            )
            score += query_count * inverse_frequency * (
                frequency * (k1 + 1.0) / denominator
            )
        return score

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        scored = [
            (self._bm25(query, doc_id), doc_id)
            for doc_id in self.documents
        ]
        scored.sort(key=lambda row: (-row[0], row[1]))
        return [
            {
                "document_id": doc_id,
                "score": round(score, 6),
                "title": self.documents[doc_id]["title"],
                "excerpt": self.documents[doc_id]["text"],
            }
            for score, doc_id in scored[:top_k]
        ]

    @staticmethod
    def fuse(rankings: list[list[str]], weights: list[float] | None,
             limits: list[int] | None, k: float, top_k: int) -> list[str]:
        return reciprocal_rank_fusion(
            rankings, weights=weights, limits=limits, k=k
        )[:top_k]
