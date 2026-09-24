"""Run this via `make climate_categories/data/AR6_SCEN_DB.yaml`
   in the main directory."""

import pathlib

import pandas as pd

import climate_categories

# Input file extracted with
# df = pd.read_csv(
#     "AR6_Scenarios_Database_World_v1.0/AR6_Scenarios_Database_World_v1.0.csv")
# df[["Variable", "Unit"]].drop_duplicates().sort_values(
#     "Variable").to_csv("ar6-variables.csv", index=False)

INPATH = pathlib.Path("./data_generation/ar6-variables.csv")
OUTPATH = pathlib.Path("./climate_categories/data/AR6_SCEN_DB.yaml")

comment = """Variables in the AR6 Scenario Database

Edward Byers, Volker Krey, Elmar Kriegler, Keywan Riahi, Roberto Schaeffer,
Jarmo Kikstra, Robin Lamboll, Zebedee Nicholls, Marit Sanstad, Chris Smith,
Kaj-Ivar van der Wijst, Franck Lecocq, Joana Portugal-Pereira, Yamina Saheb,
Anders Strømann, Harald Winkler, Cornelia Auer, Elina Brutschin, Claire Lepault,
Eduardo Müller-Casseres, Matthew Gidden, Daniel Huppmann, Peter Kolp, Giacomo
Marangoni, Michaela Werning, Katherine Calvin, Celine Guivarch, Tomoko Hasegawa,
Glen Peters, Julia Steinberger, Massimo Tavoni, Detlef von Vuuren, Piers Forster,
Jared Lewis, Malte Meinshausen, Joeri Rogelj, Bjorn Samset, Ragnhild Skeie, Alaa
Al Khourdajie.
AR6 Scenarios Database hosted by IIASA
International Institute for Applied Systems Analysis, 2022.
doi: 10.5281/zenodo.5886912 | url: data.ene.iiasa.ac.at/ar6/"""


def main():

    variables = pd.read_csv(INPATH)
    variables["Level"] = variables.Variable.apply(lambda x: str.count(x, "|") + 1)
    variables = variables.sort_values(by=["Level", "Variable"])

    categories = {}

    for _, item in variables.iterrows():

        species = item.Variable
        if species not in categories:
            categories[species] = {
                "title": species,
                "info": {"unit": item.Unit},
                "children": [[]],
            }
        if "|" in species:
            parent = item.Variable.rsplit("|", maxsplit=1)[0]

            if parent not in categories:
                categories[parent] = {
                    "title": parent,
                    "children": [[]],
                }
            if species not in categories[parent]["children"][0]:
                categories[parent]["children"][0].append(species)

    spec = {
        "name": "AR6_SCEN_DB",
        "title": "Categories from the AR6 Scenario Database",
        "comment": comment,
        "references": (
            """Edward Byers, Volker Krey, Elmar Kriegler, Keywan Riahi, et al.
AR6 Scenarios Database hosted by IIASA
International Institute for Applied Systems Analysis, 2022.
doi: 10.5281/zenodo.5886912 | url: data.ece.iiasa.ac.at/ar6/"""
        ),
        "institution": "Hosted by IIASA",
        "last_update": "2022-04-04",
        "hierarchical": True,
        "version": "1.0",
        "total_sum": False,
        "categories": categories,
    }

    AR6_SCEN_DB = climate_categories.HierarchicalCategorization.from_spec(spec)

    AR6_SCEN_DB.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
