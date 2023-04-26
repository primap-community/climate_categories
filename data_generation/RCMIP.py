"""Run this via `make climate_categories/data/RCMIP.yaml` in the main directory."""

import pathlib

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
    "BC": "Black carbon emissions",
    "BC|MAGICC AFOLU": "Black carbon AFOLU emissions",
    "BC|MAGICC Fossil and Industrial": "Black carbon fossil and industrial emissions",
    "BC|Other": "Black carbon emissions from other sources",
    "CH4": "Methane emissions",
    "CH4|MAGICC AFOLU": "Methane AFOLU emissions",
    "CH4|MAGICC Fossil and Industrial": "Methane fossil and industrial emissions",
    "CH4|Other": "Methane emissions from other sources",
    "CO": "Carbon monoxide emissions",
    "CO|MAGICC AFOLU": "Carbon monoxide AFOLU emissions",
    "CO|MAGICC Fossil and Industrial": (
        "Carbon monoxide fossil " "and industrial emissions"
    ),
    "CO|Other": "Carbon monoxide emissions from other sources",
    "CO2": "Carbon dioxide emissions",
    "CO2|MAGICC AFOLU": "Carbon dioxide AFOLU emissions",
    "CO2|MAGICC Fossil and Industrial": (
        "Carbon dioxide fossil " "and industrial emissions"
    ),
    "CO2|Other": "Carbon dioxide emissions from other sources",
    "F-Gases": "F-gas emissions",
    "F-Gases|HFC": "Hydrofluorocarbons (HFCs and HCFCs) emissions",
    "F-Gases|HFC|HFC125": "HFC125 emissions",
    "F-Gases|HFC|HFC134a": "HFC134a emissions",
    "F-Gases|HFC|HFC143a": "HFC143a emissions",
    "F-Gases|HFC|HFC152a": "HFC152a emissions",
    "F-Gases|HFC|HFC227ea": "HFC227ea emissions",
    "F-Gases|HFC|HFC23": "HFC23 emissions",
    "F-Gases|HFC|HFC236fa": "HFC236fa emissions",
    "F-Gases|HFC|HFC245fa": "HFC245fa emissions",
    "F-Gases|HFC|HFC32": "HFC32 emissions",
    "F-Gases|HFC|HFC365mfc": "HFC365mfc emissions",
    "F-Gases|HFC|HFC4310mee": "HFC43-10mee emissions",
    "F-Gases|NF3": "Nitrogen trifluoride emissions",
    "F-Gases|PFC": "Perfluorocarbons  emissions",
    "F-Gases|PFC|C2F6": "C2F6 emissions",
    "F-Gases|PFC|C3F8": "C3F8 emissions",
    "F-Gases|PFC|C4F10": "C4F10 emissions",
    "F-Gases|PFC|C5F12": "C5F12 emissions",
    "F-Gases|PFC|C6F14": "C6F14 emissions",
    "F-Gases|PFC|C7F16": "C7F16 emissions",
    "F-Gases|PFC|C8F18": "C8F18 emissions",
    "F-Gases|PFC|cC4F8": "c-C4F8 emissions",
    "F-Gases|PFC|CF4": "CF4 emissions",
    "F-Gases|SF6": "Sulfur hexafluoride emissions",
    "F-Gases|SO2F2": "Sulfuryl fluoride emissions",
    "Montreal Gases": "Montreal gas emissions",
    "Montreal Gases|CCl4": "CCl4 emissions",
    "Montreal Gases|CFC": "CFC emissions",
    "Montreal Gases|CFC|CFC11": "CFC11 emissions",
    "Montreal Gases|CFC|CFC113": "CFC113 emissions",
    "Montreal Gases|CFC|CFC114": "CFC114 emissions",
    "Montreal Gases|CFC|CFC115": "CFC115 emissions",
    "Montreal Gases|CFC|CFC12": "CFC12 emissions",
    "Montreal Gases|CH2Cl2": "CH2Cl2 emissions",
    "Montreal Gases|CH3Br": "CH3Br emissions",
    "Montreal Gases|CH3CCl3": "CH3CCl3 emissions",
    "Montreal Gases|CH3Cl": "CH3Cl emissions",
    "Montreal Gases|CHCl3": "CHCl3 emissions",
    "Montreal Gases|Halon1202": "Halon-1202 emissions",
    "Montreal Gases|Halon1211": "Halon-1211 emissions",
    "Montreal Gases|Halon1301": "Halon-1301 emissions",
    "Montreal Gases|Halon2402": "Halon-2402 emissions",
    "Montreal Gases|HCFC141b": "HCFC141b emissions",
    "Montreal Gases|HCFC142b": "HCFC22 emissions",
    "Montreal Gases|HCFC22": "HCFC22 emissions",
    "N2O": "Nitrogen emissions",
    "N2O|MAGICC AFOLU": "Nitrogen AFOLU emissions",
    "N2O|MAGICC Fossil and Industrial": "Nitrogen fossil and industrial emissions",
    "N2O|Other": "Nitrogen emissions from other sources",
    "NH3": "Ammonia emissions",
    "NH3|MAGICC AFOLU": "Ammonia AFOLU emissions",
    "NH3|MAGICC Fossil and Industrial": "Ammonia fossil and industrial emissions",
    "NH3|Other": "Ammonia emissions from other sources",
    "NOx": "Nitrous oxide emissions",
    "NOx|MAGICC AFOLU": "Nitrous oxide AFOLU emissions",
    "NOx|MAGICC Fossil and Industrial": "Nitrous oxide fossil and industrial emissions",
    "NOx|Other": "Nitrous oxide emissions from other sources",
    "OC": "Organic carbon emissions",
    "OC|MAGICC AFOLU": "Organic carbon AFOLU emissions",
    "OC|MAGICC Fossil and Industrial": "Organic carbon fossil and industrial emissions",
    "OC|Other": "Organic carbon emissions from other sources",
    "Sulfur": "Sulfur emissions",
    "Sulfur|MAGICC AFOLU": "Sulfur AFOLU emissions",
    "Sulfur|MAGICC Fossil and Industrial": "Sulfur fossil and industrial emissions",
    "Sulfur|Other": "Sulfur emissions from other sources",
    "VOC": "(Non-methane) volatile organic compounds emissions",
    "VOC|MAGICC AFOLU": "(Non-methane) volatile organic compounds AFOLU emissions",
    "VOC|MAGICC Fossil and Industrial": (
        "(Non-methane) volatile organic compounds" " fossil and industrial emissions"
    ),
    "VOC|Other": (
        "(Non-methane) volatile organic compounds" " emissions from other sources"
    ),
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
        item_comment = item.Definition.replace(
            "(please provide a definition of other sources in this category in the "
            "'comments' tab)",
            "(please provide a definition)",
        )
        if species not in categories:
            categories[species] = {
                "title": titles[species.rsplit("Emissions|", maxsplit=1)[1]],
                "comment": item_comment,
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
            "Geosci. Model Dev., 13, 5175-5190, "
            "https://doi.org/10.5194/gmd-13-5175-2020, 2020."
        ),
        "institution": "RCMIP",
        "last_update": "2020-09-21",
        "hierarchical": True,
        "version": "v5.1.0",
        "total_sum": True,
        "categories": categories,
        "canonical_top_level_category": "Emissions",
    }

    RCMIP = climate_categories.HierarchicalCategorization.from_spec(spec)

    RCMIP.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
