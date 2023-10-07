import argparse
import ndjson
import random
import json
import os

from database.entities.post import PostEntity
from database.tag_normalizer.util import load_normalizer_from_database
from database.utils.db_utils import connect_to_db
from database.utils.enums import numeric_categories
from dataset.utils.balance import balance_selections
from dataset.utils.prune import prune_and_filter_tags
from utils.progress import Progress
from utils.load_yaml import load_yaml
from dataset.utils.selection_source import SelectionSource


def get_args():
    parser = argparse.ArgumentParser(prog='Join', description='Join multiple select outputs together')
    parser.add_argument('-o', '--output', metavar='FILE', type=str, help='JSONL file where the joined output will be written', required=True)
    parser.add_argument('-s', '--samples', metavar='FILE', type=str, action='append', help='Post JSONL file(s) to import', required=True)
    parser.add_argument('--export-tags', metavar='FILE', type=str, help='Export tag counts as a JSON file', required=False, default=None)
    parser.add_argument('--export-autocomplete', metavar='FILE', type=str, help='Export autocomplete hints as a a1111-sd-webui-tagcomplete CSV file', required=False, default=None)
    parser.add_argument('--min-posts-per-tag', metavar='COUNT', type=int, help='Minimum number of posts a tag must appear in to be included', required=False, default=100)
    parser.add_argument('--min-tags-per-post', metavar='COUNT', type=int, help='Minimum number of tags in a post for the post to be included (counted after min-posts-per-tag limit has been applied)', required=False, default=10)
    parser.add_argument('--prefilter', metavar='FILE', type=str, help='Prefilter YAML file', required=False, default='../examples/dataset/prefilter.yaml')
    parser.add_argument('--limit', metavar='COUNT', type=int, help='Limit samples in dataset', required=False, default=None)

    args = parser.parse_args()
    return args


def get_unique_post_id(post: PostEntity) -> str:
    return f'{post.source.value if "value" in post.source else post.source}___{post.source_id}'


def main():
    args = get_args()

    print('Loading filters')
    prefilters = {key: True for key in load_yaml(args.prefilter).get('tags', [])}

    p = Progress('Loading samples', 'samples')
    selections = [SelectionSource(samples) for samples in args.samples]
    p.succeed('Samples loaded!')

    # remove duplicates
    print('Removing duplicates')
    for (index, selection) in enumerate(selections):
        if index > 0:
            original_count = len(selection.posts)
            before_sels = selections[0:index]
            before_posts = set([get_unique_post_id(post) for sel in before_sels for post in sel.posts])
            selection.posts = [post for post in selection.posts if get_unique_post_id(post) not in before_posts]

            if len(selection.posts) != original_count:
                print(f'Removed {original_count - len(selection.posts)} duplicates from {selection.filename}')


    # balance selections
    print('Balancing selectors')
    balance_selections(selections)

    # combine selections
    print('Combining selectors')
    posts = [post for sel in selections for post in sel.posts]

    for selection in selections:
        print(f'Using {len(selection.posts)} ({round(len(selection.posts)/len(posts)*100, 1)}%) from {selection.filename}')

    # prune and filter tags
    print('Pruning tags...')
    tag_counts = prune_and_filter_tags(posts, prefilters, args.min_posts_per_tag)

    print(f'Using {len(tag_counts)} tags')

    # remove excess tags from posts
    for post in posts:
        post.tags = [tag for tag in post.tags if tag_counts.get(tag, 0) >= args.min_posts_per_tag]

    # remove posts that have too few tags
    print('Pruning posts...')
    old_post_count = len(posts)
    posts = [post for post in posts if len(post.tags) >= args.min_tags_per_post]
    print(f'Pruned {old_post_count - len(posts)} posts')

    # save tags
    if args.export_tags is not None:
        print('Saving tags...')
        os.makedirs(os.path.dirname(args.export_tags), exist_ok=True)

        with open(args.export_tags, 'w') as fp:
            tag_dict = {tag_name: tag_count for tag_name, tag_count in tag_counts.items() if tag_count >= args.min_posts_per_tag}
            json.dump(tag_dict, fp, indent=2)

    # save autocomplete
    if args.export_autocomplete is not None:
        print('Saving autocomplete...')
        os.makedirs(os.path.dirname(args.export_autocomplete), exist_ok=True)
        (db, client) = connect_to_db()

        # process tags
        tag_normalizer = load_normalizer_from_database(db)

        with open(args.export_autocomplete, 'w') as csv_file:
            for (tag_name, tag_count) in tag_counts.items():
                tag = tag_normalizer.get(tag_name)

                if tag is None:
                    print(f'Unexpected tag not found in database: "{tag_name}"')
                    continue

                known_aliases = [t for t in [tag.v1_name, tag.v2_name, tag.v2_short, tag.origin_name] if t != tag.preferred_name]

                if tag.aliases is not None:
                    for alias in tag.aliases:
                        if alias != tag.preferred_name and alias.strip() != '':
                            known_aliases.append(alias)

                csv_file.write(f"{tag.preferred_name},{numeric_categories.get(tag.category, 0)},{tag_count},\"{','.join(set(known_aliases))}\"\n")

    # shuffle posts
    print('Shuffling posts...')
    random.shuffle(posts)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    fp = open(args.output, 'w')
    writer = ndjson.writer(fp)

    for post in posts:
        writer.writerow(vars(post))

    fp.close()

    print('Done!')
    print(f'{len(posts)} samples with {len(tag_counts)} tags stored in {args.output}')


if __name__ == "__main__":
    main()
