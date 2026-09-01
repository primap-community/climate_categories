.PHONY: docs help virtual-environment install-pre-commit update-venv cache recache test test-full lint coverage update-citation
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

lint: ## check style with pre-commit hooks
	uv run pre-commit run --all-files

test: ## run tests quickly with the default Python
	uv run --extra test pytest -rx

test-all: ## run tests on every Python version with tox
	uv run tox -p

coverage: ## check code coverage quickly with the default Python
	uv run coverage run --source climate_categories -m pytest -rx
	uv run coverage report -m
	uv run coverage html
	ls htmlcov/index.html

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-docs: ## Remove generated parts of documentation, then build docs
	uv run --group docs $(MAKE) -C docs clean
	uv run --group docs $(MAKE) -C docs html

docs: ## generate Sphinx HTML documentation, including API docs
	uv run --group docs $(MAKE) -C docs html

dist: clean-build ## builds source and wheel package
	uv build

install: ## install the package into the active virtual environment
	uv pip install .

virtual-environment: ## setup a virtual environment for development
	uv sync --all-groups --extra test

update-venv: ## update all packages in the development environment
	uv sync --upgrade --all-groups --extra test

install-pre-commit: virtual-environment ## install the pre-commit hooks
	uv run pre-commit install

cache: climate_categories/data/RCMIP.py
cache: climate_categories/data/GCB.py
cache: climate_categories/data/IPCC2006.py
cache: climate_categories/data/IPCC2006_PRIMAP.py
cache: climate_categories/data/IPCC1996.py
cache: climate_categories/data/CRF1999.py
cache: climate_categories/data/CRF2013.py
cache: climate_categories/data/CRF2013_2021.py
cache: climate_categories/data/CRF2013_2022.py
cache: climate_categories/data/CRF2013_2023.py
cache: climate_categories/data/gas.py
cache: climate_categories/data/CRFDI.py
cache: climate_categories/data/CRFDI_class.py
cache: climate_categories/data/ISO3.py
cache: climate_categories/data/ISO3_GCAM.py
cache: climate_categories/data/BURDI.py
cache: climate_categories/data/BURDI_class.py
cache: climate_categories/data/CT.py
cache: climate_categories/data/FAO.py  ## Generate Python specs from YAML files

data: climate_categories/data/BURDI_class.yaml
data: climate_categories/data/BURDI.yaml
data: climate_categories/data/CRF1999.yaml
data: climate_categories/data/CRF2013_2021.yaml
data: climate_categories/data/CRF2013_2022.yaml
data: climate_categories/data/CRF2013_2023.yaml
data: climate_categories/data/CRF2013.yaml
data: climate_categories/data/CRFDI_class.yaml
data: climate_categories/data/CRFDI.yaml
data: climate_categories/data/gas.yaml
data: climate_categories/data/IPCC1996.yaml
data: climate_categories/data/IPCC2006_PRIMAP.yaml
data: climate_categories/data/IPCC2006.yaml
data: climate_categories/data/ISO3_GCAM.yaml
data: climate_categories/data/ISO3.yaml
data: climate_categories/data/RCMIP.yaml
data: climate_categories/data/CT.yaml
data: climate_categories/data/FAO.yaml  ## Generate data files


climate_categories/data/%.yaml: data_generation/%.py data_generation/utils.py
	uv run --group data-generation python $<

climate_categories/data/%.py: climate_categories/data/%.yaml data_generation/convert_yaml_to_python.py
	uv run python data_generation/convert_yaml_to_python.py $<

# Unlike `cache`, this ignores timestamps and picks up new YAML files by itself, so it
# cannot silently skip anything. A fresh git checkout gives every file the same mtime,
# which make reads as "up to date", so CI and the release have to use this target.
recache:  ## Regenerate all Python specs from the YAML files, unconditionally
	uv run python data_generation/convert_yaml_to_python.py climate_categories/data/*.yaml

.PHONY: README.rst
README.rst:  ## Update the citation information from zenodo
	uv run --with requests --no-project python update_citation_info.py
