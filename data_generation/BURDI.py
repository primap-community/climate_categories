"""Run this via `make climate_categories/data/BURDI.yaml` in the main directory."""
import pathlib

import natsort
import treelib
from unfccc_di_api import UNFCCCApiReader

import climate_categories

OUTPATH = pathlib.Path("./climate_categories/data/BURDI.yaml")

# there are some categories with different IDs, but the same code and title.
# These are the categories directly under the top-level totals (e.g. 1. Energy),
# which are included in the category hierarchy once under the Total with and once
# under the Total without LULUCF.
#
# they can be safely merged because they are not actually different.


def parse_categories(r):
    categories = {}
    # there are unused intermediate categories needed for tree traversal only existing
    # in the tree and also categories without metadata only in the variables
    all_category_ids = set(r.non_annex_one_reader.category_tree.nodes.keys()).union(
        set(r.non_annex_one_reader.variables["categoryId"])
    )
    for category_id in all_category_ids:
        if category_id == 15164:
            # generic "Totals" category that is violating the total_sum rule and unused
            continue

        try:
            raw_category = r.non_annex_one_reader.category_tree.nodes[category_id].tag
        except KeyError:
            if category_id == 10502:
                raw_category = "Total land area"
            elif category_id == 10503:
                raw_category = "GDP"
            elif category_id == 10504:
                raw_category = "Total population"
            else:
                raw_category = f"{category_id} Unknown category no. {category_id}"

        if raw_category[0].isnumeric():
            code, title = raw_category.split(maxsplit=1)
            if code.endswith("."):
                altcodes = [code, str(category_id)]
                code = code[:-1]
            else:
                altcodes = [str(category_id)]
        elif raw_category == "Memo Items":
            # needs special handling because it doesn't have a proper code but
            # is included twice with different category_ids
            code = "14568"
            title = raw_category
            altcodes = ["24568"]
        else:
            code = str(category_id)
            title = raw_category
            altcodes = []

        if code not in categories:
            categories[code] = {"title": title}

        altcode = code.replace(".", "")
        if altcode != code:
            altcodes.append(altcode)
            altcodes.append(code.replace(".", " "))

        if altcodes:
            if "alternative_codes" not in categories[code]:
                categories[code]["alternative_codes"] = []
            for ac in altcodes:
                if ac not in categories[code]["alternative_codes"]:
                    categories[code]["alternative_codes"].append(ac)

        if "info" not in categories[code]:
            categories[code]["info"] = {}
        if "numerical_ids" not in categories[code]["info"]:
            categories[code]["info"]["numerical_ids"] = []
        categories[code]["info"]["numerical_ids"].append(str(category_id))

    return categories


def add_relationships(r, categories):
    for code in categories:
        child_codes = []
        for nid in categories[code]["info"]["numerical_ids"]:
            try:
                for child in r.non_annex_one_reader.category_tree.children(int(nid)):
                    child_code = [
                        xcode
                        for xcode, x in categories.items()
                        if str(int(child.identifier)) in x["info"]["numerical_ids"]
                    ][0]
                    child_codes.append(child_code)
            except treelib.tree.NodeIDAbsentError:
                # parent code is not included in the metadata
                # can't guess children without metadata
                pass

        if child_codes:
            categories[code]["children"] = [child_codes]


def sort_categories(categories):
    sorted_categories = {}
    # start with "special" categories without a normal X.Y etc. numbering
    special = []
    normal = []
    for code in categories:
        if code.isnumeric() and int(code) > 10:
            special.append(code)
        else:
            normal.append(code)

    sorted_codes = sorted(special, key=int) + natsort.natsorted(normal)

    for cat in sorted_codes:
        sorted_categories[cat] = categories[cat]

    return sorted_categories


def main():
    r = UNFCCCApiReader()
    categories = parse_categories(r)
    add_relationships(r, categories)
    categories = sort_categories(categories)

    spec = {
        "name": "BURDI",
        "title": "BUR GHG emission categories (DI query interface)",
        "comment": "Biannual Update Report categories of GHG emissions and removals "
        "and some other quantities as obtained from the di.unfccc.int flexible query "
        "interface",
        "references": "https://unfccc.int/process-and-meetings/"
        "transparency-and-reporting/greenhouse-gas-data/data-interface-help#eq-7 and "
        "decision 17/CP.8, 'Guidelines for the preparation of national communications "
        "from Parties not included in Annex I to the Convention' available at "
        "https://unfccc.int/files/meetings/workshops/other_meetings/application/pdf/"
        "dec17-cp.pdf",
        "institution": "UNFCCC",
        "last_update": "2021-11-05",
        "hierarchical": True,
        "total_sum": True,
        "categories": categories,
        "canonical_top_level_category": "24540",  # Total including LULUCF
    }

    CRFDI = climate_categories.HierarchicalCategorization.from_spec(spec)

    CRFDI.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
