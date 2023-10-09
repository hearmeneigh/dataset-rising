import argparse

import datasets
from datasets import Dataset
from datasets.table import embed_table_storage
import re
import os
import s3fs

from database.entities.post import PostEntity
from dataset.utils.format import format_posts_for_dataset
from dataset.utils.split import split_posts
from utils.progress import Progress



def get_args():
    parser = argparse.ArgumentParser(prog='Build', description='Build an image dataset from JSONL file(s)')
    parser.add_argument('-o', '--output', metavar='PATH', type=str, help='Path where the dataset will be stored', required=True)
    parser.add_argument('-s', '--samples', metavar='FILE', type=str, action='append', help='Post JSONL file(s) to import', required=True)
    parser.add_argument('-a', '--agent', metavar='AGENT', type=str, help='Unique user agent string (e.g. "mycrawler/1.0 (by myusername)")', required=True)
    parser.add_argument('--image-width', metavar='PIXELS', type=int, help='Maximum width for stored images', required=False, default=4096)
    parser.add_argument('--image-height', metavar='PIXELS', type=int, help='Maximum height for stored images', required=False, default=4096)
    parser.add_argument('--image-format', metavar='FORMAT', type=str, help='Storage image format [jpg, png]', choices=['jpg', 'png'], required=False, default='jpg')
    parser.add_argument('--image-quality', metavar='PERCENTAGE', type=int, help='Storage image quality (JPEG only)', required=False, default=85)
    parser.add_argument('--num-proc', metavar='COUNT', type=int, help='Maximum number of parallel processes', required=False, default=1)
    parser.add_argument('--upload-to-hf', metavar='USER_NAME/DATASET_NAME', type=str, help='Upload dataset to Huggingface (e.g. myuser/mynewdataset)', required=False, default=None)
    parser.add_argument('--upload-to-s3', metavar='S3_URL', type=str, help='Upload dataset to S3 (e.g. s3://some-bucket/some-path)', required=False, default=None)
    parser.add_argument('--limit', metavar='COUNT', type=int, help='Limit samples in dataset', required=False, default=None)
    parser.add_argument('--separator', metavar='STRING', type=str, help='Separator string for tag lists', required=False, default=' ')

    args = parser.parse_args()

    if re.match(r'(rising|hearmeneigh|mrstallion)', args.agent, flags=re.IGNORECASE):
        username = os.getlogin()
        print(f'The user agent string must not contain words "rising", "hearmeneigh", or "mrstallion". Try --agent "dr-{username}/1.0 (by {username})" instead?')
        exit(1)

    return args


def get_unique_post_id(post: PostEntity) -> str:
    return f'{post.source.value if "value" in post.source else post.source}___{post.source_id}'


def main():
    args = get_args()

    print("Splitting posts...")
    split_filenames = split_posts(args.samples, args.limit, args.num_proc)

    # generate dataset
    print('Generating the dataset & downloading images...')
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
          "selector": datasets.Value(dtype='string', id=None),
        }
      ),
      num_proc=args.num_proc,
      gen_kwargs={
            'shards': [{
                'samples': [fn],
                'limit': args.limit,
                'agent': args.agent,
                'image_width': args.image_width,
                'image_height': args.image_height,
                'image_format': args.image_format,
                'image_quality': args.image_quality,
                'separator': args.separator
            } for fn in split_filenames]
      }
    )

    # remove extra files
    for fn in split_filenames:
        os.remove(fn)

    # cast images
    p = Progress('Casting image column', 'images')
    ds.cast_column('image', datasets.Image())
    p.succeed('Image column cast complete')

    # embed bytes
    p = Progress('Embedding bytes for accurate shard sizing', 'bytes')
    initial_format = ds.format
    ds = ds.with_format("arrow")
    ds = ds.map(embed_table_storage, batched=True, num_proc=args.num_proc)
    ds = ds.with_format(**initial_format)
    p.succeed('Shard sizing complete')

    os.makedirs(args.output, exist_ok=True)
    ds.save_to_disk(args.output, max_shard_size='1GB', num_proc=args.num_proc)

    # upload to huggingface
    if args.upload_to_hf is not None:
        # max_shard_size must be < 2GB, or you will run into problems
        ds.push_to_hub(args.upload_to_hf, private=True, max_shard_size='1GB')

    # upload to S3
    if args.upload_to_s3 is not None:
        p = Progress(f'Uploading to S3 {args.upload_to_s3}', 'bytes')
        s3_file = s3fs.S3FileSystem()
        s3_file.put(args.output, args.upload_to_s3, recursive=True)
        p.succeed('Dataset uploaded to S3')

    print('Done!')
    print(f'Dataset created.')


if __name__ == "__main__":
    main()
