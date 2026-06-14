# Task 04 — Group-and-sum transform
## Category: data-transform
## Language: python
## Requirement
Create `transform.py` with `group_sum(rows, key, value)` that takes a list of dicts and returns a dict
mapping each distinct `row[key]` to the sum of `row[value]` for that group. Order of keys does not
matter.
## Done when
- `test_transform.py` exists and passes under `pytest`.
- `group_sum([{"c":"a","n":1},{"c":"b","n":2},{"c":"a","n":3}], "c", "n")` returns `{"a":4, "b":2}`.
- An empty input returns `{}`.
