import math
from typing import List

from dataset.utils.selection_source import SelectionSource


def balance_selections(selections: List[SelectionSource]):
    total_ratio = math.fsum([sel.ratio for sel in selections])
    total_posts = sum([len(sel.posts) for sel in selections])

    for selection in selections:
        intended_size = round(selection.ratio / total_ratio * total_posts)

        if intended_size > len(selection.posts):
            print(
                f'WARNING: Selection {selection.filename} has {len(selection.posts)} posts, but should have > {intended_size} posts to achieve the intended ratio. Using all {len(selection.posts)} posts.')
        else:
            selection.posts = selection.posts[0:intended_size]
