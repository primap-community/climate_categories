"""Access to all categorizations is provided directly at the module level, using the
names of categorizations. To access the example categorization `Excat`, simply use
`climate_categories.Excat` .
"""

__author__ = """Mika Pflüger"""
__email__ = "mika.pflueger@pik-potsdam.de"
__version__ = "0.5.0"

import importlib
import importlib.resources
import typing

from . import _categories, data, search
from ._categories import from_spec  # noqa: F401
from ._categories import from_yaml  # noqa: F401
from ._categories import Categorization, HierarchicalCategorization, from_pickle

cats = {}


def _read_pickle_hier(name) -> HierarchicalCategorization:
    with importlib.resources.open_binary(data, f"{name}.pickle") as fd:
        _cat = from_pickle(fd)
    cats[_cat.name] = _cat
    return _cat


def _read_pickle_nh(name) -> Categorization:
    with importlib.resources.open_binary(data, f"{name}.pickle") as fd:
        _cat = from_pickle(fd)
    cats[_cat.name] = _cat
    return _cat


# do this explicitly to help static analysis tools
IPCC1996 = _read_pickle_hier("IPCC1996")
IPCC2006 = _read_pickle_hier("IPCC2006")


def find_code(code: str) -> typing.Set[_categories.Category]:
    """Search for the given code in all included categorizations."""
    return search.search_code(code, cats.values())


__all__ = [
    "cats",
    "Categorization",
    "HierarchicalCategorization",
    "find_code",
    "from_pickle",
    "from_spec",
    "from_yaml",
] + list(cats.keys())
