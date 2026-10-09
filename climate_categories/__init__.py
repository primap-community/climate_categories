"""Access to all categorizations is provided directly at the module level, using the
names of categorizations. To access the example categorization `Excat`, simply use
`climate_categories.Excat` .

Categorizations with options, like `ISO3[eu,unfccc]`, are available via
`climate_categories.cats["ISO3[eu,unfccc]"]` or
`climate_categories.ISO3.with_options(["eu", "unfccc"])`.
"""

__author__ = """Mika Pflüger"""
__email__ = "mika.pflueger@climate-resource.com"

import importlib
import importlib.metadata

from . import (
    search,
)
from ._categories import (
    Categorization,
    Category,
    HierarchicalCategorization,
    HierarchicalCategory,
    canonical_name,
    from_pickle,
    from_python,
    from_spec,
    from_yaml,
    parse_name,
)
from ._conversions import Conversion, ConversionRule
from ._options import (
    CategorizationOption,
    CategorizationRegistry,
    CategoryRemoval,
    OptionCombination,
    OptionFamily,
    OptionManifest,
    UnsupportedCombination,
    UnsupportedCombinationError,
    UnsupportedCombinationWarning,
    load_extension,
    manifest_stem,
    option_stem,
)

__version__ = importlib.metadata.version("climate_categories")

cats = CategorizationRegistry()


def _read_py_hier(name) -> HierarchicalCategorization:
    mod = importlib.import_module(f".data.{name}", package="climate_categories")
    cat = HierarchicalCategorization.from_spec(mod.spec)
    cat._cats = cats
    cats[cat.name] = cat
    return cat


def _read_py_options(base: str) -> OptionFamily:
    def read_spec(name: str) -> dict:
        return importlib.import_module(
            f".data.{name}", package="climate_categories"
        ).spec

    manifest = OptionManifest.from_spec(read_spec(manifest_stem(base)))
    options = {
        name: CategorizationOption.from_spec(read_spec(option_stem(base, name)))
        for name in manifest.options
    }
    family = OptionFamily(base=cats[base], manifest=manifest, options=options)
    cats.register_family(family)
    return family


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
ISO3 = _read_py_hier("ISO3")
_read_py_options("ISO3")
ISO3_PRIMAP = cats["ISO3_PRIMAP"]
ISO3_GCAM = cats["ISO3_GCAM"]
FAO = _read_py_hier("FAO")
CT = _read_py_hier("CT")


def find_code(code: str) -> set[Category]:
    """Search for the given code in all included categorizations."""
    return search.search_code(code, cats.values())


__all__ = [
    "BURDI",
    "CRF1999",
    "CRF2013",
    "CRF2013_2021",
    "CRF2013_2022",
    "CRF2013_2023",
    "CRFDI",
    "CT",
    "FAO",
    "GCB",
    "IPCC1996",
    "IPCC2006",
    "IPCC2006_PRIMAP",
    "ISO3",
    "ISO3_GCAM",
    "ISO3_PRIMAP",
    "RCMIP",
    "BURDI_class",
    "CRFDI_class",
    "Categorization",
    "CategorizationOption",
    "CategorizationRegistry",
    "Category",
    "CategoryRemoval",
    "Conversion",
    "ConversionRule",
    "HierarchicalCategorization",
    "HierarchicalCategory",
    "OptionCombination",
    "OptionFamily",
    "OptionManifest",
    "UnsupportedCombination",
    "UnsupportedCombinationError",
    "UnsupportedCombinationWarning",
    "canonical_name",
    "cats",
    "find_code",
    "from_pickle",
    "from_python",
    "from_spec",
    "from_yaml",
    "gas",
    "load_extension",
    "manifest_stem",
    "option_stem",
    "parse_name",
]
