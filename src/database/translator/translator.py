from typing import Union, List, Optional, Dict

from database.entities.implication import ImplicationEntity
from database.entities.post import PostEntity
from database.entities.tag import TagEntity, TagProtoEntity
from database.tag_normalizer.tag_normalizer import TagNormalizer


class Translator:
    def translate(self, data: dict) -> Union[PostEntity, TagEntity, ImplicationEntity]:
        raise NotImplementedError()


class PostTranslator(Translator):
    def __init__(self, tag_normalizer: TagNormalizer):
        self.tag_normalizer = tag_normalizer

    def translate(self, data: dict) -> PostEntity:
        raise NotImplementedError()

    def normalize_tags(self, tags: List[str]) -> List[str]:
        rewritten_tags = [self.normalize_tag(tag) for tag in tags]
        included_tags = [x for x in rewritten_tags if x is not None]
        return included_tags

    def normalize_tag(self, tag_name) -> Optional[str]:
        tag = self.tag_normalizer.get_by_original_name(tag_name)

        if tag is None:
            return None

        return tag.preferred_name


class TagTranslator(Translator):
    def __init__(self, aliases: Optional[Dict[str, List[str]]]):
        self.aliases = aliases or {}

    def find_aliases(self, tag_name: str) -> Optional[List[str]]:
        return self.aliases.get(tag_name)

    def translate(self, data: dict) -> TagProtoEntity:
        raise NotImplementedError()


class ImplicationTranslator(Translator):
    def translate(self, data: dict) -> ImplicationEntity:
        raise NotImplementedError()


class AliasTranslator(Translator):
    def translate(self, data: dict) -> AliasEntity:
        raise NotImplementedError()
