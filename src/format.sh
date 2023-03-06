#!/bin/bash
isort . --profile black --skip aspy/antlr/
black . --line-length 120 --extend-exclude aspy/antlr/