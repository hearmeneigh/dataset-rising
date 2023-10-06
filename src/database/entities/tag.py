from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict

from database.utils.enums import Source, Category, to_source, to_category


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
    aliases: Optional[List[str]]

    def __init__(self, source: Source, source_id: str, origin_name: str, reference_name: str, category: Category, post_count: Optional[int], aliases: Optional[List[str]]):
        self.source = source
        self.source_id = source_id
        self.origin_name = origin_name
        self.reference_name = reference_name
        self.category = category
        self.post_count = post_count
        self.aliases = aliases


class TagEntity:
    def __init__(self, tag: Optional[Dict[str, any]] = None):
        if tag is not None:
            for key in tag:
                setattr(self, key, tag[key])

            self.source = to_source(self.source)
            self.category = to_category(self.category)

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

    aliases: Optional[List[str]]

    timestamp: datetime


class TagVersion(Enum):
    V0 = 'v0'
    V1 = 'v1'
    V2 = 'v2'


class AliasEntity:
    tag_name: str
    alias_name: str
    source: Source
    source_id: str

    def __init__(self, source: Source, source_id: str, tag_name: str, alias_name: str):
        self.source = source
        self.source_id = source_id
        self.tag_name = tag_name
        self.alias_name = alias_name



class TagRef:
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
