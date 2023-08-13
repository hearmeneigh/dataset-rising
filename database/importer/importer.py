import json
import pymongo.errors

from pymongo.database import Database

from database.translator.translator import PostTranslator
from database.utils.progress import Progress


class Importer:
    def __init__(self, db: Database, collection: str, translator: PostTranslator):
        self.translator = translator
        self.db = db
        self.collection = collection
        self.progress = Progress(title='Importing posts')

    def import_jsonl(self, input_file: str):
        collection = self.db[self.collection]

        cur_line = 0
        mongo_errors = 0
        json_errors = 0

        with open(input_file, 'rt') as fp:
            for line in fp:
                cur_line += 1
                self.progress.update(cur_line)

                try:
                    data = json.loads(line)
                except Exception as e:
                    json_errors += 1
                    print(f'Invalid JSON found on line #{cur_line} of {input_file}: {e}')
                    continue

                record = self.translator.translate(data)

                try:
                    collection.replace_one({
                        'source': record.source,
                        'source_id': record.source_id
                    }, vars(record), upsert=True)
                except pymongo.errors.PyMongoError as e:
                    mongo_errors += 1
                    print(f'Could not import record on line #{cur_line} of {input_file}: {e}')
                    continue

        return cur_line, mongo_errors, json_errors
