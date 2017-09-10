ALL: help

PYTHON = pipenv run python --

.PHONY: help build check clean docs lint test tox upload watch

help:
	@echo 'Available commands:'
	@echo '  help   - Display this message and exist'
	@echo '  build  - Rebuild package for PyPI publish (implies clean)'
	@echo '  check  - Check package metadata for PyPI publish'
	@echo '  clean  - Clean package artifects'
	@echo '  docs   - Build documentation with Sphinx'
	@echo '  lint   - Lint sources with Flake8'
	@echo '  test   - Run tests (implies lint)'
	@echo '  tox    - Run tests for all platforms with Tox'
	@echo '  upload - Upload package to PyPI (implies build)'

build: clean
	$(PYTHON) setup.py sdist bdist_wheel

check:
	$(PYTHON) setup.py check --restructuredtext --strict

clean:
	rm -rf build dist docs/build *.egg-info
	find . -name \*.pyc -delete
	find . -name __pycache__ -exec rm -r {} +

docs:
	$(PYTHON) -m sphinx -M html 'docs/source' 'docs/build'

lint:
	pipenv run flake8 --isolated

open: docs
	open docs/build/html/index.html

test: lint
	pipenv run pytest

tox:
	tox

upload: build
	pipenv run twine upload dist/*
