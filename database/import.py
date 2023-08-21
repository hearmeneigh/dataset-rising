# import \
#   --input posts.json \
#   --tags tags.json \
#   --source e621 \
#   --prefilter prefilter.yaml \
#   --aspect-ratios aspect_ratios.yaml \
#   --symbols symbols.yaml \
#   --save-tags \
#   --remove-old

import argparse
import json
from typing import Optional, TextIO

from entities.tag import TagEntity, TagProtoEntity
from importer.importer import Importer
from tag_normalizer.tag_normalizer import TagNormalizer
from translator.helpers import get_post_translator, get_tag_translator
from utils.db_utils import connect_to_db
from utils.load_yaml import load_yaml
from utils.progress import Progress

parser = argparse.ArgumentParser(prog='Import', description='Import index and metadata from e621, gelbooru, and danbooru')

parser.add_argument('-p', '--posts', type=str, action='append', help='Post JSONL file(s) to import', required=True)
parser.add_argument('-t', '--tags', type=str, help='Tag JSON file(s)', required=True, action='append')
parser.add_argument('-s', '--source', type=str, help='Data source', required=True, choices=['e621', 'gelbooru', 'danbooru'])
parser.add_argument('--tag-version', type=str, help='Preferred tag format version', required=False, default='v2', choices=['v0', 'v1', 'v2'])
parser.add_argument('--prefilter', type=str, help='Prefilter YAML file', required=False, default='../examples/tag_normalizer/prefilter.yaml')
parser.add_argument('--rewrites', type=str, help='Rewritten tags YAML file', required=False, default='../examples/tag_normalizer/rewrites.yaml')
parser.add_argument('--aspect-ratios', type=str, help='Aspect ratios YAML file', required=False, default='../examples/tag_normalizer/aspect_ratios.yaml')
parser.add_argument('--symbols', type=str, help='Symbols YAML file', required=False, default='../examples/tag_normalizer/symbols.yaml')
parser.add_argument('--skip-save-tags', help='Do not save tags to the database', default=False, action='store_true')
parser.add_argument('--remove-old', help='Remove all data from the database before importing', default=False, action='store_true')

args = parser.parse_args()

# initialize
aspect_ratios = load_yaml(args.aspect_ratios).get('tags', [])
symbols = load_yaml(args.symbols).get('tags', [])
prefilter = {key: True for key in load_yaml(args.prefilter).get('tags', [])}
rewrites = {tag['from']: tag['to'] for tag in load_yaml(args.rewrites).get('tags', [])}

(db, client) = connect_to_db()

# clean database?
if args.remove_old:
    progress = Progress('Cleaning database', 'collections')

    for collection in ['posts', 'tags', 'implications']:
        progress.update()
        db[collection].delete_many()

    progress.succeed('Database cleaned')

# process tags
tag_translator = get_tag_translator(args.source)
tag_normalizer = TagNormalizer(prefilter=prefilter, symbols=symbols, aspect_ratios=aspect_ratios, rewrites=rewrites)
save_tag_count = 0


def stream_tag(tp: TextIO) -> Optional[TagProtoEntity]:
    line = tp.readline()

    if line is None or line == '':
        return None

    data = json.loads(line)

    return tag_translator.translate(data)


for tag_file in args.tags:
    tp = open(tag_file, 'rt')
    tag_normalizer.load(lambda: stream_tag(tp))

tag_normalizer.normalize(args.tag_version)


def save_tag(tag: TagEntity):
    save_tags_progress.update()
    db['tags'].replace_one({'source': tag.source, 'source_id': tag.source_id}, vars(tag), upsert=True)


if not args.skip_save_tags:
    save_tags_progress = Progress(title='Saving tags', units='tags')
    tag_normalizer.save(lambda tag: save_tag(tag))
    save_tags_progress.succeed('Tags saved')


# process posts
post_translator = get_post_translator(args.source, tag_normalizer)
post_importer = Importer(db, 'posts', post_translator, tag_normalizer)

for post_file in args.posts:
    post_importer.import_jsonl(post_file)
