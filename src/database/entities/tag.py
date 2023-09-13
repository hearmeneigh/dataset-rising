from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict

from database.utils.enums import Source, Category


class AlternativeTagSource:
    source_id: str
    source: Source


class TagProtoEntity:
    source: Source
    source_id: str
    origin_name: str
    reference_name: str  # unmodified original name, never used
    category: Category
    post_count: Optional[int]
    renamed: bool = False

    def __init__(self, source: Source, source_id: str, origin_name: str, reference_name: str, category: Category, post_count: Optional[int]):
        self.source = source
        self.source_id = source_id
        self.origin_name = origin_name
        self.reference_name = reference_name
        self.category = category
        self.post_count = post_count


class TagEntity:
    def __init__(self, tag: Optional[Dict[str, any]] = None):
        if tag is not None:
            for key in tag:
                setattr(self, key, tag[key])

    source: Source
    source_id: str

    alternative_ids: Optional[List[AlternativeTagSource]]

    id_name: str

    origin_name: str
    category: Category
    reference_name: str  # unmodified original name, never used

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
    def __init__(self, id: str, category: Category, versions: List[TagVersion], tag: TagEntity, count: Optional[int], proto_tag: Optional[TagProtoEntity] = None):
        self.id = id
        self.category = category
        self.versions = versions
        self.tag = tag
        self.count = count
        self.proto_tag = proto_tag

    id: str
    category: Category
    versions: List[TagVersion]
    tag: TagEntity
    count: Optional[int]
    proto_tag: Optional[TagProtoEntity]
