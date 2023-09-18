from typing import List, Dict

from database.entities.post import PostEntity


def prune_and_filter_tags(posts: List[PostEntity], prefilters: Dict[str, bool], min_posts_per_tag: int):
    tag_counts = {}

    for post in posts:
        for tag in post.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return {key: value for key, value in tag_counts.items() if value >= min_posts_per_tag and key not in prefilters}
