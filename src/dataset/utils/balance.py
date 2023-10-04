import math
from typing import List

from dataset.utils.selection_source import SelectionSource


def balance_selections(selections: List[SelectionSource]):
    total_ratio = math.fsum([sel.ratio for sel in selections])
    total_posts = sum([len(sel.posts) for sel in selections])

    intended_sizes = [(round(sel.ratio / total_ratio * total_posts), len(sel.posts)) for sel in selections]
    multiplier = 1

    for (intended, real) in intended_sizes:
        if real/intended < multiplier:
            multiplier = real/intended

    for selection in selections:
        intended_size = round(selection.ratio / total_ratio * total_posts * multiplier)

        if intended_size > len(selection.posts):
            intended_size = len(selection.posts)

        if intended_size < len(selection.posts):
            print(
                f'WARNING: Selection {selection.filename} has {len(selection.posts)} posts, but could only use {intended_size} of them due to ratio limits. Additional posts were discarded.'
            )

        selection.posts = selection.posts[0:intended_size]
