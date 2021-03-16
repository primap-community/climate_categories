"""Access to all categorizations is provided directly at the module level, using the
names of categorizations. To access the example categorization `Excat`, simply use
`climate_categories.Excat` .
"""

__author__ = """Mika Pflüger"""
__email__ = "mika.pflueger@pik-potsdam.de"
__version__ = "0.3.0"

import importlib
import importlib.resources
import typing

from . import data, search
from ._categories import Categorization  # noqa: F401
from ._categories import HierarchicalCategorization  # noqa: F401
from ._categories import from_pickle  # noqa: F401
from ._categories import from_spec  # noqa: F401
from ._categories import from_yaml  # noqa: F401

cats = {}

# read in all categorizations delivered in data/ as pickles
for resource in importlib.resources.contents(data):
    if resource.endswith(".pickle"):
        with importlib.resources.open_binary(data, resource) as fd:
            _cat = from_pickle(fd)
            cats[_cat.name] = _cat
            globals()[_cat.name] = _cat


def find(code: str) -> typing.List[typing.Tuple[str, str]]:
    """Find the given code in all known categorizations."""
    return search.search(code, cats.values())


__all__ = [
    "cats",
    "Categorization",
    "HierarchicalCategorization",
    "find",
    "from_pickle",
    "from_spec",
    "from_yaml",
] + list(cats.keys())
