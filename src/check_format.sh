#!/bin/bash
isort . --check-only --profile black
black . --check