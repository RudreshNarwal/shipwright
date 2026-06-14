# Task 03 — HTTP fetch with retry
## Category: network-io
## Language: python
## Requirement
Create `fetch.py` with `fetch_json(url, retries=3, opener=None)` that performs a GET, parses the JSON
body, and retries on transient errors (connection error / 5xx) with a short backoff. A hard 4xx (e.g.
404) raises immediately without retrying. `opener` is an injectable callable used to make the request
so tests can stub it (default: real HTTP).
## Done when
- `test_fetch.py` exists and passes under `pytest`, using a stub `opener` (no real network).
- A stub that fails twice then returns `{"ok": true}` eventually succeeds and returns that dict.
- A stub raising a 404-equivalent raises and is NOT retried.
