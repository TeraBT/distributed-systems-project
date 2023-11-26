#!/bin/bash

echo "Creating venv"
python3 -m venv .venv

echo "Installing dependencies"
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt