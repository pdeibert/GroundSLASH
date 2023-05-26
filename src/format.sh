#!/bin/bash
isort . --profile black --skip ground_slash/antlr/
black . --extend-exclude ground_slash/antlr/