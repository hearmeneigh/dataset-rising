import argparse
import time

from database.entities.tag import TagProtoEntity, TagVersion
from database.tag_normalizer.util import load_normalizer_from_database
from database.utils.db_utils import connect_to_db
from database.utils.enums import Category, Source, to_source, to_category
from utils.load_yaml import load_yaml


def get_args():
    parser = argparse.ArgumentParser(prog='Add tag', description='Add a tag to the database')

    sources = [str(c).lower().replace('source.', '') for c in Source]
    categories = [str(c).lower().replace('category.', '') for c in Category]

    parser.add_argument('-t', '--tag', type=str, action='append', help='Tag name', required=True)
    parser.add_argument('-s', '--source', type=str, help=f'Data source', required=True, choices=sources)
    parser.add_argument('-i', '--source-id', type=str, help='Source ID', required=False)
    parser.add_argument('-c', '--category', type=str, help=f'Category', required=True, choices=categories)
    parser.add_argument('-a', '--alias', type=str, action='append', help=f'Alias', required=False)
    parser.add_argument('--category-weights', metavar='FILE', type=str, help='Category weights YAML file', required=False, default='../examples/tag_normalizer/category_weights.yaml')
    parser.add_argument('--skip-if-exists', action='store_true', help='Skip if tag already exists', required=False, default=False)

    return parser.parse_args()


def main():
    args = get_args()

    (db, client) = connect_to_db()

    category_weights = load_yaml(args.category_weights).get('categories', {})
    tag_normalizer = load_normalizer_from_database(db, category_naming_order=category_weights)

    for tag_name in args.tag:
        proto_tag = TagProtoEntity(
            source=to_source(args.source),
            source_id=args.source_id if args.source_id is not None else f'{args.source}:{args.category}:{tag_name}',
            origin_name=tag_name,
            reference_name=tag_name,
            category=to_category(args.category),
            aliases=args.alias if args.alias is not None else [],
            post_count=0
        )

        v1_tag = tag_normalizer.to_v1_tag(proto_tag)
        v2_tag = tag_normalizer.to_v2_tag(proto_tag)
        v2_tag_short = tag_normalizer.to_v2_tag(proto_tag, True)

        if args.skip_if_exists:
            t = tag_normalizer.get(v2_tag)

            if t is not None and t.source == proto_tag.source and t.source_id == proto_tag.source_id:
                print(f'Tag \'{tag_name}\' already exists')
                continue

            if t is not None and t.category == proto_tag.category and t.v2_name == v2_tag:
                print(f'Tag \'{tag_name}\' already exists')
                continue

            t = tag_normalizer.get(v2_tag_short)

            if t is not None and t.source == proto_tag.source and t.source_id == proto_tag.source_id:
                print(f'Tag \'{tag_name}\' already exists')
                continue

            if t is not None and t.category == proto_tag.category and t.v2_name == v2_tag:
                print(f'Tag \'{tag_name}\' already exists')
                continue

        tag = tag_normalizer.add_tag(v1_tag, proto_tag, TagVersion.V1)

        tag_normalizer.add_tag(v2_tag, proto_tag, TagVersion.V2)

        if v2_tag is not v2_tag_short:
            tag_normalizer.add_tag(v2_tag_short, proto_tag, TagVersion.V2)

            if tag_normalizer.get(v2_tag_short) == tag_normalizer.get(v2_tag):
                tag.preferred_name = v2_tag_short

        db['tags'].replace_one({'source': tag.source, 'source_id': tag.source_id}, vars(tag), upsert=True)

        print(f'Added tag \'{tag.preferred_name}\'')


if __name__ == "__main__":
    main()
