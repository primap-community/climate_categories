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

comment = """AFOLU in the SSPDb is AFOLU minus any agriculture
related fossil fuel based emissions hence is not the same as the
WG3 AFOLU definition. Rather AFOLU in the SSPDb is AFOLU as expected by
MAGICC (i.e. exluding agriculture related fossil fuel use), hence
we call it MAGICC AFOLU."""

titles = {
    "Emissions|BC": "Black carbon emissions",
    "Emissions|BC|MAGICC AFOLU": "Black carbon AFOLU emissions",
    "Emissions|BC|MAGICC Fossil and Industrial": "Black carbon fossil and industrial emissions",
    "Emissions|BC|Other": "Black carbon emissions from other sources",
    "Emissions|CH4": "Methane emissions",
    "Emissions|CH4|MAGICC AFOLU": "Methane AFOLU emissions",
    "Emissions|CH4|MAGICC Fossil and Industrial": "Methane fossil and industrial emissions",
    "Emissions|CH4|Other": "Methane emissions from other sources",
    "Emissions|CO": "Carbon monoxide emissions",
    "Emissions|CO|MAGICC AFOLU": "Carbon monoxide AFOLU emissions",
    "Emissions|CO|MAGICC Fossil and Industrial": "Carbon monoxide fossil and industrial emissions",
    "Emissions|CO|Other": "Carbon monoxide emissions from other sources",
    "Emissions|CO2": "Carbon dioxide emissions",
    "Emissions|CO2|MAGICC AFOLU": "Carbon dioxide AFOLU emissions",
    "Emissions|CO2|MAGICC Fossil and Industrial": "Carbon dioxide fossil and industrial emissions",
    "Emissions|CO2|Other": "Carbon dioxide emissions from other sources",
    "Emissions|F-Gases": "F-gas emissions",
    "Emissions|F-Gases|HFC": "Hydrofluorocarbons (HFCs and HCFCs) emissions",
    "Emissions|F-Gases|HFC|HFC125": "HFC125 emissions",
    "Emissions|F-Gases|HFC|HFC134a": "HFC134a emissions",
    "Emissions|F-Gases|HFC|HFC143a": "HFC143a emissions",
    "Emissions|F-Gases|HFC|HFC152a": "HFC152a emissions",
    "Emissions|F-Gases|HFC|HFC227ea": "HFC227ea emissions",
    "Emissions|F-Gases|HFC|HFC23": "HFC23 emissions",
    "Emissions|F-Gases|HFC|HFC236fa": "HFC236fa emissions",
    "Emissions|F-Gases|HFC|HFC245fa": "HFC245fa emissions",
    "Emissions|F-Gases|HFC|HFC32": "HFC32 emissions",
    "Emissions|F-Gases|HFC|HFC365mfc": "HFC365mfc emissions",
    "Emissions|F-Gases|HFC|HFC4310mee": "HFC43-10mee emissions",
    "Emissions|F-Gases|NF3": "Nitrogen trifluoride emissions",
    "Emissions|F-Gases|PFC": "Perfluorocarbons  emissions",
    "Emissions|F-Gases|PFC|C2F6": "C2F6 emissions",
    "Emissions|F-Gases|PFC|C3F8": "C3F8 emissions",
    "Emissions|F-Gases|PFC|C4F10": "C4F10 emissions",
    "Emissions|F-Gases|PFC|C5F12": "C5F12 emissions",
    "Emissions|F-Gases|PFC|C6F14": "C6F14 emissions",
    "Emissions|F-Gases|PFC|C7F16": "C7F16 emissions",
    "Emissions|F-Gases|PFC|C8F18": "C8F18 emissions",
    "Emissions|F-Gases|PFC|cC4F8": "c-C4F8 emissions",
    "Emissions|F-Gases|PFC|CF4": "CF4 emissions",
    "Emissions|F-Gases|SF6": "Sulfur hexafluoride emissions",
    "Emissions|F-Gases|SO2F2": "Sulfuryl fluoride emissions",
    "Emissions|Montreal Gases": "Montreal gas emissions",
    "Emissions|Montreal Gases|CCl4": "CCl4 emissions",
    "Emissions|Montreal Gases|CFC": "CFC emissions",
    "Emissions|Montreal Gases|CFC|CFC11": "CFC11 emissions",
    "Emissions|Montreal Gases|CFC|CFC113": "CFC113 emissions",
    "Emissions|Montreal Gases|CFC|CFC114": "CFC114 emissions",
    "Emissions|Montreal Gases|CFC|CFC115": "CFC115 emissions",
    "Emissions|Montreal Gases|CFC|CFC12": "CFC12 emissions",
    "Emissions|Montreal Gases|CH2Cl2": "CH2Cl2 emissions",
    "Emissions|Montreal Gases|CH3Br": "CH3Br emissions",
    "Emissions|Montreal Gases|CH3CCl3": "CH3CCl3 emissions",
    "Emissions|Montreal Gases|CH3Cl": "CH3Cl emissions",
    "Emissions|Montreal Gases|CHCl3": "CHCl3 emissions",
    "Emissions|Montreal Gases|Halon1202": "Halon-1202 emissions",
    "Emissions|Montreal Gases|Halon1211": "Halon-1211 emissions",
    "Emissions|Montreal Gases|Halon1301": "Halon-1301 emissions",
    "Emissions|Montreal Gases|Halon2402": "Halon-2402 emissions",
    "Emissions|Montreal Gases|HCFC141b": "HCFC141b emissions",
    "Emissions|Montreal Gases|HCFC142b": "HCFC22 emissions",
    "Emissions|Montreal Gases|HCFC22": "HCFC22 emissions",
    "Emissions|N2O": "Nitrogen emissions",
    "Emissions|N2O|MAGICC AFOLU": "Nitrogen AFOLU emissions",
    "Emissions|N2O|MAGICC Fossil and Industrial": "Nitrogen fossil and industrial emissions",
    "Emissions|N2O|Other": "Nitrogen emissions from other sources",
    "Emissions|NH3": "Ammonia emissions",
    "Emissions|NH3|MAGICC AFOLU": "Ammonia AFOLU emissions",
    "Emissions|NH3|MAGICC Fossil and Industrial": "Ammonia fossil and industrial emissions",
    "Emissions|NH3|Other": "Ammonia emissions from other sources",
    "Emissions|NOx": "Nitrous oxide emissions",
    "Emissions|NOx|MAGICC AFOLU": "Nitrous oxide AFOLU emissions",
    "Emissions|NOx|MAGICC Fossil and Industrial": "Nitrous oxide fossil and industrial emissions",
    "Emissions|NOx|Other": "Nitrous oxide emissions from other sources",
    "Emissions|OC": "Organic carbon emissions",
    "Emissions|OC|MAGICC AFOLU": "Organic carbon AFOLU emissions",
    "Emissions|OC|MAGICC Fossil and Industrial": "Organic carbon fossil and industrial emissions",
    "Emissions|OC|Other": "Organic carbon emissions from other sources",
    "Emissions|Sulfur": "Sulfur emissions",
    "Emissions|Sulfur|MAGICC AFOLU": "Sulfur AFOLU emissions",
    "Emissions|Sulfur|MAGICC Fossil and Industrial": "Sulfur fossil and industrial emissions",
    "Emissions|Sulfur|Other": "Sulfur emissions from other sources",
    "Emissions|VOC": "(Non-methane) volatile organic compounds emissions",
    "Emissions|VOC|MAGICC AFOLU": "(Non-methane) volatile organic compounds AFOLU emissions",
    "Emissions|VOC|MAGICC Fossil and Industrial": "(Non-methane) volatile organic compounds fossil and industrial emissions",
    "Emissions|VOC|Other": "(Non-methane) volatile organic compounds emissions from other sources ",
}


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
                "title": titles[species],
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
