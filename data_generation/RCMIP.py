"""Run this via `make climate_categories/data/RCMIP.yaml` in the main directory."""

import pathlib
from pprint import pprint

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


def main():
    download_cached(URL, INPATH)

    categories = {}

    categories["Emissions"] = {"title": "RCMIP Emissions", "children": [[]]}

    categories["MAGICC AFOLU"] = {
        "title": "MAGICC AFOLU",
        "comment": "emissions from agriculture, forestry and other land use (IPCC category 3), excluding any fossil-fuel based emissions in the Agricultural sector (hence not identical to WG3 AFOLU)",
    }

    categories["MAGICC Fossil and Industrial"] = {
        "title": "MAGICC Fossil and Industrial",
        "comment": "emissions from energy use on supply and demand side (IPCC category 1A, 1B), industrial processes (IPCC category 2), waste (IPCC category 4) and other (IPCC category 5)",
        "children": [[]],
    }

    categories["Other"] = {"title": "Other", "comment": "emissions from other sources"}

    definitions = pd.read_excel(INPATH, sheet_name="variable_definitions")

    for _, item in definitions[definitions.Category == "Emissions"].iterrows():

        species = item.Variable.rsplit("|", maxsplit=1)[-1]
        parent = item.Variable.rsplit("|", maxsplit=2)[-2]
        if species not in categories:
            categories[species] = {
                "title": item.Variable,
                "comment": item.Definition,
                "children": [[]],
            }
        if species not in categories[parent]["children"][0]:
            categories[parent]["children"][0].append(species)

    spec = {
        "name": "RCMIP",
        "title": "Emissions categories from the Reduced Complexity Model Intercomparison Project (RCMIP)",
        "comment": "",
        "references": "Nicholls, Z. R. J., Meinshausen, M., Lewis, J., Gieseke, R., Dommenget, D., Dorheim, K., Fan, C.-S., Fuglestvedt, J. S., Gasser, T., Golüke, U., Goodwin, P., Hartin, C., Hope, A. P., Kriegler, E., Leach, N. J., Marchegiani, D., McBride, L. A., Quilcaille, Y., Rogelj, J., Salawitch, R. J., Samset, B. H., Sandstad, M., Shiklomanov, A. N., Skeie, R. B., Smith, C. J., Smith, S., Tanaka, K., Tsutsui, J., and Xie, Z.: Reduced Complexity Model Intercomparison Project Phase 1: introduction and evaluation of global-mean temperature response, Geosci. Model Dev., 13, 5175–5190, https://doi.org/10.5194/gmd-13-5175-2020, 2020.",
        "institution": "RCMIP",
        "last_update": "2020-09-21",
        "hierarchical": True,
        "version": "v5.1.0",
        "total_sum": False,
        "categories": categories,
    }

    RCMIP = climate_categories.HierarchicalCategorization.from_spec(spec)

    RCMIP.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
