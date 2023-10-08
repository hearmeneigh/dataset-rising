from datetime import datetime
from typing import Optional
import os

from database.utils.enums import Source, Rating
from database.entities.post import PostEntity
from database.translator.translator import PostTranslator


class DanbooruPostTranslator(PostTranslator):
    def translate(self, data: dict) -> Optional[PostEntity]:
        score = int(data.get('score', 0))
        favorites = int(data.get('fav_count', 0))
        comments = int(data.get('comment_count', 0))

        p = PostEntity()

        p.source = Source.DANBOORU
        p.source_id = str(data.get('id'))

        p.rating = data.get('rating', 'e')

        all_tags = data.get('tag_string', '').split(' ')
        p.tags = self.normalize_tags(all_tags)

        filename = data.get('image', data.get('file_url'))

        if filename is None:
            return None

        p.origin_urls = [data.get('source')]
        p.origin_md5 = data.get('md5')
        p.origin_format = os.path.splitext(filename)[1][1:]
        p.origin_size = None  # file.get('size')

        p.image_url = data.get('file_url')
        p.image_width = data.get('image_width')
        p.image_height = data.get('image_height')
        p.image_ratio = round(p.image_width / p.image_height, 2)

        small_url = data.get('preview_file_url', data.get('sample_url', data.get('file_url')))
        small_width = data.get('preview_width', data.get('sample_width', data.get('image_width')))
        small_height = data.get('preview_height', data.get('sample_height', data.get('image_height')))

        p.small_url = small_url
        p.small_width = small_width
        p.small_height = small_height

        medium_url = data.get('large_file_url', data.get('file_url'))
        medium_width = data.get('sample_width', data.get('image_width'))
        medium_height = data.get('sample_height', data.get('image_height'))

        p.medium_url = medium_url
        p.medium_width = medium_width
        p.medium_height = medium_height

        p.score = score
        p.favorites_count = favorites
        p.comment_count = comments
        # view count not available

        p.created_at = datetime.strptime(data.get('created_at'), '%Y-%m-%dT%H:%M:%S.%f%z')
        p.timestamp = datetime.now()

        return p
