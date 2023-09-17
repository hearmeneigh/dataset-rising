#!/bin/sh -e

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd database
python3 up.py
python3 create_database.py
cd ..
