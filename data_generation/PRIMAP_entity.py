"""Run this via `make climate_categories/data/PRIMAP_entity.yaml` in the main
directory."""

import pathlib

import openscm_units
import openscm_units.data
import openscm_units.data.mixtures

import climate_categories

OUTPATH = pathlib.Path("./climate_categories/data/PRIMAP_entity.yaml")
OUTPATH_PICKLE = pathlib.Path("./climate_categories/data/PRIMAP_entity.pickle")


def main():
    categories = openscm_standard_gases()
    categories.update(openscm_mixtures())
    categories["emissions"] = {
        "title": "Emissions categories",
        "children": [list(categories.keys())],
    }

    spec = {
        "name": "PRIMAP_entity",
        "title": "PRIMAP2 entities",
        "comment": "Entities commonly used in PRIMAP2",
        "references": "Many emissions entities are derived from openscm_units "
        "(https://github.com/openscm/openscm-units), other entities "
        "are collected for PRIMAP2.",
        "institution": "PIK",
        "last_update": "2021-03-09",
        "version": "2",
        "total_sum": "False",
        "categories": categories,
    }

    PRIMAP_entity = climate_categories.HierarchicalCategorization.from_spec(spec)
    PRIMAP_entity.to_yaml(OUTPATH)
    PRIMAP_entity.to_pickle(OUTPATH_PICKLE)


def openscm_mixtures():
    categories = {}
    m = openscm_units.data.mixtures.MIXTURES

    for code, constituents in m.items():
        cstr = ", ".join(
            (f"{constituents[const][0]}% {const}" for const in constituents)
        )
        categories[code] = {
            "title": code,
            "comment": f"Emissions rate of the refrigerant {code}, which is a mixture "
            f"of {cstr}.",
            "info": {"addition_rule": "extensive"},
        }

    return categories


def openscm_standard_gases():
    categories = {}
    # This is not public API, will have to fix it when openscm_units changes
    sg = openscm_units._unit_registry._STANDARD_GASES

    for (oscm_gas_code, oscm_gas_spec) in sg.items():
        if isinstance(oscm_gas_spec, str):  # base entity
            code = oscm_gas_code
            categories[code] = {
                "title": oscm_gas_spec,
                "comment": f"Emission rate of {oscm_gas_spec}",
                "info": {"addition_rule": "extensive"},
            }
            if code != oscm_gas_code:
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
                    raise ValueError(f"Unexpected entry for {oscm_gas_code}")
                categories[code] = {
                    "title": oscm_altcodes[0],
                    "comment": f"Emission rate of {oscm_gas_code}",
                    "info": {"addition_rule": "extensive"},
                }
                if code != oscm_altcodes[0]:
                    categories[code]["alternative_codes"] = oscm_altcodes

    return categories


if __name__ == "__main__":
    main()
