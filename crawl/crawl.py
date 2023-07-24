import argparse

from crawler.helpers import get_crawler

# crawl --output some.jsonl --type search|index|tags|implications --source e621|gelbooru|danbooru --query "some tags"

parser = argparse.ArgumentParser(prog='Crawl', description='Download index and metadata from e621, gelbooru, and danbooru')

parser.add_argument('-o', '--output', type=str, help='Output JSONL file', required=True)
parser.add_argument('-t', '--type', type=str, help='Crawl type', required=True, choices=['search', 'index', 'tags', 'implications'])
parser.add_argument('-s', '--source', type=str, help='Crawl source', required=True, choices=['e621', 'gelbooru', 'danbooru'])
parser.add_argument('-q', '--query', type=str, help='Crawl query', required=False)

args = parser.parse_args()

c = get_crawler(args.source, args.type, args.output, args.query)
c.crawl()
