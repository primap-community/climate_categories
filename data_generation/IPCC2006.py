"""Run this via `make climate_categories/data/IPCC2006.yaml` in the main directory."""

import itertools
import pathlib
import typing

import camelot
from utils import download_cached, title_case

import climate_categories

URL = (
    "https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/1_Volume1/"
    "V1_8_Ch8_Reporting_Guidance.pdf"
)
INPATH = pathlib.Path("./data_generation/IPCC2006.pdf")
OUTPATH = pathlib.Path("./climate_categories/data/IPCC2006.yaml")


def split_code_name(code_name):
    s = code_name.split()
    code_ended = False
    code_parts = []
    name_parts = []
    for si in s:
        if code_ended:
            name_parts.append(si)
        elif si.isdigit() or len(si) <= 2 or (len(si) > 2 and si == "iii"):
            code_parts.append(si)
        else:
            code_ended = True
            name_parts.append(si)
    return code_parts, " ".join(name_parts)


def parse_pdfs(inpath: str) -> list[tuple[str, str, str, str]]:
    t = camelot.read_pdf(
        inpath,
        pages="10-33",
        flavor="stream",
        table_areas=["74,744,527,35"],
        columns=["251,468,498"],
        row_tol=3,
    )
    tend = camelot.read_pdf(
        inpath,
        pages="34",
        flavor="stream",
        table_areas=["74,744,527,410"],
        columns=["251,468,498"],
        row_tol=3,
    )
    cats_raw = []
    full_code_name = None
    full_definition = None
    full_code_96 = None
    full_gases = None
    for table in itertools.chain(t, tend):
        for _, row in table.df.iterrows():
            code_name, definition, code_96, gases = row
            if code_name and code_name[0].isnumeric():
                # store current and start new category
                if full_gases is not None:
                    cats_raw.append(
                        (full_code_name, full_definition, full_code_96, full_gases)
                    )
                full_code_name = ""
                full_definition = ""
                full_code_96 = ""
                full_gases = ""

            if code_name:
                full_code_name = f"{full_code_name} {code_name}"
            if definition:
                full_definition = f"{full_definition} {definition}"
            if code_96:
                full_code_96 = f"{full_code_96} {code_96}"
            if gases:
                if gases == "ated" or full_gases.endswith(","):
                    full_gases = f"{full_gases}{gases}"
                else:
                    full_gases = f"{full_gases} {gases}"
    cats_raw.append((full_code_name, full_definition, full_code_96, full_gases))
    return cats_raw


def parse_categories(cats_raw) -> dict[str, typing.Any]:
    categories: dict[str, typing.Any] = {}
    for code_name, definition, code_96, gases in cats_raw:
        code_parts, title = split_code_name(code_name)
        # error in pdf
        if code_parts == ["1", "B", "2", "a", "iii", "I"]:
            code_parts = ["1", "B", "2", "a", "iii", "1"]
        code = ".".join(code_parts)
        altcode = "".join(code_parts)
        comment = definition.strip().replace("\n", " ").strip()

        if code in categories:
            raise ValueError(f"double category? {code_name} -> {code_parts} {title}")

        categories[code] = {
            "title": title_case(title.strip()),
        }
        if comment:
            categories[code]["comment"] = comment

        if code != altcode:
            categories[code]["alternative_codes"] = [altcode]

        gases = gases.replace("CH4 N2O", "CH4, N2O")  # common error in pdf
        gases = gases.replace("N2O NOx", "N2O, NOx")  # common error in pdf
        gases = gases.replace("CO2*", "CO2")  # we don't care for the *
        gases_stripped = [x.strip() for x in gases.split(",") if x.strip()]
        if gases_stripped:
            categories[code]["info"] = {"gases": gases_stripped}

        if code_96.strip() and code_96.strip() != "NA":
            if "info" not in categories[code]:
                categories[code]["info"] = {}
            categories[code]["info"]["corresponding_categories_IPCC1996"] = [
                x.strip().replace(" ", "") for x in code_96.split(",")
            ]
    return categories


def add_relationships(categories):
    for parent_code in categories:
        prefix = parent_code + "."
        children = []
        for child_code in categories:
            if child_code.startswith(prefix) and "." not in child_code[len(prefix) :]:
                children.append(child_code)
        if children:
            categories[parent_code]["children"] = [children]


