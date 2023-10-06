# import \
#   --input posts.json \
#   --tags tags.json \
#   --source e621 \
#   --prefilter prefilter.yaml \
#   --aspect-ratios aspect_ratios.yaml \
#   --symbols symbols.yaml \
#   --rewrites rewrites.yaml \
#   --category-weights category_weights.yaml \
#   --save-tags \
#   --remove-old

import argparse
import json
from typing import Optional, TextIO

from pymongo.errors import DuplicateKeyError

from database.dr_db_create import reset_database
from database.importer.alias_importer import AliasImporter
from database.translator.translator import TagTranslator
from database.entities.tag import TagProtoEntity
from database.importer.importer import Importer
from database.tag_normalizer.tag_normalizer import TagNormalizer
from database.translator.helpers import get_post_translator, get_tag_translator, get_alias_translator
from database.utils.db_utils import connect_to_db
from utils.load_yaml import load_yaml
from utils.progress import Progress


def get_args():
    parser = argparse.ArgumentParser(prog='Import', description='Import post and tag metadata from e621, gelbooru, and danbooru')

    parser.add_argument('-p', '--posts', metavar='FILE', type=str, action='append', help='Post JSONL file(s) to import', required=True)
    parser.add_argument('-t', '--tags', metavar='FILE', type=str, help='Tag JSONL file(s)', required=True, action='append')
    parser.add_argument('-s', '--source', metavar='SOURCE', type=str, help='Data source [e926, e621, gelbooru, danbooru, rule34]', required=True, choices=['e926', 'e621', 'gelbooru', 'danbooru', 'rule34'])
    parser.add_argument('-a', '--aliases', metavar='FILE', type=str, help='Tag alias JSONL file(s)', required=False, default=None)
    parser.add_argument('--tag-version', metavar='VERSION', type=str, help='Preferred tag format version [v0, v1, v2]', required=False, default='v2', choices=['v0', 'v1', 'v2'])
    parser.add_argument('--prefilter', metavar='FILE', type=str, help='Prefilter YAML file', required=False, default='../examples/tag_normalizer/prefilter.yaml')
    parser.add_argument('--rewrites', metavar='FILE', type=str, help='Rewritten tags YAML file', required=False, default='../examples/tag_normalizer/rewrites.yaml')
    parser.add_argument('--aspect-ratios', metavar='FILE', type=str, help='Aspect ratios YAML file', required=False, default='../examples/tag_normalizer/aspect_ratios.yaml')
    parser.add_argument('--category-weights', metavar='FILE', type=str, help='Category weights YAML file', required=False, default='../examples/tag_normalizer/category_weights.yaml')
    parser.add_argument('--symbols', metavar='FILE', type=str, help='Symbols YAML file', required=False, default='../examples/tag_normalizer/symbols.yaml')
    parser.add_argument('--skip-save-tags', help='Do not save tags to the database', default=False, action='store_true')
    parser.add_argument('--remove-old', help='Remove all data from the database before importing', default=False, action='store_true')

    return parser.parse_args()


def stream_tag(tp: TextIO, tag_translator: TagTranslator) -> Optional[TagProtoEntity]:
    line = tp.readline()

    if line is None or line == '':
        return None

    data = json.loads(line)

    return tag_translator.translate(data)


def main():
    args = get_args()

    # initialize
    (db, client) = connect_to_db()

    # @todo: validate data structures
    aspect_ratios = load_yaml(args.aspect_ratios).get('tags', [])
    symbols = load_yaml(args.symbols).get('tags', [])
    prefilter = {key: True for key in load_yaml(args.prefilter).get('tags', [])}
    rewrites = {tag['from']: tag['to'] for tag in load_yaml(args.rewrites).get('tags', [])}
    category_weights = load_yaml(args.category_weights).get('categories', {})

    # clean database?
    if args.remove_old:
        progress = Progress('Cleaning database', 'collections')
        reset_database(db, client)
        progress.succeed('Database cleaned')

    # process tag aliases
    aliases = None

    if args.aliases is not None:
        alias_translator = get_alias_translator(args.source)
        alias_importer = AliasImporter(translator=alias_translator)
        aliases = {}

        for alias in alias_importer.load(args.aliases):
            if alias.tag_name not in aliases:
                aliases[alias.tag_name] = []

            aliases[alias.tag_name].append(alias.alias_name)

    # process tags
    tag_translator = get_tag_translator(args.source, aliases=aliases)
    tag_normalizer = TagNormalizer(prefilter=prefilter, symbols=symbols, aspect_ratios=aspect_ratios, rewrites=rewrites, category_naming_order=category_weights)

    for tag_file in args.tags:
        tp = open(tag_file, 'rt')
        tag_normalizer.load(lambda: stream_tag(tp, tag_translator))

    tag_normalizer.normalize(args.tag_version)

    if not args.skip_save_tags:
        save_tags_progress = Progress(title='Saving tags', units='tags')
        save_tag_errors = 0

        for tag in tag_normalizer.get_tags():
            save_tags_progress.update()

            try:
                db['tags'].replace_one({'source': tag.source, 'source_id': tag.source_id}, vars(tag), upsert=True)
            except DuplicateKeyError as e:
                save_tag_errors += 1
                print(f'Database level duplicate key error on tag "{tag.origin_name}" (#{tag.source_id}) -- tag not saved: {str(e)}')

        save_tags_progress.succeed(f'{save_tags_progress.count} tags saved, {save_tag_errors} errors')

    # process posts
    post_translator = get_post_translator(args.source, tag_normalizer)
    post_importer = Importer(db, 'posts', post_translator, tag_normalizer)

    for post_file in args.posts:
        post_importer.import_jsonl(post_file)


if __name__ == "__main__":
    main()
