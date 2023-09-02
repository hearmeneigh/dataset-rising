import argparse

from importer.importer import Importer
from tag_normalizer.util import load_normalizer_from_database
from translator.helpers import get_post_translator, get_tag_translator
from utils.db_utils import connect_to_db


parser = argparse.ArgumentParser(prog='Import', description='Import post and tag metadata from e621, gelbooru, and danbooru')

parser.add_argument('-p', '--posts', type=str, action='append', help='Post JSONL file(s) to import', required=True)
parser.add_argument('-s', '--source', type=str, help='Data source', required=True, choices=['e621', 'gelbooru', 'danbooru'])

args = parser.parse_args()

(db, client) = connect_to_db()

# process tags
tag_normalizer = load_normalizer_from_database(db)
tag_translator = get_tag_translator(args.source)

# process posts
post_translator = get_post_translator(args.source, tag_normalizer)
post_importer = Importer(db, 'posts', post_translator, tag_normalizer)

for post_file in args.posts:
    post_importer.import_jsonl(post_file)
