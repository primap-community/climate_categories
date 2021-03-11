"""Run this via `make climate_categories/data/IPCC2006.yaml` in the main directory."""

import pathlib

import camelot
from utils import download_cached

# import climate_categories

URL = "https://www.ipcc-nggip.iges.or.jp/public/gl/guidelin/ch1ri.pdf"
INPATH = pathlib.Path("./data_generation/IPCC1996.pdf")
OUTPATH = pathlib.Path("./climate_categories/data/IPCC1996.yaml")
OUTPATH_PICKLE = pathlib.Path("./climate_categories/data/IPCC1996.pickle")


def parse_pages(pages, areas, columns) -> list:
    ts = []
    for page in pages:
        t = camelot.read_pdf(
            str(INPATH),
            pages=str(page),
            flavor="stream",
            table_areas=[areas[page % 2]],
            columns=[columns[page % 2]],
            row_tol=10,
        )
        ts.append(t[0])
    return ts


def main():
    download_cached(URL, INPATH)

    # 1 energy
    ts = []
    ts += parse_pages(
        pages=range(3, 8),
        areas=["168,723,552,120", "43,723,468,114"],
        columns=["279", "194"],
    )
    # 2 industrial processes
    # 3 solvent and other product use
    ts += parse_pages(
        pages=range(8, 11),
        areas=["140,723,541,135", "0,723,398,117"],
        columns=["285", "206"],
    )
    # 4 agriculture
    ts += parse_pages(
        pages=range(11, 14),
        areas=["157,723,546,95", "55,723,470,88"],
        columns=["276", "193"],
    )
    # 5 agriculture
    ts += parse_pages(
        pages=range(14, 17),
        areas=["127,723,550,214", "55,723,466,208"],
        columns=["276", "198"],
    )
    # 6 waste
    ts.append(
        camelot.read_pdf(
            str(INPATH),
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
            str(INPATH),
            pages="18",
            flavor="stream",
            table_areas=["180,723,552,670"],
            columns=["288"],
            row_tol=10,
        )[0]
    )

    cats_raw = []

    for table in ts:
        code_name_previously_empty = True
        definition_previously_empty = True
        current_code_name = None
        current_definition = None
        for i, row in table.df.iterrows():
            code_name, definition = row
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
                current_code_name in ("2\nINDUSTRIAL",)
                or definition.startswith(
                    "petroleum  products,  the",
                )
            ):
                # a new cell started
                if current_code_name is not None:
                    cats_raw.append((current_code_name, current_definition))
                current_code_name = ""
                current_definition = ""

            if code_name:
                current_code_name += f" {code_name}"
            if definition:
                current_definition += f" {definition}"

            code_name_previously_empty = code_name_empty
            definition_previously_empty = definition_empty

        cats_raw.append((current_code_name, current_definition))

    for cat in cats_raw:
        print()
        print(cat[0].replace("\n", " "))
        print(cat[1].replace("\n", " "))

    # TODO:
    # * figure out codes and titles for all categories.
    # * normalize titles.
    # * generate actual specs.
    # * add relationships.


if __name__ == "__main__":
    main()
