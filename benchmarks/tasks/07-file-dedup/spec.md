# Task 07 — Find duplicate files by content
## Category: file-io
## Language: python
## Requirement
Create `dedup.py` with `find_duplicates(root)` that walks a directory tree and returns a list of
groups, where each group is a list of file paths whose contents are byte-identical. Files with unique
contents are not included. No external dependency.
## Done when
- `test_dedup.py` exists and passes under `pytest`, using a `tmp_path` fixture to create files.
- Two files with identical bytes appear together in one group.
- A file with unique content appears in no group.
