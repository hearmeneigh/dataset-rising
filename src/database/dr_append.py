import argparse
import json

from database.importer.importer import Importer
from database.tag_normalizer.util import load_normalizer_from_database
from database.translator.helpers import get_post_translator
from database.utils.db_utils import connect_to_db


def get_args():
    parser = argparse.ArgumentParser(prog='Append', description='Add posts from e621, gelbooru, rule34, and danbooru')

    parser.add_argument('-p', '--posts', type=str, action='append', help='Post JSONL file(s) to import', required=True)
    parser.add_argument('-s', '--source', type=str, help='Data source [e926, e621, gelbooru, danbooru, rule34]', required=True, choices=['e926', 'e621', 'gelbooru', 'danbooru', 'rule34'])

    return parser.parse_args()


def main():
    args = get_args()

    (db, client) = connect_to_db()

    # process tags
    tag_normalizer = load_normalizer_from_database(db)

    # process posts
    post_translator = get_post_translator(args.source, tag_normalizer, deep_tag_search=True)
    post_importer = Importer(db, 'posts', post_translator, tag_normalizer, skip_if_md5_match=True)

    for post_file in args.posts:
        post_importer.import_jsonl(post_file)

    print(json.dumps(tag_normalizer.deep_search_misses))

if __name__ == "__main__":
    main()