def main():
    download_cached(URL, INPATH)
    cats_raw = parse_pdfs(str(INPATH))

    # Widely used and very useful, even though not included in the official spec
    categories: dict[str, typing.Any] = {
        "0": {
            "title": "National Total",
            "comment": "All emissions and removals",
            "children": [["1", "2", "3", "4", "5"]],
        }
    }

    categories.update(parse_categories(cats_raw))
    add_relationships(categories)

    spec = {
        "name": "IPCC2006",
        "title": "IPCC GHG emission categories (2006)",
        "comment": "IPCC classification of green-house gas emissions into categories,"
        " 2006 edition",
        "references": "IPCC 2006, 2006 IPCC Guidelines for National Greenhouse Gas"
        " Inventories, Prepared by the National Greenhouse Gas Inventories"
        " Programme, Eggleston H.S., Buendia L., Miwa K., Ngara T. and Tanabe"
        " K. (eds). Volume 1, Chapter 8, Table 8.2,"
        " https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol1.html",
        "institution": "IPCC",
        "last_update": "2010-06-30",
        "hierarchical": True,
        "version": "2006",
        "total_sum": True,
        "categories": categories,
        "canonical_top_level_category": "0",
    }

    # individual fixes to data from pdf
    categories = spec["categories"]
    categories["1"]["title"] = "Energy"
    categories["1.A.1.a.ii"]["title"] = "Combined Heat and Power Generation (CHP)"

    categories["1.A.2.m"]["title"] = "Non-Specified Industry"
    categories["1.A.3.e"]["info"]["corresponding_categories_IPCC1996"] = ["1A3e"]
    categories["1.A.4.c.ii"]["info"]["corresponding_categories_IPCC1996"] = ["1A4cii"]

    del categories["1.B.2.b.iii.1"]["info"]["corresponding_categories_IPCC1996"]
    del categories["1.B.2.b.iii.2"]["info"]["corresponding_categories_IPCC1996"]
    del categories["1.B.2.b.iii.3"]["info"]["corresponding_categories_IPCC1996"]

    categories["2.A.3"]["info"]["gases"] = ["CO2", "CH4"]
    categories["2.A.3"]["info"]["corresponding_categories_IPCC1996"] = [
        "2A3",
        "2A4",
    ]

    categories["2.A.4"]["info"]["gases"] = [
        "CO2",
        "CH4",
        "NOx",
        "CO",
        "NMVOC",
        "SO2",
    ]
    categories["2.A.4"]["info"]["corresponding_categories_IPCC1996"] = [
        "2A3",
        "2A4",
    ]

    categories["2.B.3"]["info"]["gases"] = ["N2O", "CO2", "CH4", "NOx"]

    for cat in ("3.B.1", "3.B.1.b"):
        categories[cat]["info"]["gases"] = [
            "CO2",
            "CH4",
            "N2O",
            "NOx",
            "CO",
            "NMVOC",
            "SO2",
        ]
        categories[cat]["info"]["corresponding_categories_IPCC1996"] = [
            "5A",
            "5C",
            "5D",
        ]

    categories["3.B.3"]["info"]["corresponding_categories_IPCC1996"] = [
        "4D",
        "4E",
        "5A",
        "5B",
        "5C",
        "5D",
    ]

    categories["3.B.3.a"]["title"] = "Grassland Remaining Grassland"
    categories["3.B.3.a"][
        "comment"
    ] = "Emissions and removals from grassland remaining grassland."

    categories["3.B.3.b"][
        "comment"
    ] = "Emissions and removals from land converted to grassland."
    categories["3.B.3.b"]["info"]["corresponding_categories_IPCC1996"] = [
        "5B",
        "5C",
        "5D",
    ]

    categories["3.C.1.c"]["title"] = "Biomass Burning in Grasslands"
    categories["3.C.1.c"]["comment"] = (
        "Emissions from biomass burning that include N2O and CH4 in grasslands."
        " CO2 emissions are included here only if emissions are not included in"
        " 3B3 categories as carbon stock changes."
    )

    categories["4"]["info"]["gases"] = [
        "CO2",
        "CH4",
        "N2O",
        "NOx",
        "CO",
        "NMVOC",
        "SO2",
    ]

    categories["4.A.3"]["title"] = "Uncategorised Waste Disposal Sites"
    categories["4.A.3"]["comment"] = (
        "Mixture of above 4 A1 and 4 A2. Countries "
        "that do not have data on division of managed/unmanaged may use this category."
    )

    IPCC2006 = climate_categories.HierarchicalCategorization.from_spec(spec)

    IPCC2006.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
