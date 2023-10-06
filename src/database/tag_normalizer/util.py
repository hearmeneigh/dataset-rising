from typing import Dict

from pymongo.database import Database

from database.entities.tag import TagEntity, TagVersion
from database.tag_normalizer.tag_normalizer import TagNormalizer
from database.utils.enums import Category
from utils.progress import Progress


def load_normalizer_from_database(db: Database, category_naming_order: Dict[Category, int] = None):
    progress = Progress('Loading tags', 'tags')
    tag_normalizer = TagNormalizer(category_naming_order=category_naming_order)

    for tag in db['tags'].find(filter={}):
        progress.update()
        tag_entity = TagEntity(tag)
        tag_normalizer.add_database_tag(tag_entity, TagVersion.V2)

    progress.succeed(f'{progress.count} tags loaded')
    return tag_normalizer

