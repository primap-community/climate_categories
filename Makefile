.PHONY: clean clean-test clean-pyc clean-build docs help update-venv
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

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: venv ## check style with pre-commit hooks
	venv/bin/pre-commit run --all-files

test: venv ## run tests quickly with the default Python
	venv/bin/pytest  --xdoc -rx

coverage: venv ## check code coverage quickly with the default Python
	venv/bin/coverage run --source climate_categories -m pytest
	venv/bin/coverage report -m
	venv/bin/coverage html

docs: venv ## generate Sphinx HTML documentation
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean venv ## builds source and wheel package
	venv/bin/python setup.py sdist
	venv/bin/python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

virtual-environment: venv ## setup a virtual environment for development

venv: requirements_dev.txt setup.py
	[ -d venv ] || python3 -m venv venv
	venv/bin/python -m pip install -r requirements_dev.txt
	venv/bin/python -m pip install -e .
	touch venv

update-venv:
	[ -d venv ] || python3 -m venv venv
	venv/bin/python -m pip install -r requirements_dev.txt --upgrade
	venv/bin/python -m pip install -e .
	touch venv

install-pre-commit: update-venv ## install the pre-commit hooks
	venv/bin/pre-commit install

climate_categories/data/IPCC2006.yaml: data_generation/IPCC2006.py venv
	venv/bin/python data_generation/IPCC2006.py

climate_categories/data/IPCC1996.yaml: data_generation/IPCC1996.py venv
	venv/bin/python data_generation/IPCC1996.py
