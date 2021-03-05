"""Run this via `make climate_categories/data/IPCC2006.yaml` in the main directory."""

import itertools
import pathlib
import shutil

import camelot
import requests

import climate_categories

URL = (
    "https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/1_Volume1/"
    "V1_8_Ch8_Reporting_Guidance.pdf"
)
INPATH = pathlib.Path("./data_generation/IPCC2006.pdf")
OUTPATH = pathlib.Path("./climate_categories/data/IPCC2006.yaml")


def main():
    if not INPATH.exists():
        print(f"{INPATH} not found, downloading it.")
        r = requests.get(URL, stream=True)
        if r.status_code == 200:
            with INPATH.open("wb") as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            raise RuntimeError(f"Could not download {URL!r}")

    t = camelot.read_pdf(
        str(INPATH),
        pages="10-33",
        flavor="stream",
        table_areas=["74,744,527,35"],
        columns=["251,468,498"],
        row_tol=3,
    )

    tend = camelot.read_pdf(
        str(INPATH),
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
        for i, row in table.df.iterrows():
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

    categories = {}

    for code_name, definition, code_96, gases in cats_raw:
        try:
            code_raw, title = code_name.rsplit("\n", 1)
        except ValueError:
            code_raw, title = code_name.rsplit(" ", 1)
        code = ".".join(code_raw.split())
        altcode = "".join(code_raw.split())
        comment = definition.strip().replace("\n", " ")

        categories[code] = {
            "title": title.strip(),
            "comment": comment.strip(),
        }

        if code != altcode:
            categories[code]["alternative_codes"] = [altcode]

        gases_stripped = [x.strip() for x in gases.split(",") if x.strip()]
        if gases_stripped:
            print(gases_stripped)
            categories[code]["info"] = {"gases": gases_stripped}

        if code_96.strip():
            if "info" not in categories[code]:
                categories[code]["info"] = {}
            categories[code]["info"]["corresponding_categories_IPCC1996"] = [
                x.strip() for x in code_96.split(",")
            ]

    for parent_code in categories:
        prefix = parent_code + "."
        children = []
        for child_code in categories:

            if child_code.startswith(prefix) and "." not in child_code[len(prefix) :]:
                children.append(child_code)
        if children:
            categories[parent_code]["children"] = [children]

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
        "version": "2006",
        "total_sum": "True",
        "categories": categories,
    }

    IPCC2006 = climate_categories.HierarchicalCategorization.from_spec(spec)

    IPCC2006.to_yaml(OUTPATH)


if __name__ == "__main__":
    main()
