# Remaining source gap

The corpus schema, benchmark metric, three-level chunker, encoder-training
split and all ranking stages are recoverable from preserved source. One
earlier upstream transformation is still not proven by the files currently
available.

## Needed from the original project

1. **Raw-to-clean training script or report**
   - input query count;
   - duplicate/near-duplicate removal;
   - invalid or missing-label filtering;
   - why 7,000 raw labelled questions became 6,985 retrieval questions.

The 4,823-row encoder subset is no longer a source gap. Its preserved manifest
records 6,985 labelled rows, a fixed 2,155-query evaluation table, 4,830
non-evaluation rows, and removal of seven normalized exact-question collisions:
`6,985 - 2,155 - 7 = 4,823`.

The useful missing artifact is the original query-cleaning notebook, script or
manifest. Restricted question text is not required for this public repository.
