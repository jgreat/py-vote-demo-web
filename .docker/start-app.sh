#!/bin/bash

exec /usr/local/bin/gunicorn -c ./gunicorn.py main:app
