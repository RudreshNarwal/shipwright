# Task 01 — CLI argument parsing
## Category: cli
## Language: python
## Requirement
Create `app.py` exposing a function `parse(argv)` that parses a CLI with: a required positional
`path`, an optional `--count N` (int, default 1), and a `--verbose` flag. It returns an object/namespace
with `.path`, `.count`, `.verbose`.
## Done when
- `test_app.py` exists and passes under `pytest`.
- Parsing `["x", "--count", "3", "--verbose"]` gives path="x", count=3, verbose=True.
- Parsing `["x"]` gives count=1, verbose=False.
