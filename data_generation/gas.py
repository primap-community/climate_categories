"""Run this via `make climate_categories/data/gas.yaml` in the main directory."""

import pathlib

import openscm_units
import openscm_units.data
import openscm_units.data.mixtures

import climate_categories

OUTPATH = pathlib.Path("./climate_categories/data/gas.yaml")


def main():
    categories = openscm_standard_gases()
    categories.update(openscm_mixtures())

    # specific fixes
    categories["OC"]["title"] = "organic carbon"
    categories["OC"]["comment"] = "organic carbon"

    categories["VOC"]["title"] = "volatile organic compounds"
    categories["VOC"]["comment"] = "non-methane volatile organic compounds"

    spec = {
        "name": "gas",
        "title": "climate-forcing gases",
        "comment": "Gases and other climate-forcing substances",
        "references": "Derived from openscm_units "
        "(https://github.com/openscm/openscm-units) 'standard gases' and mixtures.",
        "last_update": "2021-05-27",
        "version": "0.3.0",
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
            "comment": f"The refrigerant {code}, which is a mixture " f"of {cstr}.",
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
