#  Copyright (c) 2021. fit&healthy 365
from itertools import chain


def flatten(not_flat):
    flat = list(chain.from_iterable(not_flat))
    return flat
