# Changelog

## v1.0 — 2026-11-05

First complete release. As-of date for data and charts: 2026-11-05.

- 12 stack layers (02–13), 5 primers, the flywheel chapter, 6 cross-cutting chapters (14–19, chapter 15 in
  11 pages), 7 case studies, executive summary, README and cheat sheet — ~221k words.
- 357 charts generated from 100+ CSVs in `data/` (`make charts`); 220 Mermaid diagrams; 15 D2/Graphviz diagrams;
  1,082 counted visuals; 1,757 registered sources.
- Transparent TCO model in `scripts/tco/` (`make tco`).
- Validation (`make validate`): citations, 30k+ links and anchors, alt text and visual quotas, Mermaid render.
- Independent QA (Phase 9): 89 numerical claims spot-checked; AMD MI455X HBM4 bandwidth corrected to 23.3 TB/s
  across the repo; chart, roadmap, glossary and consistency fixes — see `QA_LOG.md` and `docs/qa/`.
- Known limitations: 811 data rows flagged for re-verification (`docs/VERIFY_QUEUE.md`); GTC DC (2026-12-01)
  and NVIDIA Q3 FY2027 results (2026-11-17) fall after the as-of date.
