# preview --selector filename.yaml --image-format jpg --image-format png --output /tmp/path --limit 10 --output-format html --template some.html.jinja  [--aggregate]

import argparse
import os
from typing import Generator, List, Union, Dict
from bson import json_util
import json

import jinja2
import ndjson
from jinja2 import Template

from database.entities.post import PostEntity
from database.selector.selector import Selector
from database.utils.db_utils import connect_to_db
from utils.progress import Progress


def get_args():
    parser = argparse.ArgumentParser(prog='Preview', description='Generate preview for a selector')

    parser.add_argument('-s', '--selector', metavar='FILE', type=str, help='Selector YAML file', required=True)
    parser.add_argument('-o', '--output', metavar='FILE', type=str, help='Output file or path', required=True)
    parser.add_argument('-l', '--limit', metavar='COUNT', type=int, help='Number of samples to generate per aggregate', required=False, default=10)
    parser.add_argument('-i', '--image-format', metavar='FORMAT', type=str, help='Image formats to select from (default: [jpg, png])', required=False, action='append', default=[])
    parser.add_argument('-f', '--output-format', metavar='FORMAT', type=str, help='Output format phtml, jsonl]', required=False, choices=['html', 'jsonl'], default='html')
    parser.add_argument('-a', '--aggregate', help='Aggregate categories (=preview how the whole selector will perform, not the categories)', default=False, action='store_true')
    parser.add_argument('-t', '--template', metavar='FILE', type=str, help='HTML template file', required=False, default='../examples/preview/preview.html.jinja')


    args = parser.parse_args()

    if len(args.image_format) == 0:
        args.image_format = ['jpg', 'png']

    if args.aggregate and args.gap:
        print('Cannot use --aggregate and --gap at the same time')
        exit(1)

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


def save_results_to_jsonl(path: str, results: Union[Dict[str, List[PostEntity]], Generator[PostEntity, None, None]], file_subtitle: str):
    (base_path, base_name, extension) = get_file_parts(path, file_subtitle)

    fn = os.path.join(base_path, f'{base_name}-{file_subtitle}{extension}')
    os.makedirs(base_path, exist_ok=True)

    with open(fn, 'w') as fp:
        writer = ndjson.writer(fp)

        if isinstance(results, Generator):
            for post in results:
                cleaned = json.loads(json_util.dumps(vars(post)))

                writer.writerow(cleaned)
        else:
            for category, category_key in results:
                writer.writerow({
                    'category': category_key,
                    'posts': [vars(post) for post in category]
                })


def get_paginated_filename(base_name: str, file_subtitle: str, page_no: int, extension: str) -> str:
    return f'{base_name}-{file_subtitle}-{str(page_no).zfill(4)}{extension}'


def save_results_to_html(
    path: str,
    results: Union[Dict[str, List[PostEntity]], Generator[PostEntity, None, None]],
    template: Template,
    selector_file: str,
    file_subtitle: str,
):
    (base_path, base_name, extension) = get_file_parts(path, file_subtitle)
    os.makedirs(base_path, exist_ok=True)

    if isinstance(results, Generator):
        posts = list(results)

        context = {
            'title': f'Aggregated Samples for {selector_file}',
            'tags': [
                {'title': 'Images', 'images': posts}
            ]
        }

        html = template.render(context)

        with open(os.path.join(base_path, f'{base_name}{extension}'), 'w') as html_file:
            html_file.write(html)
    else:
        # paginated
        items = list(results.items())
        categories_per_page = 25
        page_chunks = [items[i:i+categories_per_page] for i in range(0, len(items), categories_per_page)]
        count = 0

        for page_chunk in page_chunks:
            count += 1

            context = {
                'title': f'Categorized Samples for {selector_file}',
                'tags': [{'title': tag_item[0], 'images': tag_item[1]} for tag_item in page_chunk],
                'pagination': {
                    'next': get_paginated_filename(base_name, file_subtitle, count + 1, extension) if count < len(page_chunks) else None,
                    'prev': get_paginated_filename(base_name, file_subtitle, count - 1, extension) if count > 1 else None
                }
            }

            html = template.render(context)

            with open(os.path.join(base_path, get_paginated_filename(base_name, file_subtitle, count, extension)), 'w') as html_file:
                html_file.write(html)


def main():
    args = get_args()

    # initialize
    (db, client) = connect_to_db()

    selector = Selector(args.selector, db)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(args.template)))
    tpl = env.get_template(os.path.basename(args.template))

    if args.aggregate:
        # generate aggregated preview
        result = selector.select(formats=args.image_format, limit=args.limit)
        progress = Progress('Generating preview', 'samples')

        if args.output_format == 'jsonl':
            save_results_to_jsonl(args.output, result, 'aggregated')
        else:
            save_results_to_html(args.output, result, tpl, args.selector, 'aggregated')

        progress.succeed('Preview generated')
    else:
        # generate per-category preview
        result = selector.sample_selectors(samples=args.limit, formats=args.image_format)
        progress = Progress('Generating preview', 'samples')

        if args.output_format == 'jsonl':
            save_results_to_jsonl(args.output, result['includes'], 'includes')
            save_results_to_jsonl(args.output, result['excludes'], 'excludes')
        else:
            save_results_to_html(args.output, result['includes'], tpl, args.selector, 'includes')
            save_results_to_html(args.output, result['excludes'], tpl, args.selector, 'excludes')

        progress.succeed('Preview generated')


if __name__ == "__main__":
    main()
