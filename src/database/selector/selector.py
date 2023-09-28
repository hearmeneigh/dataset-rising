import os
import pydash
from typing import Dict, List, Union, Generator, Optional, Tuple
from pymongo.database import Database
import yaml
from yamlinclude import YamlIncludeConstructor

from database.entities.tag import TagEntity
from database.selector.selected_sample import SelectedSample
from database.utils.source_url import get_tag_url
from utils.progress import Progress

YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.FullLoader)


class Selector:
    config: Dict[str, any]
    excludes: List[str]
    includes: List[str]
    tag_map: Dict[str, TagEntity] = {}

    def __init__(self, filename: str, db: Database):
        self.filename = filename
        self.db = db
        self.load()

    def load(self):
        progress = Progress('Verifying selector tags', 'tags')
        prev_cwd = os.getcwd()

        try:
            abs_file = os.path.abspath(self.filename)
            file_path = os.path.dirname(abs_file)

            os.chdir(file_path)

            with open(abs_file, 'r') as yaml_file:
                self.config = yaml.load(yaml_file, Loader=yaml.FullLoader)

                if type(self.config) is dict:
                    yaml_includes = self.config.get('include', [])
                    yaml_excludes = self.config.get('exclude', [])
                elif type(self.config) is list:
                    yaml_includes = self.config
                    yaml_excludes = []

                proto_includes = [self.resolve_tag(k, True) for k in pydash.uniq(pydash.flatten_deep(yaml_includes))]
                proto_excludes = [self.resolve_tag(k, True) for k in pydash.uniq(pydash.flatten_deep(yaml_excludes))]

                self.excludes = [k.preferred_name for k in proto_excludes if k is not None]
                self.includes = [k.preferred_name for k in proto_includes if k is not None]

                for excluded in proto_excludes:
                    if excluded in proto_includes and excluded is not None:
                        print(f'Warning: tag "{excluded.preferred_name}" is both included and excluded in "{self.filename}"')

                progress.succeed('Selector tags verified')
        except Exception as e:
            progress.fail(f'Tag selection error: {str(e)}')
            raise e
        finally:
            os.chdir(prev_cwd)

    def resolve_tag(self, tag_name: str, with_warnings: bool) -> Union[TagEntity, None]:
        coll = self.db['tags']
        prefixes = ['v1', 'v2', 'preferred']

        try:
            parts = tag_name.split(':', 2)

            if len(parts) < 2:
                tag_prefix = None
                tag_body = tag_name
            else:
                tag_prefix = parts[0]
                tag_body = ':'.join(parts[1:])

        except ValueError:
            tag_prefix = None
            tag_body = tag_name

        if tag_body is not None and tag_prefix in prefixes:
            tag_name = tag_body

            if tag_prefix == 'preferred' and tag_name in self.tag_map:
                return self.tag_map[tag_name]

            selector = {
                '$or': [
                    {f'{tag_prefix}_name': tag_body},
                    {'id_name': tag_body}
                ]
            }
        else:
            tag_name = tag_name
            selector = {
                '$or': [
                    {'preferred_name': tag_name},
                    {'v2_name': tag_name},
                    {'v1_name': tag_name},
                    {'id_name': tag_name},
                ]
            }

        matches = list(coll.find(filter=selector))

        if len(matches) == 0:
            if with_warnings:
                print(f'Tag name "{tag_name}" not found in the database; skipping tag from the filter: {self.filename}')
            return None

        if len(matches) > 1:
            if with_warnings:
                print(f'Ambiguous tag name "{tag_name}" has {len(matches)} matches in the database – consider prefixing selector with "v1:", "v2:", or "preferred:" (e.g. "v2:{tag_name}"); skipping tag from the filter: {self.filename}')
            return None

        tag = TagEntity(matches[0])

        self.tag_map[tag.preferred_name] = tag
        return tag

    def select(self, formats: List[str] = None, limit: int = None) -> Generator[SelectedSample, None, None]:
        if formats is None:
            formats = ['jpg', 'png']

        coll = self.db['posts']

        results = coll.aggregate([
            {
                '$match': {
                    'tags': {
                        '$in': self.includes,
                        '$nin': self.excludes
                    },
                    'origin_format': {'$in': formats},
                    'image_url': {'$exists': True, '$ne': None},
                },
            },
            {
                '$addFields': {
                    'tmp_order': {'$rand': {}}
                }
            },
            {
                '$sort': {
                    'tmp_order': 1
                }
            }
        ])

        post_count = 0

        for post in results:
            try:
                post_count += 1

                post.pop('tmp_order')
                matches = [t for t in self.includes if t in post['tags']]

                p = SelectedSample(matches=matches, post=post)
                proto_tags = [self.resolve_tag(f'preferred:{tag}', True) for tag in p.tags]
                p.tags = [k.preferred_name for k in proto_tags if k is not None]

                yield p

                if limit is not None and post_count >= limit:
                    break
            except Exception as e:
                print(f'Could not load post #{post.get("source_id")} ({post.get("source")}) – skipping: {str(e)}')

    def get_samples_by_tag(self, tag_name: str, samples: int, formats: List[str], filters: List[str]) -> Tuple[List[SelectedSample], Optional[int], Optional[str]]:
        progress = Progress(f'Sampling posts for "{tag_name}"', 'selectors')
        coll = self.db['posts']
        matchers = [tag_name] + filters

        results = coll.aggregate([
            {
                '$match': {
                    'tags': {'$in': matchers},
                    'origin_format': {'$in': formats},
                    'image_url': {'$exists': True, '$ne': None},
                }
            },
            {
                '$sample': {
                    'size': samples
                }
            }
        ])

        posts = [SelectedSample(matches=[t for t in matchers if t in post['tags']], post=post) for post in results]

        tag_url = None
        total_count = None
        tag = self.db['tags'].find_one({'preferred_name': tag_name})

        if tag is not None:
            t = TagEntity(tag)
            total_count = t.post_count
            tag_url = get_tag_url(t)

        progress.succeed(f'Sampled {len(posts)} posts for "{tag_name}"')
        return posts, total_count, tag_url

    def sample_selectors(self, samples: int = 20, formats: List[str] = None, filters: List[str] = None) -> Dict[str, Dict[str, Tuple[List[SelectedSample], Optional[int], Optional[str]]]]:
        if formats is None:
            formats = ['jpg', 'png']

        if filters is None:
            filters = []

        return {
            'includes': {tag_name: self.get_samples_by_tag(tag_name, samples, formats, filters) for tag_name in self.includes},
            'excludes': {tag_name: self.get_samples_by_tag(tag_name, samples, formats, filters) for tag_name in self.excludes}
        }

    def test(self, tag_name: str) -> Optional[bool]:
        if tag_name in self.excludes:
            return False

        if tag_name in self.includes:
            return True

        return None

