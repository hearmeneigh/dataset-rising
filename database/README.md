# Database

## Setting Up
1. `./start-mongodb.sh`
2. `python3 create_database.py`

The database is set up with user `root` and password `root`.
You can change this by setting `DB_USERNAME` and `DB_PASSWORD` environment variables.

The script uses database name `e621_rising` by default. You can change this by setting `DB_NAME` environment variable.

## Shutting Down
1. `./stop-mongodb.sh`
