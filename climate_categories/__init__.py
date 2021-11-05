"""Access to all categorizations is provided directly at the module level, using the
names of categorizations. To access the example categorization `Excat`, simply use
`climate_categories.Excat` .
"""

__author__ = """Mika Pflüger"""
__email__ = "mika.pflueger@pik-potsdam.de"
__version__ = "0.6.3"

import importlib
import importlib.resources
import typing

from . import _categories, data, search
from ._categories import Categorization  # noqa: F401
from ._categories import Category  # noqa: F401
from ._categories import HierarchicalCategory  # noqa: F401
from ._categories import from_spec  # noqa: F401
from ._categories import from_yaml  # noqa: F401
from ._categories import HierarchicalCategorization, from_pickle
from ._conversions import Conversion, ConversionRule  # noqa: F401

cats = {}


def _read_pickle_hier(name) -> HierarchicalCategorization:
    with importlib.resources.open_binary(data, f"{name}.pickle") as fd:
        _cat = from_pickle(fd)
    _cat._cats = cats
    cats[_cat.name] = _cat
    return _cat


# not used at the moment, uncomment if needed for non-hierarchical Categorizations
# def _read_pickle_nh(name) -> Categorization:
#    with importlib.resources.open_binary(data, f"{name}.pickle") as fd:
#        _cat = from_pickle(fd)
#    _cat._cats = cats
#    cats[_cat.name] = _cat
#    return _cat


# do this explicitly to help static analysis tools
IPCC1996 = _read_pickle_hier("IPCC1996")
IPCC2006 = _read_pickle_hier("IPCC2006")
IPCC2006_PRIMAP = _read_pickle_hier("IPCC2006_PRIMAP")
CRF1999 = _read_pickle_hier("CRF1999")
CRFDI = _read_pickle_hier("CRFDI")
CRFDI_class = _read_pickle_hier("CRFDI_class")
BURDI = _read_pickle_hier("BURDI")
BURDI_class = _read_pickle_hier("BURDI_class")
GCB = _read_pickle_hier("GCB")
RCMIP = _read_pickle_hier("RCMIP")
gas = _read_pickle_hier("gas")


def find_code(code: str) -> typing.Set[_categories.Category]:
    """Search for the given code in all included categorizations."""
    return search.search_code(code, cats.values())


__all__ = [
    "cats",
    "Categorization",
    "HierarchicalCategorization",
    "Category",
    "HierarchicalCategory",
    "Conversion",
    "ConversionRule",
    "find_code",
    "from_pickle",
    "from_spec",
    "from_yaml",
] + list(cats.keys())
