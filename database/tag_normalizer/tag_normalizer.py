import re
from datetime import datetime
from typing import List, Dict, Union, Optional, Callable

from anyascii import anyascii

from entities.post import PostEntity
from utils.enums import Category, category_naming_order, Source, Rating
from entities.tag import TagEntity, TagProtoEntity, TagAlias, TagVersion
from utils.progress import Progress

scoreAboveMilestones = [250, 500, 1000, 1500, 2000]
scoreBelowMilestones = [0, 25, 50, 100, 250]
favAboveMilestones = [1000, 2000, 3000, 4000]
favBelowMilestones = [25, 50, 100, 250, 500, 1000]
ratingMilestones = [Rating.SAFE, Rating.QUESTIONABLE, Rating.EXPLICIT]

long_name_categories = [Category.SYMBOL, Category.ASPECT_RATIO, Category.SCORE, Category.FAVORITES, Category.RATING, Category.COMMENTS, Category.VIEWS, Category.DESCRIPTION, Category.RISING]

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

    # tag reference_name => TagEntity
    original_map: Dict[str, TagEntity] = {}

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

    def load(self, read_tag_cb: Callable[[], Optional[TagProtoEntity]]):
        progress = Progress(title='Loading tags', units='tags')
        tag_count = 0
        prefilter_count = 0
        recategorize_count = 0
        symbol_count = 0
        aspect_ratio_count = 0
        rewrite_count = 0

        while (proto_tag := read_tag_cb()) is not None:
            tag_count += 1
            progress.update(tag_count)

            if proto_tag.category == Category.INVALID:
                continue

            if proto_tag.origin_name in self.prefilter:
                prefilter_count += 1
                continue

            if proto_tag.category == Category.GENERAL:
                for category in [Category.ARTIST, Category.CHARACTER, Category.COPYRIGHT, Category.SPECIES]:
                    if re.match(r'^.*_\(' + re.escape(category) + r'\)$', proto_tag.origin_name) or re.match(r'^.*_' + re.escape(category) + r'$', proto_tag.origin_name):
                        # proto_tag.reference_name = proto_tag.reference_name.replace(f'_({category})', '')
                        # proto_tag.origin_name = proto_tag.origin_name.replace(f'_({category})', '')
                        recategorize_count += 1
                        proto_tag.category = category
                        proto_tag.renamed = True

            if proto_tag.origin_name in self.rewrites:
                rewrite_count += 1
                rw = self.rewrites[proto_tag.origin_name]

                if type(rw) is dict:
                    proto_tag.origin_name = rw.get('name', proto_tag.origin_name)
                    proto_tag.source_id = rw.get('source_id', proto_tag.source_id)
                else:
                    # shortcut
                    proto_tag.origin_name = rw

            v1_tag = self.to_v1_tag(proto_tag)
            v2_tag = self.to_v2_tag(proto_tag)
            v2_tag_short = self.to_v2_tag(proto_tag, True)

            if proto_tag.reference_name in self.symbols:
                proto_tag.category = Category.SYMBOL
                v1_tag = proto_tag.reference_name
                v2_tag = proto_tag.reference_name
                v2_tag_short = proto_tag.reference_name
                symbol_count += 1

            if proto_tag.reference_name in self.aspect_ratios:
                proto_tag.category = Category.ASPECT_RATIO
                v1_tag = proto_tag.reference_name.replace(':', '_')
                v2_tag = v1_tag
                v2_tag_short = v1_tag
                aspect_ratio_count += 1

            self.add_tag(v1_tag, proto_tag, TagVersion.V1)
            self.add_tag(v2_tag, proto_tag, TagVersion.V2)

            if v2_tag != v2_tag_short:
                self.add_tag(v2_tag_short, proto_tag, TagVersion.V2)

            self.add_tag(proto_tag.origin_name, proto_tag, TagVersion.V0)

        self.register_pseudo_tags()
        progress.succeed(f'{tag_count} tags loaded; {prefilter_count} filtered, {rewrite_count} rewritten, and {recategorize_count} recategorized; {symbol_count} symbols and {aspect_ratio_count} aspect ratios')

    def add_tag(self, tag_alias: str, proto_tag: TagProtoEntity, version: TagVersion):
        try:
            tag_alias = self.clean(tag_alias)
            tag = self.register_tag_reference(proto_tag)
            tag_id = self.get_unique_tag_id(proto_tag)

            if tag_alias not in self.alias_map:
                self.alias_map[tag_alias] = TagAlias(
                    id=self.get_unique_tag_id(tag),
                    category=proto_tag.category,
                    versions=[version],
                    tag=tag,
                    count=tag.post_count,
                    proto_tag=proto_tag
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
            print(f'Loading tag {tag_alias} failed: {str(e)} -- {str(proto_tag)}')
            raise

    def register_tag_reference(self, tag: TagProtoEntity) -> TagEntity:
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

        if t.v1_name == '' or t.v2_name == '' or t.v2_short == '' or t.preferred_name == '':
            print(f'Tag converts to empty tag name: {str(tag.origin_name)}')

        self.id_map[tag_id] = t
        self.original_map[tag.reference_name] = t
        return t

    def to_v2_tag(self, proto_tag: Union[TagProtoEntity, TagEntity], short: bool = False) -> str:
        if proto_tag.category is None:
            return proto_tag.origin_name

        if proto_tag.category in long_name_categories:
            return proto_tag.origin_name

        tag_name = self.clean_proto_name(proto_tag.origin_name)

        cleaned_name = self.strip_specials(tag_name, str(proto_tag.category.value))
        v1_name = self.to_v1_tag(proto_tag)

        if v1_name[0:7] == 'symbol:':
            cleaned_name = proto_tag.origin_name

        if short:
            return cleaned_name

        suffix = ''

        if proto_tag.category != Category.GENERAL:
            suffix = f'_{proto_tag.category.value}'

        return f'{cleaned_name}{suffix}'

    def to_v1_tag(self, proto_tag: Union[TagProtoEntity, TagEntity]) -> str:
        prefix = ''
        tag_name = self.clean_proto_name(proto_tag.origin_name)

        if proto_tag.category is None:
            return tag_name

        if proto_tag.category in long_name_categories:
            return proto_tag.origin_name

        tag_category = proto_tag.category.value

        if tag_category != Category.GENERAL:
            prefix = f'{tag_category}:'

        cleaned_name = self.strip_specials(tag_name, str(tag_category))
        special_naming = self.get_special_naming_convention(proto_tag)

        if special_naming is not None:
            cleaned_name = special_naming

        return f'{prefix}{cleaned_name}'

    def normalize(self, tag_version_format: TagVersion):
        tag_count = 0
        tag_total = len(self.id_map)
        progress = Progress('Normalizing tags', units='tags')
        clashes = {}
        significant_tag_post_count_threshold = 1
        merge_count = 0

        for tag in self.id_map.copy().values():
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
                if v2_name_short in self.alias_map and self.alias_map[v2_name_short].tag is tag:
                    tag.preferred_name = v2_name_short

                if v2_name_long not in self.alias_map:
                    raise KeyError(v2_name_long)

                if self.alias_map[v2_name_long].tag is not tag:
                    old_tag = self.alias_map[v2_name_long].tag
                    old_v2_name_long = self.to_v2_tag(old_tag)

                    if old_v2_name_long == v2_name_long:
                        clashes[v2_name_long] = True
                        merge_count += 1

                        # can be merged?
                        if tag.v2_name == old_tag.v2_name and tag.category == old_tag.category:
                            removed_tag = tag if tag.post_count <= old_tag.post_count else old_tag
                            preserved_tag = old_tag if tag.post_count <= old_tag.post_count else tag

                            self.id_map.pop(self.get_unique_tag_id(removed_tag))

                            for alias in [removed_tag.v1_name, removed_tag.v2_name, removed_tag.v2_short, removed_tag.origin_name]:
                                if alias in self.alias_map and self.alias_map[alias].tag == removed_tag:
                                    old_alias = self.alias_map[alias]

                                    self.alias_map[alias] = TagAlias(
                                        id=self.get_unique_tag_id(preserved_tag),
                                        category=preserved_tag.category,
                                        versions=old_alias.versions,
                                        tag=preserved_tag,
                                        count=preserved_tag.post_count
                                    )

                            if preserved_tag.post_count >= significant_tag_post_count_threshold or removed_tag.post_count >= significant_tag_post_count_threshold:
                                print(f'Merged tags: "{preserved_tag.origin_name}" and "{removed_tag.origin_name}" have been merged together as "{preserved_tag.preferred_name}". Use rewrite or prefilter rules to resolve this conflict if necessary.')

                            continue
                        else:
                            pass
                    else:
                        pass

                    if self.alias_map[old_v2_name_long].tag is not old_tag:
                        if old_tag.post_count >= significant_tag_post_count_threshold:
                            raise ValueError(v2_name_long)

                    self.alias_map[v2_name_long] = TagAlias(
                        id=self.get_unique_tag_id(tag),
                        category=tag.category,
                        versions=[TagVersion.V2],
                        tag=tag,
                        count=tag.post_count
                    )

                    old_tag.preferred_name = old_v2_name_long

                tag.preferred_name = v2_name_long

        self.determine_short_names()

        progress.succeed(f'{tag_count} tags normalized, {merge_count} merged')

    def determine_short_names(self):
        for tag in self.id_map.values():
            v2_name_short = self.to_v2_tag(tag, short=True)

            if v2_name_short not in self.alias_map:
                self.alias_map[v2_name_short] = TagAlias(
                    id=self.get_unique_tag_id(tag),
                    category=tag.category,
                    versions=[TagVersion.V2],
                    tag=tag,
                    count=tag.post_count
                )

                tag.preferred_name = v2_name_short
                tag.v2_short = v2_name_short
                print(f'Preferring "{tag.v2_short}" for "{tag.origin_name}" ({tag.category})')

            elif self.alias_map[v2_name_short].tag is not tag:
                old_tag = self.alias_map[v2_name_short].tag

                if old_tag.v2_name == v2_name_short:
                    continue

                if category_naming_order[tag.category] < category_naming_order[old_tag.category]:
                    if old_tag.v2_name not in self.alias_map or self.alias_map[old_tag.v2_name] is not old_tag:
                        self.alias_map[old_tag.v2_name] = TagAlias(
                            id=self.get_unique_tag_id(old_tag),
                            category=old_tag.category,
                            versions=[TagVersion.V2],
                            tag=old_tag,
                            count=old_tag.post_count
                        )
                        old_tag.preferred_name = old_tag.v2_name
                        print(f'Switching "{old_tag.origin_name}" ({old_tag.category}) to "{old_tag.preferred_name}"')

                    self.alias_map[v2_name_short] = TagAlias(
                        id=self.get_unique_tag_id(tag),
                        category=tag.category,
                        versions=[TagVersion.V2],
                        tag=tag,
                        count=tag.post_count
                    )

                    tag.preferred_name = v2_name_short
                    tag.v2_short = v2_name_short
                    print(f'Preferring "{tag.v2_short}" for "{tag.origin_name}" ({tag.category})')
            elif self.alias_map[v2_name_short].tag is tag:
                tag.preferred_name = v2_name_short

    def get_special_naming_convention(self, tag: Union[TagProtoEntity, TagEntity]) -> Optional[str]:
        if tag.category == Category.META and tag.origin_name in self.aspect_ratios:
            cleaned = tag.origin_name.replace(':', '_')
            return f'aspect_ratio:{cleaned}'

        if tag.category == Category.GENERAL and tag.origin_name in self.symbols:
            return f'symbol:{tag.origin_name}'

        return None

    def strip_specials(self, tag_name: str, category_name: str) -> str:
        tag_name = tag_name.replace(f'_({category_name})', '').replace('_(western_artist)', '')
        full_name = re.sub(r'[^a-z0-9_/]', '', tag_name)
        return re.sub(r'_{2,32}', '_', full_name.strip('_'))

    def clean(self, tag: str) -> str:
        return tag.strip().lower() ## no regex here, so it's v0 compatible

    def clean_proto_name(self, proto_name: str) -> str:
        return anyascii(proto_name.replace('♂', '_male').replace('♀', '_female')).strip().lower()

    def get_unique_tag_id(self, tag: Union[TagProtoEntity, TagEntity]) -> str:
        return f'{tag.source.value}___{tag.source_id}'

    def get_category_naming_order(self, category: Category) -> int:
        return category_naming_order[category.value]

    def save(self, write_tag_cb: Callable[[TagEntity], None]):
        for tag in self.id_map.values():
            write_tag_cb(tag)

    def get_by_original_name(self, tag_name: str) -> Optional[TagEntity]:
        return self.original_map.get(tag_name, None)

    def get(self, tag_name: str) -> Optional[TagEntity]:
        alias = self.alias_map.get(tag_name, None)

        if alias is None:
            return None

        return alias.tag

    def get_pseudo_tags(self, post: PostEntity) -> List[str]:
        score = post.score
        favorites = post.favorites_count
        rating = post.rating

        tags = []

        for threshold in scoreAboveMilestones:
            if score > threshold:
                tags.append(f'score_above_{threshold}')

        for threshold in scoreBelowMilestones:
            if score < threshold:
                tags.append(f'score_below_{threshold}')

        for threshold in favAboveMilestones:
            if favorites > threshold:
                tags.append(f'favorites_above_{threshold}')

        for threshold in favBelowMilestones:
            if favorites < threshold:
                tags.append(f'favorites_below_{threshold}')

        if rating == Rating.SAFE:
            tags.append(f'rating_safe')

        if rating == Rating.QUESTIONABLE:
            tags.append(f'rating_questionable')

        if rating == Rating.EXPLICIT:
            tags.append(f'rating_explicit')

        if score > 1500 and favorites > 3000:
            tags.append('rising_masterpiece')

        if score is not None and score < 10 and favorites is not None and favorites < 10:
            tags.append('rising_unpopular')

        return tags

    def register_pseudo_tags(self):
        for threshold in scoreAboveMilestones:
            self.add_tag(f'score_above_{threshold}', TagProtoEntity(
                origin_name=f'score_above_{threshold}',
                reference_name=f'score_above_{threshold}',
                category=Category.SCORE,
                source=Source.RISING,
                source_id=f'score_above_{threshold}',
                post_count=0
            ), TagVersion.V2)

        for threshold in scoreBelowMilestones:
            self.add_tag(f'score_below_{threshold}', TagProtoEntity(
                origin_name=f'score_below_{threshold}',
                reference_name=f'score_below_{threshold}',
                category=Category.SCORE,
                source=Source.RISING,
                source_id=f'score_below_{threshold}',
                post_count=0
            ), TagVersion.V2)

        for threshold in favAboveMilestones:
            self.add_tag(f'favorites_above_{threshold}', TagProtoEntity(
                origin_name=f'favorites_above_{threshold}',
                reference_name=f'favorites_above_{threshold}',
                category=Category.FAVORITES,
                source=Source.RISING,
                source_id=f'favorites_above_{threshold}',
                post_count=0
            ), TagVersion.V2)

        for threshold in favBelowMilestones:
            self.add_tag(f'favorites_below_{threshold}', TagProtoEntity(
                origin_name=f'favorites_below_{threshold}',
                reference_name=f'favorites_below_{threshold}',
                category=Category.FAVORITES,
                source=Source.RISING,
                source_id=f'favorites_below_{threshold}',
                post_count=0
            ), TagVersion.V2)

        for rating in ratingMilestones:
            if rating == Rating.EXPLICIT:
                rating_str = 'explicit'
            elif rating == Rating.QUESTIONABLE:
                rating_str = 'questionable'
            elif rating == Rating.SAFE:
                rating_str = 'safe'
            else:
                rating_str = 'unknown'

            self.add_tag(f'rating_{rating_str}', TagProtoEntity(
                origin_name=f'rating_{rating_str}',
                reference_name=f'rating_{rating_str}',
                category=Category.RATING,
                source=Source.RISING,
                source_id=f'rating_{rating_str}',
                post_count=0
            ), TagVersion.V2)

        for rising_type in ['masterpiece', 'unpopular']:
            self.add_tag(f'rising_{rising_type}', TagProtoEntity(
                origin_name=f'rising_{rising_type}',
                reference_name=f'rising_{rising_type}',
                category=Category.RISING,
                source=Source.RISING,
                source_id=f'rising_{rising_type}',
                post_count=0
            ), TagVersion.V2)
