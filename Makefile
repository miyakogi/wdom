.PHONY: release release-pypi release-github
.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	@echo "Remove build files (build/, dist/, .egg*, ...)."
	@rm -fr build/
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	@echo "Remove python files (*.py[co], __pycache__, ...)."
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	@echo "Remove test/coverage files (.coverage, htmlcov/)."
	@rm -f .coverage
	@rm -fr htmlcov/
	@rm -f wdom/tests/browser/server/tmp*.py

release: release-pypi release-github ## register pypi and push tags to github

release-pypi: ## register pypi
	python setup.py sdist upload

release-github: ## push tags to gihub
	git push origin --tags

.PHONY: green green-cov green-single unittests
green:  ## run green test
	@echo "Run green."
	@cd maint && \
	green -c ../.green ../wdom

green-cov:  # run green and calculate coverage
	@echo "Run green with coverage."
	@cd maint && \
	green -r -c ../.green ../wdom

green-single:  ## run green with a single process
	@echo "Run green with a single process."
	@cd maint && \
	green -s 1 -c ../.green ../wdom

unittest:  ## run python's unitttest
	@python -W ignore::ResourceWarning -m unittest discover wdom/tests

.PHONY: flake8
flake8:  ## run flake8 syntax check
	flake8 wdom setup.py

.PHONY: mypy
mypy:  ## run mypy type check
	mypy wdom

.PHONY: pydocstyle
pydocstyle:  ## run pydocstyle check
	pydocstyle wdom

# -n option is better but type hints refs are not found
.PHONY: docs
docs:  ## build document
	@echo "Sphinx build start."
	sphinx-build -q -E -W -b html docs docs/_build/html
	@echo "Sphinx build done."

.PHONY: sphinx
sphinx:  ## run document build server
	@echo "### Sphinx Build Server Start ###"
	@python docs/server.py

.PHONY: check
check:  ## run flake8, mypy, pydocstyle, sphinx-build
	@doit --verbosity 1 --process 4 --parallel-type thread

.PHONY: test-all
test-all: check green-cov  ## run style check and test
