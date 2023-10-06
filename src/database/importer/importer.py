import json
import pymongo.errors

from pymongo.database import Database

from database.tag_normalizer.tag_normalizer import TagNormalizer
from database.translator.translator import PostTranslator
from utils.progress import Progress


class Importer:
    def __init__(self, db: Database, collection: str, translator: PostTranslator, tag_normalizer: TagNormalizer, skip_if_md5_match: bool = False):
        self.translator = translator
        self.db = db
        self.collection = collection
        self.tag_normalizer = tag_normalizer
        self.skip_if_md5_match = skip_if_md5_match

    def import_jsonl(self, input_file: str):
        progress = Progress(title='Importing posts', units='posts')
        collection = self.db[self.collection]

        cur_line = 0
        mongo_errors = 0
        json_errors = 0

        with open(input_file, 'rt') as fp:
            for line in fp:
                cur_line += 1
                progress.update(cur_line)

                try:
                    data = json.loads(line)
                except Exception as e:
                    json_errors += 1
                    print(f'Invalid JSON found on line #{cur_line} of {input_file}: {e}')
                    continue

                record = self.translator.translate(data)

                if record is None:
                    continue

                record.tags.extend(self.tag_normalizer.get_pseudo_tags(record))

                # remove duplicates
                record.tags = list(set(record.tags))

                if self.skip_if_md5_match and record.origin_md5 is not None:
                    existing_record = collection.find_one({
                        'origin_md5': record.origin_md5
                    })

                    if existing_record is not None:
                        continue

                try:
                    collection.replace_one({
                        'source': record.source,
                        'source_id': record.source_id
                    }, vars(record), upsert=True)
                except pymongo.errors.PyMongoError as e:
                    mongo_errors += 1
                    print(f'Could not import record on line #{cur_line} of {input_file}: {e}')
                    continue

        total_errors = json_errors + mongo_errors
        progress.succeed(f'{cur_line - total_errors} posts imported, {total_errors} errors')
        return cur_line, mongo_errors, json_errors
