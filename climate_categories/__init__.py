"""Access to all categorizations is provided directly at the module level, using the
names of categorizations. To access the example categorization `Excat`, simply use
`climate_categories.Excat` .
"""

__author__ = """Mika Pflüger"""
__email__ = "mika.pflueger@climate-resource.com"
__version__ = "0.8.3"

import importlib
import importlib.resources

from . import (
    search,
)
from ._categories import (
    Categorization,
    Category,
    HierarchicalCategorization,
    HierarchicalCategory,
    from_pickle,
    from_python,
    from_spec,
    from_yaml,
)
from ._conversions import Conversion, ConversionRule

cats = {}


def _read_py_hier(name) -> HierarchicalCategorization:
    mod = importlib.import_module(f".data.{name}", package="climate_categories")
    cat = HierarchicalCategorization.from_spec(mod.spec)
    cat._cats = cats
    cats[cat.name] = cat
    return cat


# do this explicitly to help static analysis tools
IPCC1996 = _read_py_hier("IPCC1996")
IPCC2006 = _read_py_hier("IPCC2006")
IPCC2006_PRIMAP = _read_py_hier("IPCC2006_PRIMAP")
CRF1999 = _read_py_hier("CRF1999")
CRF2013 = _read_py_hier("CRF2013")
CRF2013_2021 = _read_py_hier("CRF2013_2021")
CRF2013_2022 = _read_py_hier("CRF2013_2022")
CRF2013_2023 = _read_py_hier("CRF2013_2023")
CRFDI = _read_py_hier("CRFDI")
CRFDI_class = _read_py_hier("CRFDI_class")
BURDI = _read_py_hier("BURDI")
BURDI_class = _read_py_hier("BURDI_class")
GCB = _read_py_hier("GCB")
RCMIP = _read_py_hier("RCMIP")
gas = _read_py_hier("gas")


def find_code(code: str) -> set[Category]:
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
    "from_python",
    *list(cats.keys()),
]
