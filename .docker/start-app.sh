#!/bin/bash
exec gunicorn -c ./gunicorn.py main:app
