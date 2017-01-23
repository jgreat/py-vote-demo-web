#!/bin/bash
. ./venv/bin/activate
exec gunicorn -c ./gunicorn.py main:app
