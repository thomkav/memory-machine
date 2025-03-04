# Makefile for a generic Python project

# ONESHELL directive is needed to ensure that all commands are run in the same shell
.ONESHELL:

# If any command fails, stop the execution of the Makefile
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c # -e: fail on any error, -u: fail if variable is not set, -o pipefail: fail if any command in a pipe fails -c: run commands in a single shell

# Pre and Post steps for each target
define echo_wrapper
	@start=$$(date +%s); \
	echo "`date "+%Y-%m-%d %H:%M:%S"` ============ Running make target =============== >> $@"; \
	chmod +x scripts/*.sh > /dev/null 2>&1; \
	$1; \
	end=$$(date +%s); \
	runtime=$$((end-start)); \
	echo "`date "+%Y-%m-%d %H:%M:%S"` ------------ Completed make target ------------- >> $@ | Total Runtime: $$runtime seconds";
endef

# --------------------
# Virtual environment
# --------------------

# Python version - get from .python-version file
PYTHON_VERSION := $(shell cat .python-version)

python3:
	$(call echo_wrapper, bash scripts/install_python.sh $(PYTHON_VERSION))

.venv:
	$(call echo_wrapper, python3 -m venv .venv)

# --------------------
# Mock-Database commands
# --------------------

.PHONY: db-teardown-docker
db-teardown-docker: # Teardown the mock database using docker
	$(call echo_wrapper, bash scripts/teardown_docker_postgres_db.sh)

.PHONY: db-mock-docker
db-mock-docker: db-teardown-docker # Mock the database using docker
	$(call echo_wrapper, bash scripts/setup_docker_postgres_db.sh)

# --------------------
# Dependencies
# --------------------

.PHONY: install-coreutils
install-coreutils:
	$(call echo_wrapper, bash scripts/install_coreutils.sh)

.PHONY: install-dependencies
install-dependencies: .venv requirements.txt requirements-dev.txt # Install Python dependencies 
	$(call echo_wrapper, bash scripts/install_dependencies.sh)

.PHONY: install-git-hooks
install-git-hooks: # Install git hooks
	$(call echo_wrapper, git config --unset-all core.hooksPath || true)
	$(call echo_wrapper, pip install pre-commit --quiet)
	$(call echo_wrapper, pre-commit install)

.PHONY: install
install: install-dependencies install-git-hooks install-coreutils # Install all dependencies
	$(call echo_wrapper, echo "Dependencies installed successfully")

# --------------------
# Development
# --------------------

.PHONY: check-aws-sso-session
check-aws-sso-session: # Check if AWS SSO session is valid
	$(call echo_wrapper, bash scripts/check_aws_sso_session.sh)

.PHONY: deploy-dev
deploy-dev: # Deploy the project to dev environment
	$(call echo_wrapper, sh scripts/deploy_dev.sh)

# --------------------
# Testing
# --------------------

.PHONY: anonymize-fixtures
anonymize-fixtures: # Anonymize fixtures
	$(call echo_wrapper, bash scripts/anonymize_fixtures.sh)

.PHONY: unit-tests
unit-tests: db-mock-docker # Run unit tests
	$(call echo_wrapper, bash scripts/run_unit_tests.sh)
	make db-teardown-docker

.PHONY: db-tests
db-tests: db-mock-docker # Run database tests
	@echo "Database tests are not implemented yet - but mock database was setup successfully"
	make db-teardown-docker

.PHONY: download-unit-test-fixtures
download-unit-test-fixtures: check-aws-sso-session # Download unit test fixtures
	$(call echo_wrapper, bash scripts/download_unit_test_fixtures.sh)

.PHONY: update-remote-unit-test-fixtures
update-remote-unit-test-fixtures: check-aws-sso-session # Update remote unit test fixtures (S3)
	$(call echo_wrapper, bash scripts/update_remote_unit_test_fixtures.sh)

.PHONY: test
test: unit-tests db-tests update-unit-test-fixtures # Run all tests
	$(call echo_wrapper, echo "All tests passed successfully")

# --------------------
# Database commands
# --------------------

.PHONY: db-migrate-schema
db-migrate-schema:
	$(call echo_wrapper, bash scripts/run_db_migrations.sh)

.PHONY: clean-db-local
clean-db-local:
	$(call echo_wrapper, bash scripts/clean_db_local_docker_db.sh)

.PHONY: clean-db-catalyst-staging
clean-db-catalyst-staging:
	$(call echo_wrapper, bash scripts/clean_db_catalyst_staging_only.sh)

.PHONY: remigrate-schema-local
remigrate-schema-local: clean-local-db db-migrate-schema
	$(call echo_wrapper, echo "Schema remigrated successfully")

# --------------------
# Deployment
# --------------------

.PHONY: deploy
deploy: # Deploy the project
	$(call echo_wrapper, sh scripts/deploy.sh)

# --------------------
# Cleaning commands
# --------------------

.PHONY: clean-logs
clean-logs:
	$(call echo_wrapper, rm -rf logs/)

.PHONY: clean-pyc
clean-pyc:
	$(call echo_wrapper, find . -name '*.pyc' -exec rm -f {} +)
	$(call echo_wrapper, find . -name '*.pyo' -exec rm -f {} +)
	$(call echo_wrapper, find . -name '__pycache__' -exec rm -rf {} +)

.PHONY: clean-test
clean-test:
	$(call echo_wrapper, rm -rf .pytest_cache/)
	$(call echo_wrapper, rm -f .coverage)
	$(call echo_wrapper, rm -rf htmlcov/)

.PHONY: clean
clean: clean-pyc clean-test clean-logs # Clean the project
	$(call echo_wrapper, rm -rf .venv)

# --------------------
# Help
# --------------------

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# --------------------
# Required targets by Makefile linter
# --------------------

.PHONY: all
all: help

.DEFAULT_GOAL := help