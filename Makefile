# NVIDIA full-stack deep dive — build & validation
PY ?= python3
NODE ?= node

.PHONY: help setup charts diagrams build validate validate-final stats site tco all clean

help:
	@echo "make setup      install Python + Node tooling"
	@echo "make charts     regenerate every chart from data/*.csv (+ assets/charts/CATALOG.md)"
	@echo "make diagrams   render diagrams/src/*.{d2,dot,mmd} -> assets/diagrams/*.svg"
	@echo "make tco        run the TCO model (scripts/tco)"
	@echo "make build      bibliography + glossary + link/citation normalisation + PROGRESS stats"
	@echo "make validate   citations, links, alt text + visual quotas, Mermaid render check"
	@echo "make site       assemble and build the optional MkDocs site into ./site"

setup:
	$(PY) -m pip install -r requirements.txt
	npm ci

charts:
	$(PY) scripts/charts/run_all.py

diagrams:
	bash scripts/build/render_diagrams.sh

tco:
	@if [ -f scripts/tco/tco_model.py ]; then $(PY) scripts/tco/tco_model.py; else echo "tco: model not built yet"; fi

build:
	$(PY) scripts/build/bibliography.py
	$(PY) scripts/build/glossary.py
	$(PY) scripts/build/sync_alt.py
	$(PY) scripts/build/normalize.py
	$(PY) scripts/validate/stats.py --write

stats:
	$(PY) scripts/validate/stats.py

validate:
	$(PY) scripts/validate/check_citations.py
	$(PY) scripts/validate/check_links.py
	$(PY) scripts/validate/check_visuals.py
	$(NODE) scripts/validate/mermaid_check.mjs

validate-final: validate
	$(PY) scripts/validate/check_visuals.py --final --quiet

site:
	$(PY) scripts/build/site.py
	mkdocs build -f mkdocs.yml --strict || mkdocs build -f mkdocs.yml

all: charts diagrams build validate

clean:
	rm -rf site .site_src
