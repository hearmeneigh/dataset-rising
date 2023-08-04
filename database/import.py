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

from database.entities.tag import TagEntity
from database.importer.importer import Importer
from database.tag_normalizer.tag_normalizer import TagNormalizer
from database.translator.helpers import get_post_translator
from database.utils.db_utils import connect_to_db
from database.utils.load_yaml import load_yaml
from database.utils.progress import Progress

parser = argparse.ArgumentParser(prog='Import', description='Import index and metadata from e621, gelbooru, and danbooru')

parser.add_argument('-i', '--input', type=str, action='append', help='Post JSONL file(s) to input', required=True)
parser.add_argument('-t', '--tags', type=str, help='Tag JSON file', required=True)
parser.add_argument('-s', '--source', type=str, help='Data source', required=True, choices=['e621', 'gelbooru', 'danbooru'])
parser.add_argument('--prefilter', type=str, help='Prefilter YAML file', required=False, default='../examples/tag_normalizer/prefilter.yaml')
parser.add_argument('--aspect-ratios', type=str, help='Aspect ratios YAML file', required=False, default='../examples/tag_normalizer/aspect_ratios.yaml')
parser.add_argument('--symbols', type=str, help='Symbols YAML file', required=False, default='../examples/tag_normalizer/symbols.yaml')
parser.add_argument('--save-tags', type=bool, help='Save tags to the database', required=False, default=True)
parser.add_argument('--remove-old', type=bool, help='Remove all data from the database before importing', required=False)

args = parser.parse_args()

aspect_ratios = load_yaml(args.aspect_ratios)['tags']
symbols = load_yaml(args.symbols)['tags']
prefilter = load_yaml(args.prefilter)['tags']

(db, client) = connect_to_db()
save_tag_count = 0

normalizer = TagNormalizer(prefilter=prefilter, symbols=symbols, aspect_ratios=aspect_ratios)
normalizer.load(args.tag_file)
normalizer.normalize(args.tag_version)

translator = get_post_translator(args.source, normalizer)
importer = Importer(db, 'posts', translator)

if args.remove_old:
    db['posts'].delete_many({})
    db['tags'].delete_many({})
    db['implications'].delete_many({})

for input_file in args.input:
    importer.import_jsonl(args.input)

if args.save_tags:
    save_tags_progress = Progress('Importing tags', total=len(normalizer.id_map))
    normalizer.save(lambda tag: save_tag(tag))


def save_tag(tag: TagEntity):
    save_tags_progress.update()
    db['tags'].replace_one({'source': tag.source, 'source_id': tag.source_id}, vars(tag), upsert=True)
