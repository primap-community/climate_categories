"""Run this via `make climate_categories/data/RCMIP.yaml` in the main directory."""

import pathlib
import re

import pandas as pd
from utils import download_cached

import climate_categories

RCMIP_SUBMISSIONS_TEMPLATE = "rcmip-data-submission-template.xlsx"
URL = (
    "https://gitlab.com/rcmip/rcmip/-/raw/master/data/submission-template/"
    + RCMIP_SUBMISSIONS_TEMPLATE
)
INPATH = pathlib.Path(f"./data_generation/{RCMIP_SUBMISSIONS_TEMPLATE}")
OUTPATH = pathlib.Path("./climate_categories/data/RCMIP.yaml")

comment = """


AFOLU in the SSPDb is AFOLU minus any agriculture
related fossil fuel based emissions hence is not the same as the
WG3 AFOLU definition. Rather AFOLU in the SSPDb is AFOLU as expected by
MAGICC (i.e. exluding agriculture related fossil fuel use), hence
we call it MAGICC AFOLU."""

def main():
    download_cached(URL, INPATH)

    categories = {}

    categories["Emissions"] = {"title": "RCMIP Emissions", "children": [[]]}

    definitions = pd.read_excel(INPATH, sheet_name="variable_definitions")

    for _, item in definitions[definitions.Category == "Emissions"].iterrows():

        species = item.Variable
        print(species)
        parent = item.Variable.rsplit("|", maxsplit=1)[0]
        print(parent)
        if species not in categories:
            categories[species] = {
                "title": re.sub(r'\([^)]*\)', '', item.Definition).replace(" ,", ",").replace("  ", " "),
                "comment": item.Definition,
                "children": [[]],
            }
        if species not in categories[parent]["children"][0]:
            categories[parent]["children"][0].append(species)

    spec = {
        "name": "RCMIP",
        "title": (
            "Emissions categories from the Reduced Complexity Model "
            "Intercomparison Project (RCMIP)"
        ),
        "comment": comment,
        "references": (
            "Nicholls, Z. R. J., Meinshausen, M., Lewis, J., Gieseke, R., "
            "Dommenget, D., Dorheim, K., Fan, C.-S., Fuglestvedt, J. S., Gasser, T., "
            "Golüke, U., Goodwin, P., Hartin, C., Hope, A. P., Kriegler, E., Leach, "
            "N. J., Marchegiani, D., McBride, L. A., Quilcaille, Y., Rogelj, J., "
            "Salawitch, R. J., Samset, B. H., Sandstad, M., Shiklomanov, A. N., "
            "Skeie, R. B., Smith, C. J., Smith, S., Tanaka, K., Tsutsui, J., "
            "and Xie, Z.: Reduced Complexity Model Intercomparison Project Phase 1:"
            " introduction and evaluation of global-mean temperature response, "
            "Geosci. Model Dev., 13, 5175–5190, "
            "https://doi.org/10.5194/gmd-13-5175-2020, 2020."
        ),
        "institution": "RCMIP",
        "last_update": "2020-09-21",
        "hierarchical": True,
        "version": "v5.1.0",
        "total_sum": True,
        "categories": categories,
    }

    RCMIP = climate_categories.HierarchicalCategorization.from_spec(spec)

    RCMIP.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
