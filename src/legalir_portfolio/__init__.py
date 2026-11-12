"""Public-safe utilities extracted from the full LegalIR research pipeline."""

from .core import constrained_top5, reciprocal_rank_fusion
from .metrics import evaluate_ranking

__all__ = ["constrained_top5", "reciprocal_rank_fusion", "evaluate_ranking"]
