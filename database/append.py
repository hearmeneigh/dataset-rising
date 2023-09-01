import argparse

from entities.tag import TagProtoEntity, TagVersion
from importer.importer import Importer
from tag_normalizer.tag_normalizer import TagNormalizer
from translator.helpers import get_post_translator, get_tag_translator
from utils.db_utils import connect_to_db
from utils.progress import Progress


parser = argparse.ArgumentParser(prog='Import', description='Import post and tag metadata from e621, gelbooru, and danbooru')

parser.add_argument('-p', '--posts', type=str, action='append', help='Post JSONL file(s) to import', required=True)
parser.add_argument('-s', '--source', type=str, help='Data source', required=True, choices=['e621', 'gelbooru', 'danbooru'])

args = parser.parse_args()

(db, client) = connect_to_db()

# process tags
tag_progress = Progress('Importing tags', 'tags')
tag_translator = get_tag_translator(args.source)
tag_normalizer = TagNormalizer()

for tag in db['tags'].find({}):
    tag_progress.update()
    tag_normalizer.add_tag(tag['preferred_name'], tag, TagVersion.V2)

tag_progress.succeed(f'{tag_progress.count} tags imported')

# process posts
post_translator = get_post_translator(args.source, tag_normalizer)
post_importer = Importer(db, 'posts', post_translator, tag_normalizer)

for post_file in args.posts:
    post_importer.import_jsonl(post_file)
