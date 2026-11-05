# QA log

Every issue found by validation, editorial review or the independent QA pass (Phase 9) is logged
here with its resolution. Newest first.

| Date | Phase | Area / file | Issue | Severity | Resolution | Status |
|---|---|---|---|---|---|---|
| 2026-11-05 | 0 | assets/charts (style.py) | `$` in chart titles was parsed as matplotlib mathtext (italic garble) | Medium | Disabled `text.parse_math` globally in `style.py` | Fixed |
| 2026-11-05 | 0 | git remote | Tag pushes return HTTP 403 from the session's git proxy (branch pushes work) | Low | Tags created locally; SHAs recorded in PROGRESS.md; owner can push tags with `git push origin --tags` | Open (environment) |
