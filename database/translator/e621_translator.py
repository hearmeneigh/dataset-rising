from datetime import datetime

from database.utils.enums import Source
from database.entities.post import PostEntity
from database.translator.translator import PostTranslator


class E621PostTranslator(PostTranslator):
    def translate(self, data: dict) -> PostEntity:
        file = data.get('file', {})
        preview = data.get('preview', {})
        sample = data.get('sample', {})
        score = data.get('score', {})

        p = PostEntity()

        p.source = Source.E621
        p.source_id = str(data['id'])

        p.rating = data['rating']
        p.tags = self.normalize_tags(data['tags'])

        p.description = data['description']

        p.origin_urls = data['sources']
        p.origin_md5 = file.get('md5')
        p.origin_format = file.get('ext')
        p.origin_size = file.get('size')

        p.image_url = file.get('url')
        p.image_width = file.get('width')
        p.image_height = file.get('height')
        p.image_ratio = p.image_width / p.image_height

        p.small_url = preview.get('url')
        p.small_width = preview.get('width')
        p.small_height = preview.get('height')

        p.medium_url = sample.get('url')
        p.medium_width = sample.get('width')
        p.medium_height = sample.get('height')

        p.score = int(score.get('total', 0))
        p.favorites_count = int(data['fav_count'])
        p.comment_count = int(data['comment_count'])
        # view count not available

        p.created_at = datetime.strptime(data['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z')
        p.timestamp = datetime.now()

        return p
