#!/bin/sh -e

source venv/bin/activate

cd ./src
python3 -m database.dr_db_uninstall
