ALL: help

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
	pipenv run python setup.py sdist bdist_wheel

check:
	pipenv run python setup.py check --restructuredtext --strict

clean:
	rm -rf build dist *.egg-info
	find . -name \*.pyc -delete
	find . -name __pycache__ -exec rm -r {} +

docs:
	make -C docs html

lint:
	pipenv run flake8 --isolated

open:
	open docs/build/html/index.html

test: lint
	pipenv run pytest

tox:
	tox

upload: build
	pipenv run twine upload dist/*
