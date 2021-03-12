"""Run this via `make climate_categories/data/IPCC1996.yaml` in the main directory."""

import pathlib

import camelot
from utils import download_cached

import climate_categories

URL = "https://www.ipcc-nggip.iges.or.jp/public/gl/guidelin/ch1ri.pdf"
INPATH = pathlib.Path("./data_generation/IPCC1996.pdf")
OUTPATH = pathlib.Path("./climate_categories/data/IPCC1996.yaml")
OUTPATH_PICKLE = pathlib.Path("./climate_categories/data/IPCC1996.pickle")


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
        for i, (code_name, definition) in table.df.iterrows():
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
    for (code_title, definition) in rows:
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
    for (code, title, definition) in cats_raw:
        title = " ".join(title.split()).title()
        definition = " ".join(definition.split()).replace("- ", "")

        altcode = code.replace(".", "")
        altcode2 = code.replace(".", " ")
        spec = {
            "title": title,
            "comment": definition,
        }
        if altcode != code:
            spec["alternative_codes"] = [altcode, altcode2]

        if code in cats:
            raise ValueError(f"{code!r} exists twice")
        cats[code] = spec

    return cats


def main():
    download_cached(URL, INPATH)
    ts = read_pdf(INPATH)
    rows = combine_rows(ts)
    cats_raw = parse_codes(rows)
    categories = parse_categories(cats_raw)

    spec = {
        "name": "IPCC1996",
        "title": "IPCC GHG emission categories (1996)",
        "comment": "IPCC classification of green-house gas emissions and removals into"
        " categories, 1996 edition",
        "references": "IPCC 1996, Revised 1996 IPCC Guidelines for National Greenhouse"
        " Gas Inventories: Reporting Instructions,"
        " Volume 1, Chapter 1.1, pages 1.2ff, "
        " https://www.ipcc-nggip.iges.or.jp/public/gl/guidelin/ch1ri.pdf",
        "institution": "IPCC",
        "last_update": "1996-09-13",
        "version": "1996",
        "total_sum": "True",
        "categories": categories,
    }

    IPCC1996 = climate_categories.HierarchicalCategorization.from_spec(spec)

    IPCC1996.to_yaml(OUTPATH)
    IPCC1996.to_pickle(OUTPATH_PICKLE)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)

    # TODO:
    # * add relationships.


if __name__ == "__main__":
    main()
