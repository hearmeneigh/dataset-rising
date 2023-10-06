from typing import Optional, Dict, List

from database.translator.danbooru_translator import DanbooruPostTranslator
from database.translator.gelbooru_translator import GelbooruPostTranslator
from database.translator.rule34_translator import Rule34PostTranslator
from database.utils.enums import Source
from database.tag_normalizer.tag_normalizer import TagNormalizer
from database.translator.e621_translator import E621PostTranslator, E621TagTranslator, E621AliasTranslator
from database.translator.translator import PostTranslator, TagTranslator, AliasTranslator


def get_post_translator(source: Source, tag_normalizer: TagNormalizer, deep_tag_search: bool = False) -> PostTranslator:
    if source == Source.E621:
        return E621PostTranslator(tag_normalizer, deep_tag_search=deep_tag_search)
    elif source == Source.RULE34:
        return Rule34PostTranslator(tag_normalizer, deep_tag_search=deep_tag_search)
    elif source == Source.GELBOORU:
        return GelbooruPostTranslator(tag_normalizer, deep_tag_search=deep_tag_search)
    elif source == Source.DANBOORU:
        return DanbooruPostTranslator(tag_normalizer, deep_tag_search=deep_tag_search)

    raise NotImplementedError(f'Unsupported post translator source (\'{source}\')')


def get_tag_translator(source: Source, aliases: Optional[Dict[str, List[str]]]) -> TagTranslator:
    if source == Source.E621:
        return E621TagTranslator(aliases=aliases)

    raise NotImplementedError(f'Unsupported tag translator source (\'{source}\')')


def get_alias_translator(source: Source) -> AliasTranslator:
    if source == Source.E621:
        return E621AliasTranslator()

    raise NotImplementedError(f'Unsupported alias translator source (\'{source}\')')
