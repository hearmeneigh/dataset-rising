from typing import Optional

from crawl.crawler.crawler import Crawler
import urllib.parse


def get_e926_index_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://e926.net/posts.json?limit=320',
        page_type='by_id',
        page_field='page',
        page_field_prefix='b'
    )


def get_e926_search_crawler(output_file: str, search_query: str):
    return Crawler(
        output_file=output_file,
        base_url='https://e926.net/posts.json?limit=320&tags=' + urllib.parse.quote(search_query, ''),
        page_type='index',
        page_field='page'
    )


def get_e926_tag_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://e926.net/tags.json?limit=320&search[order]=date',
        page_type='by_id',
        page_field='page',
        page_field_prefix='b',
        json_field=None
    )


def get_e926_tag_aliases_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://e926.net/tag_aliases.json?limit=320&search[order]=date',
        page_type='by_id',
        page_field='page',
        page_field_prefix='b',
        json_field=None
    )


def get_e926_implications_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://e926.net/tag_implications.json?limit=320',
        page_type='index',
        page_field='page',
        json_field=None
    )


def get_e621_index_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://e621.net/posts.json?limit=320',
        page_type='by_id',
        page_field='page',
        page_field_prefix='b'
    )


def get_e621_search_crawler(output_file: str, search_query: str):
    return Crawler(
        output_file=output_file,
        base_url='https://e621.net/posts.json?limit=320&tags=' + urllib.parse.quote(search_query, ''),
        page_type='index',
        page_field='page'
    )


def get_e621_tag_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://e621.net/tags.json?limit=320&search[order]=date',
        page_type='by_id',
        page_field='page',
        page_field_prefix='b',
        json_field=None
    )


def get_e621_tag_aliases_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://e621.net/tag_aliases.json?limit=320&search[order]=date',
        page_type='by_id',
        page_field='page',
        page_field_prefix='b',
        json_field=None
    )


def get_e621_implications_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://e621.net/tag_implications.json?limit=320',
        page_type='index',
        page_field='page',
        json_field=None
    )


def get_gelbooru_search_crawler(output_file: str, search_query: str):
    return Crawler(
        output_file=output_file,
        base_url='https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=100&tags=' + urllib.parse.quote(search_query),
        page_type='index',
        page_field='pid',
        json_field='post'
    )


def get_gelbooru_index_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=100',
        page_type='index',
        page_field='pid',
        json_field='post'
    )


def get_gelbooru_tag_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://gelbooru.com/index.php?page=dapi&s=tag&q=index&json=1&limit=100',
        page_type='index',
        page_field='pid',
        json_field='tag'
    )


def get_danbooru_search_crawler(output_file: str, search_query: str):
    return Crawler(
        output_file=output_file,
        base_url='https://danbooru.donmai.us/posts.json?limit=200&tags=' + urllib.parse.quote(search_query),
        page_type='index',
        page_field='page',
        json_field=None
    )


def get_danbooru_index_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://danbooru.donmai.us/posts.json?limit=200',
        page_type='by_id',
        page_field='page',
        page_field_prefix='b',
        json_field=None
    )


def get_danbooru_tag_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://danbooru.donmai.us/tags.json?limit=200',
        page_type='index',
        page_field='page',
        json_field=None
    )


def get_rule34_search_crawler(output_file: str, search_query: str):
    return Crawler(
        output_file=output_file,
        base_url='https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&limit=1000&json=1&tags=' + urllib.parse.quote(search_query),
        page_type='index',
        page_field='pid',
        json_field=None
    )


def get_rule34_index_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&limit=1000&json=1',
        page_type='index',
        page_field='pid',
        json_field=None
    )


def get_rule34_tag_crawler(output_file: str):
    return Crawler(
        output_file=output_file,
        base_url='https://api.rule34.xxx/index.php?page=dapi&s=tag&q=index&limit=100&json=1',
        page_type='index',
        page_field='pid',
        json_field=None
    )


def get_crawler(source: str, type: str, output_file: str, search_query: Optional[str]) -> Crawler:
    if source == 'e926':
        if type == 'posts':
            return get_e926_index_crawler(output_file)
        elif type == 'search':
            return get_e926_search_crawler(output_file, search_query)
        elif type == 'tags':
            return get_e926_tag_crawler(output_file)
        elif type == 'implications':
            return get_e926_implications_crawler(output_file)
        elif type == 'aliases':
            return get_e621_tag_aliases_crawler(output_file)
    elif source == 'e621':
        if type == 'posts':
            return get_e621_index_crawler(output_file)
        elif type == 'search':
            return get_e621_search_crawler(output_file, search_query)
        elif type == 'tags':
            return get_e621_tag_crawler(output_file)
        elif type == 'implications':
            return get_e621_implications_crawler(output_file)
        elif type == 'aliases':
            return get_e621_tag_aliases_crawler(output_file)
    elif source == 'gelbooru':
        if type == 'posts':
            return get_gelbooru_index_crawler(output_file)
        elif type == 'search':
            return get_gelbooru_search_crawler(output_file, search_query)
        elif type == 'tags':
            return get_gelbooru_tag_crawler(output_file)
    elif source == 'danbooru':
        if type == 'index':
            return get_danbooru_index_crawler(output_file)
        elif type == 'search':
            return get_danbooru_search_crawler(output_file, search_query)
        elif type == 'tags':
            return get_danbooru_tag_crawler(output_file)
    elif source == 'rule34':
        if type == 'index':
            return get_rule34_index_crawler(output_file)
        elif type == 'search':
            return get_rule34_search_crawler(output_file, search_query)
        elif type == 'tags':
            return get_rule34_tag_crawler(output_file)

    raise NotImplementedError(f'Unsupported source (\'{source}\') or type (\'{type}\')')
