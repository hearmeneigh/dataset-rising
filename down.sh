#!/bin/sh -e

source venv/bin/activate

cd database
python3 down.py
