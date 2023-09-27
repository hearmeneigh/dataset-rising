# gap --category artists --selector filename.yaml --selector filename2.yaml --image-format jpg --image-format png --output /tmp/path --limit 10 --output-format html --template some.html.jinja

import argparse
import os
from typing import List, Tuple, Optional

import jinja2
import ndjson
import pymongo
from jinja2 import Template
from pymongo.database import Database

from database.entities.tag import TagEntity
from database.selector.selected_sample import SelectedSample
from database.selector.selector import Selector
from database. utils.db_utils import connect_to_db
from database.utils.enums import Category
from database.utils.source_url import get_tag_url, get_post_url
from utils.progress import Progress

missing = 'data:image/png;base64,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'


def get_args():
    parser = argparse.ArgumentParser(prog='Gap', description='Generate category gap analysis for selectors')

    parser.add_argument('-s', '--selector', metavar='FILE', type=str, help='Selector YAML file(s)', required=True, action='append', default=[])
    parser.add_argument('-o', '--output', metavar='FILE', type=str, help='Output file or path', required=True)
    parser.add_argument('-c', '--category', metavar='CATEGORY', type=str, help=f'Only list tags which 1) are in this specified category; and 2) are NOT matches with any of the selectors [{", ".join([c.value for c in Category])}]', required=True, choices=[c.value for c in Category])
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


def save_results_to_jsonl(path: str, results: List[Tuple[str, int, List[SelectedSample], str]], file_subtitle: str):
    (base_path, base_name, extension) = get_file_parts(path, file_subtitle)

    fn = os.path.join(base_path, f'{base_name}-{file_subtitle}{extension}')
    os.makedirs(base_path, exist_ok=True)

    with open(fn, 'w') as fp:
        writer = ndjson.writer(fp)

        for (tag_name, post_count, posts, tag_url) in results:
            writer.writerow({
                'category': tag_name,
                'post_count': post_count,
                'posts': [vars(post) for post in posts],
                'url': tag_url
            })


def get_paginated_filename(base_name: str, page_no: int, extension: str) -> str:
    return f'{base_name}-{str(page_no).zfill(4)}{extension}'


def save_results_to_html(
    path: str,
    results: List[Tuple[str, int, List[SelectedSample], str]],
    template: Template,
    category: str,
    file_subtitle: str,
):
    (base_path, base_name, extension) = get_file_parts(path, file_subtitle)
    os.makedirs(base_path, exist_ok=True)

    results.sort(key=lambda x: int(x[1]), reverse=True)

    # paginated
    categories_per_page = 25
    page_chunks = [results[i:i+categories_per_page] for i in range(0, len(results), categories_per_page)]
    count = 0

    for page_chunk in page_chunks:
        count += 1

        context = {
            'title': f'Tags in \'{category}\' not matching any selectors',
            'tags': [{'title': tag_name, 'images': posts, 'total_count': post_count, 'url': tag_url} for (tag_name, post_count, posts, tag_url) in page_chunk],
            'pagination': {
                'next': get_paginated_filename(base_name, count + 1, extension) if count < len(page_chunks) else None,
                'prev': get_paginated_filename(base_name, count - 1, extension) if count > 1 else None
            },
            'missing_image_url': missing
        }

        html = template.render(context)

        with open(os.path.join(base_path, get_paginated_filename(base_name, count, extension)), 'w') as html_file:
            html_file.write(html)


def does_not_match_selectors(tag_name: str, selectors: List[Selector]) -> bool:
    for selector in selectors:
        if selector.test(tag_name) is not None:
            return False
    return True


def sample_posts(tag_name: str, limit: int, db: Database, image_format: List[str]) -> Tuple[str, int, List[SelectedSample], str]:
    post_count_result = list(db['posts'].aggregate(pipeline=[
        {'$match': {'tags': tag_name, 'origin_format': {'$in': image_format}, 'image_url': {'$exists': True, '$ne': None}}},
        {'$count': 'total'}
    ]))

    if len(post_count_result) == 0:
        post_count = 0
    else:
        post_count = post_count_result[0].get('total', 0)

    posts = list(db['posts'].aggregate(pipeline=[
        {'$match': {'tags': tag_name, 'origin_format': {'$in': image_format}, 'image_url': {'$exists': True, '$ne': None}}},
        {'$sample': {'size': limit}}
    ]))

    tag_url = None
    tag = db['tags'].find_one({'preferred_name': tag_name})

    if tag is not None:
        tag_url = get_tag_url(TagEntity(tag))

    return tag_name, post_count, [SelectedSample(matches=[tag_name], post=post) for post in posts], tag_url


def main():
    args = get_args()

    # initialize
    (db, client) = connect_to_db()

    selectors = [Selector(selector, db) for selector in args.selector]
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(args.template)))

    def get_post_url_tpl(post: SelectedSample) -> Optional[str]:
        return get_post_url(post)

    env.filters['get_post_url'] = get_post_url_tpl

    tpl = env.get_template(os.path.basename(args.template))
    progress = Progress('Generating preview (this will take a while)', 'samples')

    category_tags = db['tags'].find(filter={'category': args.category}, sort=[('post_count', pymongo.DESCENDING)])
    result = [sample_posts(tag['preferred_name'], args.limit, db, args.image_format) for tag in category_tags if does_not_match_selectors(tag['preferred_name'], selectors)]

    if args.output_format == 'jsonl':
        save_results_to_jsonl(args.output, result, 'gap')
    else:
        save_results_to_html(args.output, result, tpl, args.category, 'gap')

    progress.succeed('Preview generated')


if __name__ == "__main__":
    main()
