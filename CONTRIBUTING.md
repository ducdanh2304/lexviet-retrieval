# Contributing

Contributions are welcome for public-safe improvements to metrics, validators,
tests, and documentation.

Before opening a pull request:

1. install `python -m pip install -e ".[api,test]"`;
2. run `pytest -q`;
3. ensure no restricted dataset content is present;
4. do not commit model weights, score caches, submissions, or credentials;
5. report new metrics with the split, sample count, and evaluation protocol.
