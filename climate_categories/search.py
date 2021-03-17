from typing import Iterable, Set

from . import _categories


def search_code(
    code: str, cats: Iterable[_categories.Categorization]
) -> Set[_categories.Category]:
    """Search for the given code in the given categorizations."""
    res = set()
    for cat in cats:
        if code in cat.all_keys():
            res.add(cat[code])
    return res
