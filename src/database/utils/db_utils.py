from pymongo import MongoClient
import os


def connect_to_db(
    username=os.environ.get('DB_USERNAME', 'root'),
    password=os.environ.get('DB_PASSWORD', 'root'),
    db_name=os.environ.get('DB_DATABASE', 'dataset_rising'),
    host=os.environ.get('DB_HOST', 'localhost'),
    port=os.environ.get('DB_PORT', 27017)
):
    client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}')
    db = client[db_name]

    return db, client
