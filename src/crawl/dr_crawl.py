# crawl --output some.jsonl --type search|index|tags|implications --source e926|e621|gelbooru|danbooru [--query "some tags"] [--recover]

import argparse
import re
import os

from crawl.crawler.helpers import get_crawler


def get_args():
    parser = argparse.ArgumentParser(prog='Crawl', description='Download metadata from e926, e621, gelbooru, rule34, and danbooru')

    parser.add_argument('-o', '--output', metavar='FILE', type=str, help='Output JSONL file', required=True)
    parser.add_argument('-a', '--agent', metavar='AGENT', type=str, help='Unique user agent string (e.g. "mycrawler/1.0 (by myusername)")', required=True)
    parser.add_argument('-t', '--type', metavar='TYPE', type=str, help='Crawl type [search, index, tags, implications, aliases]', required=True, choices=['search', 'posts', 'tags', 'implications', 'aliases'])
    parser.add_argument('-s', '--source', metavar='SOURCE', type=str, help='Crawl source [e926, e621, gelbooru, danbooru, rule34]', required=True, choices=['e926', 'e621', 'gelbooru', 'danbooru', 'rule34'])
    parser.add_argument('-q', '--query', metavar='KEYWORD', type=str, help='Crawl query', required=False)
    parser.add_argument('-r', '--recover', default=False, action='store_true', help='Recover from last crawl position')

    return parser.parse_args()


def main():
    args = get_args()

    if re.match(r'(rising|hearmeneigh|mrstallion)', args.agent, flags=re.IGNORECASE):
        username = os.getlogin()
        print(f'The user agent string must not contain words "rising", "hearmeneigh", or "mrstallion". Try --agent "dr-{username}/1.0 (by {username})" instead?')
        exit(1)

    c = get_crawler(args.source, args.type, args.output, args.query)
    c.crawl(recover=args.recover, agent=args.agent)


if __name__ == "__main__":
    main()
