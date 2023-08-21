# pick --selector filename.yaml --image-format jpg --image-format png --output /tmp/path/to/file.jsonl

import argparse
import os
from typing import Generator
from bson import json_util
import json

import ndjson

from entities.post import PostEntity
from selector.selector import Selector
from utils.db_utils import connect_to_db
from utils.progress import Progress

parser = argparse.ArgumentParser(prog='Pick', description='Pick samples for a selector')

parser.add_argument('-s', '--selector', type=str, help='Selector YAML file', required=True)
parser.add_argument('-o', '--output', type=str, help='Output file (JSONL)', required=True)
parser.add_argument('-l', '--limit', type=int, help='Number of samples to generate (default: max)', required=False, default=None)
parser.add_argument('-i', '--image-format', type=str, help='Image formats to select from', required=False, action='append', default=['jpg', 'png'])

args = parser.parse_args()


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


def save_results_to_jsonl(filename: str, results: Generator[PostEntity, None, None], progress: Progress):
    with open(filename, 'w') as fp:
        writer = ndjson.writer(fp)
        i = 0

        for post in results:
            progress.update()

            cleaned = json.loads(json_util.dumps(vars(post)))

            writer.writerow(cleaned)
            i += 1



# initialize
(db, client) = connect_to_db()
selector = Selector(args.selector, db)

result = selector.select(formats=args.image_format, limit=args.limit)

progress = Progress('Generating samples', 'samples')
save_results_to_jsonl(args.output, result, progress)
progress.succeed(f'Generated {progress.count} samples')
