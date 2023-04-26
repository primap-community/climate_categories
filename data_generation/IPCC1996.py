"""Run this via `make climate_categories/data/IPCC1996.yaml` in the main directory."""

import pathlib
import typing

import camelot
from utils import download_cached, title_case

import climate_categories

URL = "https://www.ipcc-nggip.iges.or.jp/public/gl/guidelin/ch1ri.pdf"
INPATH = pathlib.Path("./data_generation/IPCC1996.pdf")
OUTPATH = pathlib.Path("./climate_categories/data/IPCC1996.yaml")


def parse_pages(fpath, pages, areas, columns) -> list:
    ts = []
    for page in pages:
        t = camelot.read_pdf(
            str(fpath),
            pages=str(page),
            flavor="stream",
            table_areas=[areas[page % 2]],
            columns=[columns[page % 2]],
            row_tol=10,
        )
        ts.append(t[0])
    return ts


def read_pdf(fpath):
    # 1 energy
    ts = []
    ts += parse_pages(
        fpath,
        pages=range(3, 8),
        areas=["168,723,552,120", "43,723,468,114"],
        columns=["279", "194"],
    )
    # 2 industrial processes
    # 3 solvent and other product use
    ts += parse_pages(
        fpath,
        pages=range(8, 11),
        areas=["140,723,541,135", "0,723,398,117"],
        columns=["285", "206"],
    )
    # 4 agriculture
    ts += parse_pages(
        fpath,
        pages=range(11, 14),
        areas=["157,723,546,95", "55,723,470,88"],
        columns=["276", "193"],
    )
    # 5 agriculture
    ts += parse_pages(
        fpath,
        pages=range(14, 17),
        areas=["127,723,550,214", "55,723,466,208"],
        columns=["276", "198"],
    )
    # 6 waste
    ts.append(
        camelot.read_pdf(
            str(fpath),
            pages="17",
            flavor="stream",
            table_areas=["52,723,464,159"],
            columns=["210"],
            row_tol=10,
        )[0]
    )
    # 7 other
    ts.append(
        camelot.read_pdf(
            str(fpath),
            pages="18",
            flavor="stream",
            table_areas=["180,723,552,670"],
            columns=["288"],
            row_tol=10,
        )[0]
    )
    return ts


def combine_rows(ts):
    rows = []
    for table in ts:
        code_name_previously_empty = True
        definition_previously_empty = True
        current_code_name = None
        current_definition = None
        for _, (code_name, definition) in table.df.iterrows():
            if (
                code_name.startswith("Time period is an important element in")
                or code_name.startswith("categories.  For example, the IPCC default")
                or code_name.startswith("years for biomass decay.")
            ):
                continue
            code_name_empty = not code_name.strip()
            definition_empty = not definition.strip()

            if (
                (code_name_previously_empty and not code_name_empty)
                or (definition_previously_empty and not definition_empty)
                or "\n" in code_name
                or code_name
                in (
                    "iv Motorcycles",
                    "Mining activities",
                    "2 D OTHER PRODUCTION",
                    "2 G OTHER",
                    "4 B MANURE",
                    "6 B WASTEWATER",
                    "6 C WASTE INCINERATION",
                )
            ) and not (
                current_code_name in (" 2\nINDUSTRIAL",)
                or definition.startswith(
                    "petroleum  products,  the",
                )
            ):
                # a new logical row started
                if current_code_name is not None:
                    rows.append((current_code_name, current_definition))
                current_code_name = ""
                current_definition = ""

            if code_name:
                current_code_name += f" {code_name}"
            if definition:
                current_definition += f" {definition}"

            code_name_previously_empty = code_name_empty
            definition_previously_empty = definition_empty

        rows.append((current_code_name, current_definition))

    return rows


def parse_codes(rows):
    cats_raw = []
    roman_numerals = ("i", "ii", "iii", "iv", "v", "vi", "vii")
    parent_code = ""
    parent_roman_code = ""
    running_number = 1
    for code_title, definition in rows:
        if code_title.startswith(" 1 A 2\nb "):
            code_raw = code_title[:8]
            title = code_title[9:]
        elif code_title == " 1 A 2\ne":
            code_raw = code_title
            title = definition
            definition = ""
        elif code_title == " 1 A 3\nd Navigation":
            code_raw = "1 A 3 d"
            title = "Navigation"
        elif code_title == " 4G\nOTHER":
            code_raw = "4 G"
            title = "OTHER"
        elif (
            code_title.startswith(" 1 A 4\n")
            or code_title.startswith(" 1 A 5\nb")
            or code_title.startswith(" 1 B 1\na")
        ) and code_title[7] in ("a", "b", "c"):
            code_raw = code_title[:8]
            title = code_title[9:]
        elif code_title == " FUGITIVE EMISSIONS FROM FUELS":
            code_raw = "1 B"
            title = code_title
        elif (
            "\n" in code_title
            and code_title.strip()[0].isnumeric()
            and code_title
            not in (
                " 4 B\nANAEROBIC 10",
                " 5 A 1\na Wet/ very moist",
                " 5 A 1\nh Other",
                " 5 A 2\nd Other",
            )
        ):
            code_raw, title = code_title.rsplit("\n", 1)
        else:
            splitted = code_title.split()
            if len(splitted) == 2 and len(splitted[0]) == 1:
                code_raw, title = splitted
            else:
                code_raw = ""
                title = ""
                for s in splitted:
                    if len(s) == 1 or s in roman_numerals or s.isnumeric():
                        code_raw += f" {s}"
                    else:
                        title += f" {s}"

        if code_raw == " 2 B3":
            code = "2.B.3"
        else:
            code = ".".join(code_raw.split())
        if code in roman_numerals:
            code = f"{parent_code}.{code}"
            running_number = 1
            parent_roman_code = code
        elif code in ("c.i", "c.ii"):
            code = f"{parent_code[:-1]}{code}"
            running_number = 1
            parent_roman_code = code
        elif not code:
            code = f"{parent_roman_code}.{running_number}"
            running_number += 1
        else:
            parent_code = code
            running_number = 1

        cats_raw.append((code, title, definition))

    return cats_raw


