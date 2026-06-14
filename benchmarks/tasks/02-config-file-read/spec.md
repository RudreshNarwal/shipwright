# Task 02 — Config file read
## Category: config-io
## Language: python
## Requirement
Create `config.py` with `load(path)` that reads a JSON config file and returns a dict, applying these
defaults for missing keys: `{"host": "localhost", "port": 8080, "debug": false}`. Values present in the
file override the defaults.
## Done when
- `test_config.py` exists and passes under `pytest`.
- Loading a file containing `{"port": 9000}` returns host="localhost", port=9000, debug=False.
- Loading an empty `{}` returns all three defaults.
