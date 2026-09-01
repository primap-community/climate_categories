"""Run this via `make climate_categories/data/gas.yaml` in the main directory."""

import pathlib
import re

import openscm_units
import openscm_units.data
import openscm_units.data.mixtures

import climate_categories
from utils import latex_title

OUTPATH = pathlib.Path("./climate_categories/data/gas.yaml")

#: Halocarbons and refrigerants are named by a numbering scheme instead of by their
#: molecular formula, so their digits must not be subscripted: HFC134a is a name, not
#: a molecule with 134 of something in it. The digit is required so that formulae like
#: HCl are still recognized as formulae.
_DESIGNATION_RE = re.compile(
    r"^(?:CFC|HCFC|HCFE|HCFO|HCO|HFC|HFE|HFO|HGalden|HG|HO|HC|Halon)\d|^PFPMIE$"
)
#: The elements occurring in the formulae of climate-forcing gases. Longer symbols
#: have to come first so that, for example, Cl is not read as C followed by l.
_ELEMENTS = "Cl|Br|C|H|N|O|S|F|I"
#: A molecular formula, optionally prefixed with c for a cyclic molecule (cC4F8).
_FORMULA_RE = re.compile(rf"^c?(?:(?:{_ELEMENTS})[0-9]*)+$")


def latex_formula(title: str) -> str | None:
    """Subscript the numbers in a title which is a molecular formula.

    Returns None if the title is not a molecular formula, or is one without numbers,
    i.e. if it needs no separate LaTeX title.
    """
    if _DESIGNATION_RE.match(title) or not _FORMULA_RE.match(title):
        return None
    latex = re.sub(
        r"[0-9]+",
        lambda m: f"$_{m.group()}$" if len(m.group()) == 1 else f"$_{{{m.group()}}}$",
        title,
    )
    if latex == title:
        return None
    return latex


def main():
    categories = openscm_standard_gases()
    categories.update(openscm_mixtures())

    # specific fixes
    categories["OC"]["title"] = "organic carbon"
    categories["OC"]["comment"] = "organic carbon"

    categories["VOC"]["title"] = "volatile organic compounds"
    categories["VOC"]["comment"] = "non-methane volatile organic compounds"

    # LaTeX titles: the gases named after a formula need their numbers subscripted,
    # the ones named after the substance (methane) or by a numbering scheme (HFC134a)
    # do not.
    for category in categories.values():
        latex = latex_title(category["title"]) or latex_formula(category["title"])
        if latex is not None:
            category["latex_title"] = latex

    spec = {
        "name": "gas",
        "title": "climate-forcing gases",
        "comment": "Gases and other climate-forcing substances",
        "references": "Derived from openscm_units "
        "(https://github.com/openscm/openscm-units) 'standard gases' and mixtures.",
        "last_update": "2024-10-23",
        "version": "0.3.1",
        "institution": "openscm",
        "categories": categories,
        "hierarchical": True,
        "total_sum": False,
    }

    gas = climate_categories.HierarchicalCategorization.from_spec(spec)
    gas.to_yaml(OUTPATH)


def openscm_mixtures():
    categories = {}
    m = openscm_units.data.mixtures.MIXTURES

    for code, constituents in m.items():
        cstr = ", ".join(f"{constituents[const][0]}% {const}" for const in constituents)
        categories[code] = {
            "title": code,
            "comment": f"The refrigerant {code}, which is a mixture of {cstr}.",
        }

    categories["mixtures"] = {
        "title": "refrigerant mixtures",
        "children": [list(categories.keys())],
    }

    return categories


def openscm_standard_gases():
    categories = {}
    # This is not public API, will have to fix it when openscm_units changes
    sg = openscm_units._unit_registry._STANDARD_GASES

    for oscm_gas_code, oscm_gas_spec in sg.items():
        if isinstance(oscm_gas_spec, str):  # base entity
            code = oscm_gas_code
            title = oscm_gas_spec.replace("_", " ")
            categories[code] = {
                "title": title,
            }
            if code != oscm_gas_spec and " " not in oscm_gas_spec:
                categories[code]["alternative_codes"] = [oscm_gas_spec]
        else:  # derived entity or alias
            definition = oscm_gas_spec[0]
            oscm_altcodes = oscm_gas_spec[1:]
            if definition in categories:  # alias
                if "alternative_codes" not in categories[definition]:
                    categories[definition]["alternative_codes"] = []
                categories[definition]["alternative_codes"].append(oscm_gas_code)
                categories[definition]["alternative_codes"] += oscm_altcodes
            else:  # derived entity
                code = oscm_gas_code
                if len(oscm_altcodes) > 1:
                    raise ValueError(f"Unexpected entry for {code}")
                title = oscm_altcodes[0].replace("_", " ")
                categories[code] = {
                    "title": title,
                }
                if code != oscm_altcodes[0]:
                    categories[code]["alternative_codes"] = oscm_altcodes

    return categories


if __name__ == "__main__":
    main()
