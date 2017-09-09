ALL: help

.PHONY: help build check clean docs lint test tox upload watch

help:
	@echo 'Available commands:'
	@echo '  help  - Display this message and exist'
	@echo '  check - Check package metadata for PyPI publish'
	@echo '  docs  - Build documentation with Sphinx'
	@echo '  lint  - Lint sources with Flake8'
	@echo '  test  - Run tests (implies linting)'
	@echo '  tox   - Run tests for all platforms with Tox'
	@echo '  watch - Start Sphinx autobuild watcher'

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

test: lint
	pipenv run pytest

tox:
	tox

upload: build
	pipenv run twine upload dist/*

# This requires sphinx-autobuild. It is not listed in the Pipfile because
# PyPy3 does not like it and causes CI to fail. :(
watch:
	pipenv run sphinx-autobuild docs/source docs/build/html
