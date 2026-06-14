# Task 06 — Email-ish string validation
## Category: validation
## Language: python
## Requirement
Create `validate.py` with `is_valid(s)` returning True only when `s` looks like a basic email: a
non-empty local part, a single `@`, a domain with at least one dot, and no spaces. No external
validation library.
## Done when
- `test_validate.py` exists and passes under `pytest`.
- `"a@b.co"` → True; `"x@y.z.com"` → True.
- `"a@b"`, `"a b@c.com"`, `"@b.com"`, `"a@@b.com"`, `""` → all False.
