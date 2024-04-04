#!/bin/bash
isort . --profile black --skip ground_slash/parser/
black . --extend-exclude ground_slash/parser/