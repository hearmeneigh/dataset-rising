import json
import re
import os
from typing import List

from database.entities.post import PostEntity


class SelectionSource:
    def __init__(self, filename_with_ratio: str):
        match = re.match(r'^(.*):([0-9.]+%|\*)$', filename_with_ratio)

        if match is None:
            filename = filename_with_ratio
            ratio = 1.0
        else:
            filename = match.group(1)

            if match.group(2) == '*':
                ratio = 'fixed'
            else:
                ratio = float(match.group(2)[:-1]) / 100.0

        self.filename = filename
        self.ratio = ratio
        self.posts = self.load(filename)

    def load(self, filename: str) -> List[PostEntity]:
        posts = []
        selector_name = os.path.splitext(os.path.basename(filename))[0]

        with open(filename, 'r') as fp:
            for line in fp:
                p = PostEntity(json.loads(line))
                p.selector = selector_name

                posts.append(p)

        return posts

