#!/bin/sh -e

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ./src
python3 -m database.dr_db_up
python3 -m database.dr_db_create
cd ..
