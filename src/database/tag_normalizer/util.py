from pymongo.database import Database

from database.entities.tag import TagEntity, TagVersion
from database.tag_normalizer.tag_normalizer import TagNormalizer
from utils.progress import Progress


def load_normalizer_from_database(db: Database):
    progress = Progress('Loading tags', 'tags')
    tag_normalizer = TagNormalizer()

    for tag in db['tags'].find({}):
        progress.update()
        tag_entity = TagEntity(tag)
        tag_normalizer.add_database_tag(tag_entity, TagVersion.V2)

    progress.succeed(f'{progress.count} tags loaded')
