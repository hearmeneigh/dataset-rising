from datetime import datetime
from enum import Enum
from typing import Optional, List

from database.utils.enums import Source, Category


class AlternativeTagSource:
    source_id: str
    source: Source


class TagPseudoEntity:
    source: Source
    source_id: str
    origin_name: str
    category: Category
    post_count: Optional[int]


class TagEntity:
    source: Source
    source_id: str

    alternative_ids: Optional[List[AlternativeTagSource]]

    id_name: str

    origin_name: str
    category: Category

    v1_name: str
    v2_name: str
    v2_short: str
    preferred_name: str

    post_count: Optional[int]

    timestamp: datetime


class TagVersion(Enum):
    V0 = 'v0'
    V1 = 'v1'
    V2 = 'v2'


class TagAlias:
    def __init__(self, id: str, category: Category, versions: List[TagVersion], tag: TagEntity, count: Optional[int]):
        self.id = id
        self.category = category
        self.versions = versions
        self.tag = tag
        self.count = count

    id: str
    category: Category
    versions: List[TagVersion]
    tag: TagEntity
    count: Optional[int]
