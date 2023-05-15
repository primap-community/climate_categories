.PHONY: clean docs help update-venv cache test test-full lint coverage release update-citation
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

test-all: venv ## run tests with all Python versions; needs python versions already set up
	tox -p

coverage: venv ## check code coverage quickly with the default Python
	venv/bin/coverage run --source climate_categories -m pytest --xdoc -rx
	venv/bin/coverage report -m
	venv/bin/coverage html

docs: venv ## generate Sphinx HTML documentation
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

clean: ## clean up after dist
	rm -rf dist/
	rm -rf climate_categories.egg-info/
	rm -rf build/

update-citation: ## Update the citation information from zenodo
	venv/bin/python update_citation_info.py
	git commit -am 'Update citation information from zenodo.'

release: dist ## package and upload a release
	venv/bin/twine upload --repository climate-categories dist/*

dist: clean venv ## builds source and wheel package
	venv/bin/python -m build
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

virtual-environment: venv ## setup a virtual environment for development

venv: setup.py pyproject.toml setup.cfg
	[ -d venv ] || python3 -m venv venv
	venv/bin/python -m pip install -e .[dev]
	touch venv

update-venv:
	[ -d venv ] || python3 -m venv venv
	venv/bin/python -m pip install --upgrade pip wheel
	venv/bin/python -m pip install --upgrade --upgrade-strategy eager -e .[dev]
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
cache: climate_categories/data/BURDI.py
cache: climate_categories/data/BURDI_class.py  ## Generate Python specs from YAML files

climate_categories/data/%.yaml: data_generation/%.py data_generation/utils.py
	venv/bin/python $<

climate_categories/data/%.py: climate_categories/data/%.yaml data_generation/convert_yaml_to_python.py
	venv/bin/python data_generation/convert_yaml_to_python.py $< $@

README.rst:  CHANGELOG.rst .changelog_latest_version.rst  ## Update the citation information from zenodo
	venv/bin/python update_citation_info.py
