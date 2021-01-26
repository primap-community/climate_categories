from typing import Iterable, List, Tuple

from . import _categories


def search(
    code: str, cats: Iterable[_categories.Categorization]
) -> List[Tuple[str, str]]:
    """Search for the given code in the given categorizations."""
    res = []
    for cat in cats:
        if code in cat.keys():
            res.append((cat.name, cat[code]))
    return res
