import argparse
import io
import math

import boto3
import datasets
from datasets import Dataset
from datasets.table import embed_table_storage
from typing import List
import re
import random
import json

from dataset.tasks.download import download_image
from dataset.tasks.load import load_image
from dataset.tasks.resize import resize_image
from entities.post import PostEntity
from utils.progress import Progress
from utils.load_yaml import load_yaml

parser = argparse.ArgumentParser(prog='Build', description='Build an image dataset from JSONL file(s)')
parser.add_argument('-s', '--source', metavar='FILE', type=str, action='append', help='Post JSONL file(s) to import', required=True)
parser.add_argument('-a', '--agent', metavar='AGENT', type=str, help='Unique user agent string', required=True)
parser.add_argument('-e', '--export-tags', metavar='FILE', type=str, help='Export tag counts as a JSON file', required=False, default=None)
parser.add_argument('--min-posts-per-tag', metavar='COUNT', type=int, help='Minimum number of posts a tag must appear in to be included', required=False, default=150)
parser.add_argument('--min-tags-per-post', metavar='COUNT', type=int, help='Minimum number of tags in a post for the post to be included (counted after min-posts-per-tag limit has been applied)', required=False, default=10)
parser.add_argument('--prefilter', metavar='FILE', type=str, help='Prefilter YAML file', required=False, default='../examples/dataset/prefilter.yaml')
parser.add_argument('--image-width', metavar='PIXELS', type=int, help='Maximum width for stored images', required=False, default=4096)
parser.add_argument('--image-height', metavar='PIXELS', type=int, help='Maximum height for stored images', required=False, default=4096)
parser.add_argument('--image_format', metavar='FORMAT', type=str, help='Store image format', choices=['JPEG', 'PNG'], required=False, default='JPEG')
parser.add_argument('--image_quality', metavar='PERCENTAGE', type=str, help='Store image quality', required=False, default=85)
parser.add_argument('--num-proc', metavar='COUNT', type=int, help='Maximum number of parallel processes', required=False, default=1)
parser.add_argument('--upload-to-huggingface', metavar='USER_NAME/DATASET_NAME', type=int, help='Upload dataset to Huggingface (e.g. myuser/mynewdataset)', required=False, default=None)
parser.add_argument('--upload-to-s3', metavar='S3_URL', type=int, help='Upload dataset to S3 (e.g. s3://some-bucket/some-path)', required=False, default=None)
parser.add_argument('--limit', metavar='COUNT', type=int, help='Limit samples in dataset', required=False, default=None)

args = parser.parse_args()

prefilters = {key: True for key in load_yaml(args.prefilter).get('tags', [])}


class SelectionSource:
    def __init__(self, filename_with_ratio: str):
        match = re.match(r'^(.*)(:[0-9.]%)$', filename_with_ratio)

        if match is None:
            filename = filename_with_ratio
            ratio = 1.0
        else:
            filename = match.group(1)
            ratio = float(match.group(2)) / 100.0

        self.filename = filename
        self.ratio = ratio
        self.posts = self.load(filename)

    def load(self, filename: str) -> List[PostEntity]:
        posts = []

        with open(filename, 'r') as fp:
            for line in fp:
                posts.append(PostEntity(json.loads(line)))

        return posts


selections = [SelectionSource(source) for source in args.source]

# remove duplicates
for (selection, index) in selections:
    if index > 0:
        before_sels = selections[0:index-1]
        before_posts = [post for sel in before_sels for post in sel.posts]
        selection.posts = set(selection).intersection(before_posts)

# balance selections
total_ratio = math.fsum([sel.ratio for sel in selections])
total_posts = sum([len(sel.posts) for sel in selections])

for selection in selections:
    intended_size = round(selection.ratio / total_ratio * total_posts)

    if intended_size > len(selection.posts):
        print(f'WARNING: Selection {selection.filename} has {len(selection.posts)} posts, but should have {intended_size} to match ratio. Using all posts.')
    else:
        selection.posts = selection.posts[0:intended_size]

