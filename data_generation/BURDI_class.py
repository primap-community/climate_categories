"""Run this via `make climate_categories/data/BURDI_class.yaml` in the main directory.
"""
import pathlib

import numpy as np
import unfccc_di_api

import climate_categories

OUTPATH = pathlib.Path("./climate_categories/data/BURDI_class.yaml")


def parse_classifications():
    rao = unfccc_di_api.UNFCCCSingleCategoryApiReader(party_category="nonAnnexOne")

    new_categories = {}
    new_children = []
    for parent_category in climate_categories.BURDI.values():
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

    return new_categories, new_children


def main():
    categories, children = parse_classifications()

    BURDI_class = climate_categories.BURDI.extend(
        categories=categories,
        children=children,
        name="class",
        title=" + classifications",
        comment=" extended by sub-classifications also provided by the DI flexible "
        "query interface",
    )
    BURDI_class.institution = "UNFCCC"
    BURDI_class.references = (
        "https://unfccc.int/process-and-meetings/"
        "transparency-and-reporting/greenhouse-gas-data/data-interface-help#eq-7"
    )
    BURDI_class.total_sum = False  # unfortunately, not generally true anymore

    BURDI_class.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
