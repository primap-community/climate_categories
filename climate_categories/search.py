from typing import Iterable, List, Tuple

from . import _categories


def search(
    code: str, cats: Iterable[_categories.Categorization]
) -> List[Tuple[str, str]]:
    """Search for the given code in the given categorizations."""
    raise NotImplementedError
