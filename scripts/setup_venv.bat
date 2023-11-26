@echo off

echo Creating venv
py -m venv .venv

echo Installing dependencies
call .venv/Scripts/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt