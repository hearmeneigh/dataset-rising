import urllib.parse
from typing import Optional

from database.entities.post import PostEntity
from database.entities.tag import TagEntity
from database.utils.enums import Source


def get_tag_url(tag: TagEntity) -> Optional[str]:
    if tag.source == Source.E621:
        return f'https://e621.net/posts?tags={urllib.parse.quote(tag.reference_name)}'  # yes, posts

    return None


def get_post_url(post: PostEntity) -> Optional[str]:
    if post.source == Source.E621:
        return f'https://e621.net/posts/{urllib.parse.quote(post.source_id)}'

    return post.image_url

