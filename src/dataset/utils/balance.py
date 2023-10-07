import math
from typing import List

from dataset.utils.selection_source import SelectionSource


def resolve_fixed_ratios(selections: List[SelectionSource]):
    total_dynamic_ratio = math.fsum([sel.ratio for sel in selections if sel.ratio != 'fixed'])

    if total_dynamic_ratio == 0:
        return  # nothing to do since everything is '*'

    if total_dynamic_ratio >= 1:
        raise Exception('When using a wildcard, selectors with percentage ratios must sum to less than 100%')

    total_fixed_posts = math.fsum([len(sel.posts) for sel in selections if sel.ratio == 'fixed'])
    total_fixed_ratio = 1 - total_dynamic_ratio

    for sel in selections:
        if sel.ratio == 'fixed':
            sel.ratio = total_fixed_ratio * len(sel.posts) / total_fixed_posts


def balance_selections(selections: List[SelectionSource]):
    for sel in selections:
        if sel.ratio == 'fixed':
            resolve_fixed_ratios(selections)
            break

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
                f'WARNING: Selection {selection.filename} has {len(selection.posts)} posts, but only {intended_size} were used due to ratio limits. Additional posts were discarded.'
            )

        selection.posts = selection.posts[0:intended_size]
