#!/usr/bin/env python3
"""Dependency-free latency smoke benchmark for a running API."""

from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000/v1/retrieve")
    parser.add_argument("--requests", type=int, default=100)
    args = parser.parse_args()
    body = json.dumps({"query": "thủ tục thay đổi họ tên", "top_k": 5}).encode()
    latency = []
    for _ in range(args.requests):
        request = urllib.request.Request(
            args.url, data=body, headers={"Content-Type": "application/json"}
        )
        started = time.perf_counter()
        with urllib.request.urlopen(request) as response:
            if response.status != 200:
                raise RuntimeError(response.status)
            response.read()
        latency.append((time.perf_counter() - started) * 1000.0)
    latency.sort()
    print(json.dumps({
        "requests": len(latency),
        "mean_ms": round(statistics.mean(latency), 3),
        "p50_ms": round(latency[len(latency) // 2], 3),
        "p95_ms": round(latency[int(len(latency) * .95) - 1], 3),
        "max_ms": round(max(latency), 3),
    }, indent=2))


if __name__ == "__main__":
    main()
