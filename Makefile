ALL: help

.PHONY: help docs test tox watch

help:
	@echo 'Available commands:'
	@echo '  help  - Display this message and exists'
	@echo '  docs  - Build documentation with Sphinx'
	@echo '  lint  - Lint sources with Flake8'
	@echo '  test  - Run tests (implies linting)'
	@echo '  tox   - Run tests for all platforms with Tox'
	@echo '  watch - Start Sphinx autobuild watcher'

docs:
	make -C docs html

lint:
	pipenv run flake8 --isolated

test: lint
	pipenv run pytest

tox:
	tox

watch:
	pipenv run sphinx-autobuild docs/source docs/build/html
