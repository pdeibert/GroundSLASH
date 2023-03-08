#!/bin/bash
isort src/ --profile black --skip aspy/antlr/
black src/ --extend-exclude aspy/antlr/
