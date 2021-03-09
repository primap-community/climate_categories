"""Access to all categorizations is provided directly at the module level, using the
names of categorizations. To access the example categorization `Excat`, simply use
`climate_categories.Excat` .
"""

__author__ = """Mika Pflüger"""
__email__ = "mika.pflueger@pik-potsdam.de"
__version__ = "0.2.2"

import pathlib
import typing

from . import search
from ._categories import Categorization  # noqa: F401
from ._categories import HierarchicalCategorization  # noqa: F401

_data_dir = pathlib.Path(__file__).parent / "data"

IPCC2006 = HierarchicalCategorization.from_pickle(_data_dir / "IPCC2006.pickle")

cats = {"IPCC2006": IPCC2006}


def find(code: str) -> typing.List[typing.Tuple[str, str]]:
    """Find the given code in all known categorizations."""
    return search.search(code, cats.values())


__all__ = ["cats", "Categorization", "HierarchicalCategorization", "find"] + list(
    cats.keys()
)
