#!/bin/bash
isort . --profile black --skip aspy/antlr/
black . --extend-exclude aspy/antlr/