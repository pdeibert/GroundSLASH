#!/bin/bash
isort . --check-only --profile black --skip ground_slash/antlr/
black . --check --extend-exclude ground_slash/antlr/