#!/bin/bash
isort . --check-only --profile black --skip ground_slash/parser/
black . --check --extend-exclude ground_slash/parser/