# crawl --output some.jsonl --type search|index|tags|implications --source e621|gelbooru|danbooru [--query "some tags"] [--recover]

import argparse
from crawler.helpers import get_crawler

parser = argparse.ArgumentParser(prog='Crawl', description='Download metadata from e621, gelbooru, and danbooru')

parser.add_argument('-o', '--output', metavar='FILE', type=str, help='Output JSONL file', required=True)
parser.add_argument('-a', '--agent', metavar='AGENT', type=str, help='Unique user agent string', required=True)
parser.add_argument('-t', '--type', metavar='TYPE', type=str, help='Crawl type', required=True, choices=['search', 'index', 'tags', 'implications'])
parser.add_argument('-s', '--source', metavar='SOURCE', type=str, help='Crawl source', required=True, choices=['e621', 'gelbooru', 'danbooru'])
parser.add_argument('-q', '--query', metavar='KEYWORD', type=str, help='Crawl query', required=False)
parser.add_argument('-r', '--recover', default=False, action='store_true')

args = parser.parse_args()

c = get_crawler(args.source, args.type, args.output, args.query)
c.crawl(recover=args.recover, agent=args.agent)
