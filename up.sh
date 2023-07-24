#!/bin/sh -e

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd database
./start-mongodb.sh
python3 create_database.py
cd ..
