.PHONY: docs help virtual-environment install-pre-commit update-venv cache test test-full lint coverage release update-citation
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

lint: venv ## check style with pre-commit hooks
	venv/bin/pre-commit run --all-files

test: venv ## run tests quickly with the default Python
	venv/bin/pytest --xdoc -rx

test-all: venv ## run tests on every Python version with tox
	venv/bin/tox -p

coverage: venv ## check code coverage quickly with the default Python
	venv/bin/coverage run --source climate_categories -m pytest --xdoc -rx
	venv/bin/coverage report -m
	venv/bin/coverage html
	ls htmlcov/index.html

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-docs: venv ## Remove generated parts of documentation, then build docs
	. venv/bin/activate ; $(MAKE) -C docs clean
	. venv/bin/activate ; $(MAKE) -C docs html

docs: venv ## generate Sphinx HTML documentation, including API docs
	. venv/bin/activate ; $(MAKE) -C docs html

release: venv dist ## package and upload a release
	venv/bin/twine upload --repository climate-categories dist/*

dist: clean-build venv ## builds source and wheel package
	# because we update the citation info after releasing on github and zenodo but
	# before building for pypi, we need to force the correct version.
	SETUPTOOLS_SCM_PRETEND_VERSION=10.0.4 venv/bin/python -m build

install: clean ## install the package to the active Python's site-packages
	python setup.py install

virtual-environment: venv ## setup a virtual environment for development

venv: setup.py pyproject.toml setup.cfg
	[ -d venv ] || python3 -m venv --system-site-packages venv
	venv/bin/python -m pip install --upgrade wheel uv
	. venv/bin/activate ; venv/bin/uv pip install --upgrade -e .[dev]
	touch venv

update-venv: ## update all packages in the development environment
	[ -d venv ] || python3 -m venv venv
	venv/bin/python -m pip install --upgrade wheel uv
	. venv/bin/activate ; venv/bin/uv pip  install --upgrade --resolution highest -e .[dev]
	touch venv

install-pre-commit: update-venv ## install the pre-commit hooks
	venv/bin/pre-commit install

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
cache: climate_categories/data/BURDI_class.py  ## Generate Python specs from YAML files

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
data: climate_categories/data/RCMIP.yaml  ## Generate data files


climate_categories/data/%.yaml: data_generation/%.py data_generation/utils.py
	venv/bin/python $<

climate_categories/data/%.py: climate_categories/data/%.yaml data_generation/convert_yaml_to_python.py
	venv/bin/python data_generation/convert_yaml_to_python.py $< $@

.PHONY: README.rst
README.rst:  ## Update the citation information from zenodo
	venv/bin/python update_citation_info.py
