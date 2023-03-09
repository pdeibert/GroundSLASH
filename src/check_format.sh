#!/bin/bash
isort . --check-only --profile black --skip aspy/antlr/
black . --check --extend-exclude aspy/antlr/