from typing import Optional, Dict, List

from database.utils.enums import Source
from database.tag_normalizer.tag_normalizer import TagNormalizer
from database.translator.e621_translator import E621PostTranslator, E621TagTranslator, E621AliasTranslator
from database.translator.translator import PostTranslator, TagTranslator, AliasTranslator


def get_post_translator(source: Source, tag_normalizer: TagNormalizer) -> PostTranslator:
    if source == Source.E621:
        return E621PostTranslator(tag_normalizer)

    raise NotImplementedError(f'Unsupported post translator source (\'{source}\')')


def get_tag_translator(source: Source, aliases: Optional[Dict[str, List[str]]]) -> TagTranslator:
    if source == Source.E621:
        return E621TagTranslator(aliases=aliases)

    raise NotImplementedError(f'Unsupported tag translator source (\'{source}\')')


def get_alias_translator(source: Source) -> AliasTranslator:
    if source == Source.E621:
        return E621AliasTranslator()

    raise NotImplementedError(f'Unsupported alias translator source (\'{source}\')')
