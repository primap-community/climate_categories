"""Run this via `make climate_categories/data/CRFDI_class.yaml` in the main directory.
"""
import datetime
import pathlib

import numpy as np
import treelib
import unfccc_di_api

import climate_categories

OUTPATH = pathlib.Path("./climate_categories/data/CRFDI_class.yaml")


def parse_classifications(rao):
    new_categories = {}
    new_children = []
    new_alternative_codes = {}
    for parent_category in climate_categories.CRFDI.values():
        classification_ids = np.unique(
            rao.variables.loc[
                rao.variables["categoryId"].isin(
                    [int(x) for x in parent_category.info["numerical_ids"]]
                ),
                "classificationId",
            ]
        )

        new_children_for_category = []
        i = 0
        for cid in sorted(classification_ids):
            if cid == 10510:  # Total for category, i.e. not a sub-category
                # Just add additional altcodes
                primary_altcode = f"{parent_category.codes[0]}-{cid}"
                new_alternative_codes[primary_altcode] = parent_category.codes[0]
                for nid in parent_category.info["numerical_ids"]:
                    altcode = f"{nid}-{cid}"
                    if altcode != primary_altcode:
                        new_alternative_codes[altcode] = parent_category.codes[0]
                continue
            i += 1
            code = f"{parent_category.codes[0]}-{i}"
            altcodes = [f"{parent_category.codes[0]}-{cid}"]
            numerical_altcodes = [
                f"{nid}-{cid}" for nid in parent_category.info["numerical_ids"]
            ]
            for numerical_altcode in numerical_altcodes:
                if numerical_altcode not in altcodes:
                    altcodes.append(numerical_altcode)

            new_categories[code] = {
                "title": rao.classifications.loc[cid, "name"],
                "alternative_codes": altcodes,
            }
            new_children_for_category.append(code)

        if new_children_for_category:
            new_children.append((parent_category.codes[0], new_children_for_category))

    return new_categories, new_children, new_alternative_codes


def parse_refrigerant_measures(rao: unfccc_di_api.UNFCCCSingleCategoryApiReader):
    refrigerant_emission_measures = {
        "Emissions from manufacturing": 1,
        "Emissions from stocks": 2,
        "Emissions from disposal": 3,
    }
    new_categories = {}
    new_children = []
    new_alternative_codes = {}
    for parent_category in climate_categories.CRFDI.values():
        measure_ids = np.unique(
            rao.variables.loc[
                rao.variables["categoryId"].isin(
                    [int(x) for x in parent_category.info["numerical_ids"]]
                ),
                "measureId",
            ]
        )

        new_children_for_category = []
        for mid in sorted(measure_ids):
            try:
                measure = rao.measure_tree[mid].tag
            except treelib.tree.NodeIDAbsentError:
                continue
            if measure not in refrigerant_emission_measures:
                continue
            short_mid = refrigerant_emission_measures[measure]
            code = f"{parent_category.codes[0]}-m{short_mid}"
            altcodes = [f"{parent_category.codes[0]}-m{mid}"]
            numerical_altcodes = [
                f"{nid}-m{mid}" for nid in parent_category.info["numerical_ids"]
            ]
            for numerical_altcode in numerical_altcodes:
                if numerical_altcode not in altcodes:
                    altcodes.append(numerical_altcode)

            new_categories[code] = {
                "title": measure,
                "alternative_codes": altcodes,
            }
            new_children_for_category.append(code)

        if new_children_for_category:
            new_children.append((parent_category.codes[0], new_children_for_category))

    return new_categories, new_children, new_alternative_codes


def main():
    rao = unfccc_di_api.UNFCCCSingleCategoryApiReader(party_category="annexOne")
    categories, children, alternative_codes = parse_classifications(rao)

    categories_add, children_add, alternative_codes_add = parse_refrigerant_measures(
        rao
    )
    categories.update(categories_add)
    children += children_add
    alternative_codes.update(alternative_codes_add)

    CRFDI_class = climate_categories.CRFDI.extend(
        categories=categories,
        children=children,
        alternative_codes=alternative_codes,
        name="class",
        title=" + classifications",
        comment=" extended by sub-classifications also provided by the DI flexible "
        "query interface",
        last_update=datetime.date.fromisoformat("2021-11-05"),
    )
    CRFDI_class.institution = "UNFCCC"
    CRFDI_class.references = (
        "https://unfccc.int/process-and-meetings/"
        "transparency-and-reporting/greenhouse-gas-data/data-interface-help#eq-7"
    )
    CRFDI_class.total_sum = False  # unfortunately, not generally true anymore

    CRFDI_class.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
