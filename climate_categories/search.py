from collections.abc import Iterable

from . import _categories


def search_code(
    code: str, cats: Iterable[_categories.Categorization]
) -> set[_categories.Category]:
    """Search for the given code in the given categorizations."""
    return {cat[code] for cat in cats if code in cat.all_keys()}
