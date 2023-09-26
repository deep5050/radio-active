SHELL := /bin/bash
PYTHON = python3
TEST_PATH = ./tests/
FLAKE8_EXCLUDE = venv,.venv,.eggs,.tox,.git,__pycache__,*.pyc,build
SRC_DIR = "radioactive"
TEST_DIR = "test"

.PHONY: all clean isort check dist deploy test-deploy help build install install-dev test
all: clean format check build install

check:
	@echo "Chceking linting errors......."
	${PYTHON} -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude ${FLAKE8_EXCLUDE}
	${PYTHON} -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=79 --statistics --exclude ${FLAKE8_EXCLUDE}

clean:
	@echo "Cleaning build artifacts......"
	@find . -name '*.pyc' -exec rm --force {} +
	@find . -name '*.pyo' -exec rm --force {} +
	@find . -name '*~' -exec rm --force {} +
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -f *.sqlite
	rm -rf .cache
	rm -rf *.mp3

dist: clean
	${PYTHON} setup.py sdist bdist_wheel

deploy: dist
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

test-deploy: dist
	@echo "Sending to testpypi server......."
	@twine upload -r testpypi dist/*

help:
	@echo "help............."
	@echo "    clean"
	@echo "        Remove python artifacts and build artifacts."
	@echo "    isort"
	@echo "			Sort import statements."
	@echo "    build"
	@echo "         Build the target app"
	@echo "   install"
	@echo "        Install the target app"
	@echo "    check"
	@echo "        Check style with flake8."
	@echo "    test"
	@echo "        Run pytest"
	@echo "    todo"
	@echo "        Finding lines with 'TODO'"

isort:
	@echo "Sorting imports....."
	isort $(SRC_DIR) $(TEST_DIR)

build: format
	@echo "Building........."
	${PYTHON} setup.py build

install: build
	@echo "Installing........."
	pip install -e .

install-dev: install
	pip install --upgrade pip
	pip install -e .[dev]

test:
	${PYTHON} -m pytest ${TEST_PATH}

todo:
	@echo "Finding lines with 'TODO:' in current directory..."
	@grep -rn 'TODO:' ./radioactive

format:
	@echo "Formatting files using black..........."
	${PYTHON} -m black setup.py
	${PYTHON} -m black radioactive/*
