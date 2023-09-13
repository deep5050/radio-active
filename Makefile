SHELL := /bin/bash
PYTHON = python3
TEST_PATH = ./tests/
FLAKE8_EXCLUDE = venv,.venv,.eggs,.tox,.git,__pycache__,*.pyc
SRC_DIR = "radioactive"
TEST_DIR = "test"

all: clean install-dev test

check:
	${PYTHON} -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude ${FLAKE8_EXCLUDE}
	${PYTHON} -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=79 --statistics --exclude ${FLAKE8_EXCLUDE}

clean:
	@find . -name '*.pyc' -exec rm --force {} +
	@find . -name '*.pyo' -exec rm --force {} +
	@find . -name '*~' -exec rm --force {} +
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -f *.sqlite
	rm -rf .cache

dist: clean
	${PYTHON} setup.py sdist bdist_wheel

deploy:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
	
test-deploy: dist
	@echo "-------------------- sending to testpypi server ------------------------"
	@twine upload -r testpypi dist/*

help:
	@echo "---------------------------- help --------------------------------------"
	@echo "    clean"
	@echo "        Remove python artifacts and build artifacts."
	@echo "    isort"
	@echo "			Sort import statements."
	@echo "    check"
	@echo "        Check style with flake8."
	@echo "    test"
	@echo "        Run pytest"

isort:
	@echo "Sorting imports..."
	isort $(SRC_DIR) $(TEST_DIR)

build:
	python3 setup.py build

install:
	pip install -e .

install-dev: install
	pip install --upgrade pip
	pip install -e .[dev]

test: 
	${PYTHON} -m pytest ${TEST_PATH}
