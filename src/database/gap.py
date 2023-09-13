# gap --category artists --selector filename.yaml --selector filename2.yaml --image-format jpg --image-format png --output /tmp/path --limit 10 --output-format html --template some.html.jinja

import argparse
import os
from typing import List, Tuple

import jinja2
import ndjson
from jinja2 import Template
from pymongo.database import Database

from database.entities.post import PostEntity
from database.selector.selector import Selector
from database. utils.db_utils import connect_to_db
from database.utils.enums import Category
from utils.progress import Progress


def get_args():
    parser = argparse.ArgumentParser(prog='Gap', description='Generate category gap analysis for selectors')

    parser.add_argument('-s', '--selector', metavar='FILE', type=str, help='Selector YAML file(s)', required=True, action='append', default=[])
    parser.add_argument('-o', '--output', metavar='FILE', type=str, help='Output file or path', required=True)
    parser.add_argument('-c', '--category', metavar='CATEGORY', type=str, help=f'Only list tags which 1) are in this specified category; and 2) are NOT matches with any of the selectors [{", ".join([c for c in Category])}]', required=True, choices=[c for c in Category])
    parser.add_argument('-l', '--limit', metavar='COUNT', type=int, help='Number of samples to generate per aggregate', required=False, default=10)
    parser.add_argument('-i', '--image-format', metavar='FORMAT', type=str, help='Image formats to select from (default: [jpg, png])', required=False, action='append', default=[])
    parser.add_argument('-f', '--output-format',metavar='FORMAT', type=str, help='Output format [html, jsonl]', required=False, choices=['html', 'jsonl'], default='html')
    parser.add_argument('-t', '--template', metavar='FILE', type=str, help='HTML template file', required=False, default='../examples/preview/preview.html.jinja')

    args = parser.parse_args()

    if len(args.image_format) == 0:
        args.image_format = ['jpg', 'png']

    return args


def get_file_parts(path: str, file_subtitle) -> (str, str, str):
    filename = os.path.basename(path)
    (base_name, extension) = os.path.splitext(filename)

    if extension == '' or extension is None:
        # we were provided a base path
        base_path = path
        base_name = file_subtitle
        extension = '.html'
    else:
        # we were provided a filename
        base_path = os.path.dirname(path)
        base_name = base_name
        extension = extension

    return base_path, base_name, extension


def save_results_to_jsonl(path: str, results: List[Tuple[str, int, List[PostEntity]]], file_subtitle: str):
    (base_path, base_name, extension) = get_file_parts(path, file_subtitle)

    fn = os.path.join(base_path, f'{base_name}-{file_subtitle}{extension}')
    os.makedirs(base_path, exist_ok=True)

    with open(fn, 'w') as fp:
        writer = ndjson.writer(fp)

        for (tag_name, post_count, posts) in results:
            writer.writerow({
                'category': tag_name,
                'post_count': post_count,
                'posts': [vars(post) for post in posts]
            })


def get_paginated_filename(base_name: str, file_subtitle: str, page_no: int, extension: str) -> str:
    return f'{base_name}-{file_subtitle}-{str(page_no).zfill(4)}{extension}'


def save_results_to_html(
    path: str,
    results: List[Tuple[str, int, List[PostEntity]]],
    template: Template,
    category: str,
    file_subtitle: str,
):
    (base_path, base_name, extension) = get_file_parts(path, file_subtitle)
    os.makedirs(base_path, exist_ok=True)

    # paginated
    categories_per_page = 25
    page_chunks = [results[i:i+categories_per_page] for i in range(0, len(results), categories_per_page)]
    count = 0

    for page_chunk in page_chunks:
        count += 1

        context = {
            'title': f'Tags in \'{category}\' not matching any selectors',
            'tags': [{'title': tag_name, 'images': posts, 'total_count': post_count} for (tag_name, post_count, posts) in page_chunk],
            'pagination': {
                'next': get_paginated_filename(base_name, file_subtitle, count + 1, extension) if count < len(page_chunks) else None,
                'prev': get_paginated_filename(base_name, file_subtitle, count - 1, extension) if count > 1 else None
            }
        }

        html = template.render(context)

        with open(os.path.join(base_path, get_paginated_filename(base_name, file_subtitle, count, extension)), 'w') as html_file:
            html_file.write(html)


def does_not_match_selectors(tag_name: str, selectors: List[Selector]) -> bool:
    for selector in selectors:
        if selector.test(tag_name) is not None:
            return False
    return True


def sample_posts(tag_name: str, limit: int, db: Database, image_format: List[str]) -> Tuple[str, int, List[PostEntity]]:
    post_count = int(db['posts'].aggregate([
        {'$match': {'tags': tag_name, 'image_format': {'$in': image_format}, 'image_url': {'$exists': True}}},
        {'$count': 'total'}
    ])[0]['total'])

    posts = list(db['posts'].aggregate([
        {'$match': {'tags': tag_name, 'image_format': {'$in': image_format}, 'image_url': {'$exists': True}}},
        {'$sample': {'size': limit}}
    ]))
    return tag_name, post_count, [PostEntity(post) for post in posts]


def main():
    args = get_args()

    # initialize
    (db, client) = connect_to_db()

    selectors = [Selector(selector, db) for selector in args.selector]
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(args.template)))
    tpl = env.get_template(os.path.basename(args.template))

    category_tags = db['tags'].find({'category': args.category}, {'post_count': -1})
    result = [sample_posts(tag['preferred_name'], args.limit, db, args.image_format) for tag in category_tags if does_not_match_selectors(tag['preferred_name'], selectors)]

    progress = Progress('Generating preview', 'samples')

    if args.output_format == 'jsonl':
        save_results_to_jsonl(args.output, result, 'gap')
    else:
        save_results_to_html(args.output, result, tpl, args.category, 'gap')

    progress.succeed('Preview generated')


if __name__ == "__main__":
    main()
