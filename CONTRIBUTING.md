# Contributing

Contributions are welcome for public-safe improvements to metrics, validators,
tests, and documentation.

Before opening a pull request:

1. run `python -m unittest discover -s tests -v`;
2. ensure no restricted dataset content is present;
3. do not commit model weights, score caches, submissions, or credentials;
4. report new metrics with the split, sample count, and evaluation protocol.
