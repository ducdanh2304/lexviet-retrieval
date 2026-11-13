from __future__ import annotations

import os
import threading
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from .engine import DemoRetrievalEngine
from .schemas import FuseRequest, FuseResponse, RetrieveRequest, RetrieveResponse


DEFAULT_CORPUS = Path(__file__).resolve().parents[2] / "data" / "demo_corpus.json"
engine = DemoRetrievalEngine(os.getenv("LEGALIR_CORPUS", str(DEFAULT_CORPUS)))

app = FastAPI(
    title="LexViet Retrieval API",
    version="0.1.0",
    description=(
        "Public API demo for LexViet — Vietnamese Legal Retrieval. "
        "The full research backend is replaced by a synthetic BM25 corpus."
    ),
)

_lock = threading.Lock()
_metrics = {"requests": 0, "errors": 0, "latency_ms_total": 0.0}


@app.middleware("http")
async def observe_requests(request: Request, call_next):
    started = time.perf_counter()
    try:
        response = await call_next(request)
        if response.status_code >= 400:
            with _lock:
                _metrics["errors"] += 1
        return response
    except Exception:
        with _lock:
            _metrics["errors"] += 1
        raise
    finally:
        elapsed = (time.perf_counter() - started) * 1000.0
        with _lock:
            _metrics["requests"] += 1
            _metrics["latency_ms_total"] += elapsed


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok", "documents": len(engine.documents)}


@app.get("/metrics")
def metrics():
    with _lock:
        snapshot = dict(_metrics)
    requests = int(snapshot["requests"])
    return {
        **snapshot,
        "average_latency_ms": (
            snapshot["latency_ms_total"] / requests if requests else 0.0
        ),
    }


@app.post("/v1/retrieve", response_model=RetrieveResponse)
def retrieve(payload: RetrieveRequest):
    started = time.perf_counter()
    hits = engine.search(payload.query, payload.top_k)
    return RetrieveResponse(
        query=payload.query,
        hits=hits,
        latency_ms=round((time.perf_counter() - started) * 1000.0, 3),
    )


@app.post("/v1/fuse", response_model=FuseResponse)
def fuse(payload: FuseRequest):
    if payload.weights is not None and len(payload.weights) != len(payload.rankings):
        raise ValueError("weights must match the number of rankings")
    if payload.limits is not None and len(payload.limits) != len(payload.rankings):
        raise ValueError("limits must match the number of rankings")
    documents = engine.fuse(
        payload.rankings, payload.weights, payload.limits,
        payload.rrf_k, payload.top_k,
    )
    return FuseResponse(documents=documents)
