# Portfolio audit report

## Scope

The repository was reviewed against the preserved source reports, public code,
configuration, tests, Docker setup, and documentation. Claims were retained
only when supported by code or aggregate report evidence.

## Changes made

- separated the private research pipeline from the synthetic FastAPI demo;
- replaced the README with a shorter evidence-first project narrative;
- added an offline/batch-inference architecture diagram and artifact lineage;
- added a sanitized CAL512 metrics manifest with source-report SHA-256 hashes;
- downgraded `0.9428` from a reproducible benchmark claim to a reported private
  leaderboard outcome;
- corrected setup and test commands to use the package extras in `pyproject`;
- documented exactly which components are public and which require authorized
  private artifacts;
- removed obsolete repository-upload and role-specific application notes;
- added tests for the sanitized metrics artifact and updated citation metadata.

## Verified checks

- package installation from `pyproject.toml`;
- unit and API smoke tests;
- public metrics artifact schema and internal arithmetic;
- README relative links;
- root redirect, health handler, BM25 retrieval, and RRF fusion;
- no restricted benchmark files or large model/cache artifacts tracked by Git.

## Important limitation

The public repository is not a one-command reproduction of the competition
system. It is a public-safe engineering case study with runnable core utilities
and a synthetic service demo. Rebuilding the reported research funnel requires
the restricted dataset, trained checkpoints, retrieval caches, Jina SQLite,
and frozen fold policies.
