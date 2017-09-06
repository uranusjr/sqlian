ALL: help

.PHONY: help test tox

help:
	@echo 'Available commands:'
	@echo '  help - Display this message and exists'
	@echo '  test - Run tests'
	@echo '  tox  - Run tests for all platforms with Tox'

test:
	pipenv run flake8 --isolated
	pipenv run pytest

tox:
	tox
