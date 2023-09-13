import json
import re
from typing import List

from database.entities.post import PostEntity


class SelectionSource:
    def __init__(self, filename_with_ratio: str):
        match = re.match(r'^(.*)(:[0-9.]%)$', filename_with_ratio)

        if match is None:
            filename = filename_with_ratio
            ratio = 1.0
        else:
            filename = match.group(1)
            ratio = float(match.group(2)) / 100.0

        self.filename = filename
        self.ratio = ratio
        self.posts = self.load(filename)

    def load(self, filename: str) -> List[PostEntity]:
        posts = []

        with open(filename, 'r') as fp:
            for line in fp:
                posts.append(PostEntity(json.loads(line)))

        return posts