1# combine selections
posts = [post for sel in selections for post in sel.posts]

for selection in selections:
    print(f'Using {len(selection.posts)} ({round(len(selection.posts)/len(posts)*100, 1)}%) from {selection.filename}')

# prune tags
tag_counts = {}

for post in posts:
    for tag in post.tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

# filter tags
for prefilter in prefilters:
    tag_counts.pop(prefilter)

# count tags
total_tags = 0

for tag_count in tag_counts:
    if tag_count >= args.min_posts_per_tag:
        total_tags += 1

print(f'Using {total_tags} tags')

for post in posts:
    posts.tags = [tag for tag in post.tags if tag_counts.get(tag, 0) >= args.min_posts_per_tag]


# filter posts
posts = [post for post in posts if len(post.tags) >= args.min_tags_per_post]


# save tags
if args.export_tags is not None:
    with open(args.export_tags, 'w') as fp:
        tag_dict = {tag_name: tag_count for tag_count, tag_name in tag_counts.items() if tag_count >= args.min_posts_per_tag}
        json.dump(tag_dict, fp, indent=2)


# shuffle posts
random.shuffle(posts)


def format_posts_for_dataset(posts: List[PostEntity]):
    progress = Progress('Downloading and importing images', 'images')

    for post in posts:
        progress.update()
        download = download_image(post, args.agent)

        if download is None:
            continue

        im = load_image(download, post)

        if im is None:
            continue

        resized_image = resize_image(im=im, post=post, max_width=args.image_width, max_height=args.image_height)

        if resized_image is None:
            continue

        # shuffle tags
        shuffled_tags = post.tags.copy()
        random.shuffle(shuffled_tags)

        # compress image
        compressed_image = io.BytesIO()
        resized_image.save(compressed_image, format=args.image_format, quality=args.image_quality, optimize=True)

        record = {
            'source_id': post.source_id,
            'source': post.source,
            'image': compressed_image.getvalue(),
            'tags': shuffled_tags,
            'url': post.image_url,
            'text': args.separator.join(shuffled_tags),
            'desc': post.description
        }

        yield record

    progress.succeed(f'{progress.count} images imported')


ds = Dataset.from_generator(
  format_posts_for_dataset,
  features=datasets.Features(
    {
      "source_id": datasets.Value(dtype='string', id=None),
      "source": datasets.Value(dtype='string', id=None),
      "image": datasets.Image(),
      "tags": datasets.Sequence(datasets.Value(dtype='string', id=None)),
      "url": datasets.Value(dtype='string', id=None),
      "text": datasets.Value(dtype='string', id=None),
      "desc": datasets.Value(dtype='string', id=None)
    }
  ),
  num_proc=args.num_proc,
  gen_kwargs={'posts': posts if args.limit is None else posts[0:args.limit]}
)


p = Progress('Casting image column', 'images')
ds.cast_column('image', datasets.Image())
p.succeed('Image column cast complete')


p = Progress('Embedding bytes for accurate shard sizing', 'bytes')
initial_format = ds.format
ds = ds.with_format("arrow")
ds = ds.map(embed_table_storage, batched=True, num_proc=args.num_proc)
ds = ds.with_format(**initial_format)
p.succeed('Shard sizing complete')


if args.upload_to_huggingface is not None:
    p = Progress(f'Uploading to Huggingface {args.upload_to_huggingface}', 'bytes')
    # max_shard_size must be < 2GB, or you will run into problems
    ds.push_to_hub(args.upload_to_huggingface, private=True, max_shard_size='1GB')
    p.succeed('Dataset uploaded to Huggingface')

if args.upload_to_s3 is not None:
    p = Progress(f'Uploading to S3 {args.upload_to_s3}', 'bytes')
    s3_client = boto3.client('s3')
    p.succeed('Dataset uploaded to S3')

print('Done!')
print(f'Created a dataset with {len(posts)} samples and {len(tag_counts)} tags')
