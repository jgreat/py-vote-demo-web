#!/bin/bash
source .venv/bin/activate
exec gunicorn -c ./gunicorn.py main:app
