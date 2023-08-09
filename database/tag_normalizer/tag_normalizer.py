import re
from datetime import datetime
from typing import List, Dict, Union, Optional, Callable

from anyascii import anyascii

from database.utils.enums import Category, category_naming_order
from database.entities.tag import TagEntity, TagPseudoEntity, TagAlias, TagVersion
from database.utils.progress import Progress


# Manages v0, v1, v2, and v2 short tag namespaces
# and mitigates conflicts between the tag names
#
# Any TagEntity added to TagNormalizer will have its
# tag names normalized and overwritten.
class TagNormalizer:
    # alias name => { id, versions, count, tag }
    alias_map: Dict[str, TagAlias] = {}

    # tag id => TagEntity
    id_map: Dict[str, TagEntity] = {}

    # determines which tag gets the preferred no-prefix name
    category_naming_order: Dict[Category, int] = category_naming_order

    def __init__(self, prefilter: Dict[str, bool] = None, symbols: List[str] = None, aspect_ratios: List[str] = None, rewrites: Dict[str, dict] = None):
        if prefilter is None:
            prefilter = {}

        if symbols is None:
            symbols = []

        if aspect_ratios is None:
            aspect_ratios = []

        if rewrites is None:
            rewrites = {}

        self.prefilter = prefilter
        self.symbols = symbols
        self.aspect_ratios = aspect_ratios
        self.rewrites = rewrites

    def load(self, read_tag_cb: Callable[[], Optional[TagPseudoEntity]]):
        progress = Progress('Loading tags')
        tag_count = 0

        while (tag := read_tag_cb()) is not None:
            tag_count += 1
            progress.update(tag_count)

            if tag.origin_name in self.prefilter:
                continue

            if tag.origin_name in self.rewrites:
                rw = self.rewrites[tag.origin_name]

                if type(rw) is dict:
                    tag.origin_name = rw.get('name', tag.origin_name)
                    tag.source_id = rw.get('source_id', tag.source_id)
                else:
                    # shortcut
                    tag.origin_name = rw

            v1_tag = self.to_v1_tag(tag)
            v2_tag = self.to_v2_tag(tag)
            v2_tag_short = self.to_v2_tag(tag, True)

            self.add_tag(v1_tag, tag, TagVersion.V1)
            self.add_tag(v2_tag, tag, TagVersion.V2)

            if v2_tag != v2_tag_short:
                self.add_tag(v2_tag_short, tag, TagVersion.V2)

            self.add_tag(tag.origin_name, tag, TagVersion.V0)

    def add_tag(self, tag_alias: str, pseudo_tag: TagPseudoEntity, version: TagVersion):
        try:
            tag_alias = self.clean(tag_alias)
            tag = self.register_tag_reference(pseudo_tag)
            tag_id = self.get_unique_tag_id(pseudo_tag)

            if tag_alias not in self.alias_map:
                self.alias_map[tag_alias] = TagAlias(
                    id=self.get_unique_tag_id(tag),
                    category=pseudo_tag.category,
                    versions=[version],
                    tag=tag,
                    count=tag.post_count
                )

            alias_record = self.alias_map[tag_alias]

            if alias_record.id != tag_id:
                # prefer short versions of tags in lower categories (e.g. prefer GENERAL to ARTIST)
                if self.get_category_naming_order(tag.category) < self.get_category_naming_order(alias_record.category):
                    if TagVersion.V0 not in alias_record.versions:
                        # print(f'Lookup replacement: {tag_alias} -- ID {alias_record.id} => {tag_id}, category {alias_record.category.value} => {tag.category.value}')
                        self.alias_map[tag_alias] = TagAlias(id=tag_id, category=tag.category, versions=[version], tag=tag, count=tag.post_count)
                    else:
                        # print(f'V0 overrides: {tag_alias}')
                        pass
            else:
                if version not in alias_record.versions:
                    alias_record.versions.append(version)
        except Exception as e:
            print(f'Loading tag {tag_alias} failed: {str(e)} -- {str(pseudo_tag)}')
            raise

    def register_tag_reference(self, tag: TagPseudoEntity) -> TagEntity:
        tag_id = self.get_unique_tag_id(tag)

        if tag_id in self.id_map:
            ref_tag = self.id_map[tag_id]

            if ref_tag.origin_name != tag.origin_name:
                print(f'Tag clash between "{tag.origin_name}" and "{ref_tag.origin_name}" -- both have same ID and source')
                raise KeyError()

            return ref_tag

        t = TagEntity()

        t.source = tag.source
        t.source_id = tag.source_id
        t.origin_name = tag.origin_name
        t.category = tag.category
        t.v1_name = self.to_v1_tag(tag)
        t.v2_name = self.to_v2_tag(tag)
        t.v2_short = self.to_v2_tag(tag, short=True)
        t.id_name = t.v2_name
        t.preferred_name = t.v2_name
        t.reference_name = tag.reference_name
        t.post_count = tag.post_count
        t.timestamp = datetime.now()

        self.id_map[tag_id] = t
        return t

    def to_v2_tag(self, pseudo_tag: Union[TagPseudoEntity, TagEntity], short: bool = False) -> str:
        if pseudo_tag.category is None:
            return pseudo_tag.origin_name

        tag_name = self.clean_pseudo_name(pseudo_tag.origin_name)

        cleaned_name = self.strip_specials(tag_name, str(pseudo_tag.category.value))
        v1_name = self.to_v1_tag(pseudo_tag)

        if v1_name[0:7] == 'symbol:':
            cleaned_name = pseudo_tag.origin_name

        if short:
            return cleaned_name

        suffix = ''

        if pseudo_tag.category != Category.GENERAL:
            suffix = f'_{pseudo_tag.category.value}'

        return f'{cleaned_name}{suffix}'

    def to_v1_tag(self, pseudo_tag: Union[TagPseudoEntity, TagEntity]) -> str:
        prefix = ''
        tag_name = self.clean_pseudo_name(pseudo_tag.origin_name)

        if pseudo_tag.category is None:
            return tag_name

        tag_category = pseudo_tag.category.value

        if tag_category != Category.GENERAL:
            prefix = f'{tag_category}:'

        cleaned_name = self.strip_specials(tag_name, str(tag_category))
        special_naming = self.get_special_naming_convention(pseudo_tag)

        if special_naming is not None:
            cleaned_name = special_naming

        return f'{prefix}{cleaned_name}'

    def normalize(self, tag_version_format: TagVersion):
        tag_count = 0
        tag_total = len(self.id_map)
        progress = Progress('Normalizing tags', total=tag_total)
        clashes = {}

        for tag in self.id_map.values():
            tag_count += 1
            progress.update(tag_count)

            v1_name = self.to_v1_tag(tag)
            v2_name_short = self.to_v2_tag(tag, short=True)
            v2_name_long = self.to_v2_tag(tag)

            if tag_version_format == TagVersion.V0:
                tag.preferred_name = tag.origin_name
            elif tag_version_format == TagVersion.V1:
                tag.preferred_name = v1_name
            else:
                if v2_name_short in self.alias_map and self.alias_map[v2_name_short] is tag:
                    tag.preferred_name = v2_name_short
                else:
                    if v2_name_long not in self.alias_map:
                        raise KeyError(v2_name_long)

                    if self.alias_map[v2_name_long].tag is not tag:
                        old_tag = self.alias_map[v2_name_long].tag
                        old_v2_name_long = self.to_v2_tag(old_tag)

                        if old_v2_name_long == v2_name_long:
                            if v2_name_long not in clashes:
                                clashes[v2_name_long] = True

                            print(f'Namespace clash: "{tag.reference_name}" ({tag.source_id}) and "{old_tag.reference_name}" ({old_tag.source_id}) cannot fit to the same namespace. Ignoring "{tag.reference_name}". Use rewrite or prefilter rules to adjust.')

                            continue
                            # raise KeyError(old_v2_name_long)

                        if self.alias_map[old_v2_name_long].tag is not old_tag:
                            raise ValueError(v2_name_long)

                        self.alias_map[v2_name_long] = TagAlias(
                            id=self.get_unique_tag_id(tag),
                            category=tag.category,
                            versions=[TagVersion.V2],
                            tag=tag,
                            count=tag.post_count
                        )

                    tag.preferred_name = v2_name_long

    def get_special_naming_convention(self, tag: Union[TagPseudoEntity, TagEntity]) -> Optional[str]:
        if tag.category == Category.META and tag.origin_name in self.aspect_ratios:
            cleaned = tag.origin_name.replace(':', '_')
            return f'aspect_ratio:{cleaned}'

        if tag.category == Category.GENERAL and tag.origin_name in self.symbols:
            return f'symbol:{tag.origin_name}'

        return None

    def strip_specials(self, tag_name: str, category_name: str) -> str:
        tag_name = tag_name.replace(f'_({category_name})', '').replace('_(western_artist)', '')
        full_name = re.sub(r'[^a-z0-9_/]', '', tag_name)
        return re.sub(r'_{2,10}', '_', full_name.strip('_'))

    def clean(self, tag: str) -> str:
        return tag.strip().lower() ## no regex here, so it's v0 compatible

    def clean_pseudo_name(self, pseudo_name: str) -> str:
        return anyascii(pseudo_name.replace('♂', '_male').replace('♀', '_female')).strip().lower()

    def get_unique_tag_id(self, tag: Union[TagPseudoEntity, TagEntity]) -> str:
        return f'{tag.source.value}___{tag.source_id}'

    def get_category_naming_order(self, category: Category) -> int:
        return category_naming_order[category.value]

    def save(self, write_tag_cb: Callable[[TagEntity], None]):
        for tag in self.id_map.values():
            write_tag_cb(tag)

    def get(self, tag_name: str) -> Optional[TagEntity]:
        return self.alias_map.get(tag_name, None)