def parse_categories(cats_raw):
    cats = {}
    for code, title, definition in cats_raw:
        if "(" in title and "ISIC" in title and not definition:
            title, definition = title.split("(")
            definition = definition[:-1]

        title = title_case(" ".join(title.split()))
        definition = " ".join(definition.split()).replace("- ", "")
        if len(definition) > 2 and definition[0] == "(" and definition[-1] == ")":
            definition = definition[1:-1]

        altcode = code.replace(".", "")
        altcode2 = code.replace(".", " ")
        spec = {
            "title": title,
        }
        if definition and definition.strip() != ".":
            spec["comment"] = definition
        if altcode != code:
            spec["alternative_codes"] = [altcode, altcode2]

        if code in cats:
            raise ValueError(f"{code!r} exists twice")
        cats[code] = spec

    return cats


def add_relationships(categories):
    for parent_code in categories:
        prefix = f"{parent_code}."
        children = []
        for child_code in categories:
            if child_code.startswith(prefix) and "." not in child_code[len(prefix) :]:
                children.append(child_code)
        if children:
            categories[parent_code]["children"] = [children]


def main():
    download_cached(URL, INPATH)
    ts = read_pdf(INPATH)
    rows = combine_rows(ts)
    cats_raw = parse_codes(rows)

    # Widely used and very useful, even though not included in the official spec
    categories: dict[str, typing.Any] = {
        "0": {
            "title": "National Total",
            "comment": "All emissions and removals",
            "children": [["1", "2", "3", "4", "5", "6", "7"]],
        }
    }

    categories.update(parse_categories(cats_raw))
    add_relationships(categories)

    spec = {
        "name": "IPCC1996",
        "title": "IPCC GHG emission categories (1996)",
        "comment": "IPCC classification of green-house gas emissions and removals into"
        " categories, 1996 edition",
        "references": "IPCC 1996, Revised 1996 IPCC Guidelines for National Greenhouse"
        " Gas Inventories: Reporting Instructions,"
        " Volume 1, Chapter 1.1, pages 1.2ff,"
        " https://www.ipcc-nggip.iges.or.jp/public/gl/guidelin/ch1ri.pdf",
        "institution": "IPCC",
        "last_update": "1996-09-13",
        "hierarchical": True,
        "version": "1996",
        "total_sum": True,
        "categories": categories,
        "canonical_top_level_category": "0",
    }

    categories = spec["categories"]
    categories["1.A.1"]["comment"] = categories["1.A.1"]["comment"].replace(
        "energyproducing", "energy producing"
    )

    categories["1.A.2"]["title"] = "Manufacturing Industries and Construction"
    categories["1.A.2"]["comment"] = categories["1.A.2"]["comment"].replace(
        "Emissions from the industry sector should be specified by subsectors that "
        "correspond to the International Standard Industrial Classification of All "
        "Economic Activities (ISIC).",
        "Emissions from the industry sector should be specified by subsectors that "
        "correspond to the International Standard Industrial Classification of All "
        "Economic Activities, 3rd Edition (ISIC) "
        " [International Standard Industrial Classification of all Economic Activities,"
        " Series M No. 4, Rev. 3, United Nations, New York, 1990].",
    )

    categories["1.A.5"]["title"] = "Other"

    categories["2.C.4"]["title"] = "SF6 used in Aluminium and Magnesium Foundries"

    categories["4.B.10"]["title"] = "Anaerobic Lagoons"

    categories["4.C.3.a"]["title"] = "Water Depth 50-100 cm"
    categories["4.C.3.b"]["title"] = "Water Depth > 100 cm"

    categories["5.A.5"]["comment"] = (
        "Emissions and removals of CO2 from other biomass categories, including"
        " village and farm trees, etc."
        " This category"
        " is intended to account for biomass which is found in locations other than"
        " the major ecosystem types listed. This includes dispersed trees in villages,"
        " farms, urban areas, etc., and also includes additional ecosystem types which"
        " may be important for biomass accounting in specific countries."
        " Afforestation programmes which create forests will be accounted for in the"
        " appropriate forest ecosystem category. Afforestation which produces"
        " dispersed trees, e.g., urban tree planting, would be accounted for in"
        " “Other.”"
    )

    categories["5.D"]["title"] = "CO2 Emissions and Removals From Soil"

    IPCC1996 = climate_categories.HierarchicalCategorization.from_spec(spec)

    IPCC1996.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
