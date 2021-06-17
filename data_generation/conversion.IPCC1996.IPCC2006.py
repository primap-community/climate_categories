"""Run this via `make climate_categories/data/conversion.IPCC1996.IPCC2006.csv` in the
main directory."""

import climate_categories as cc


def level(code):
    return code.count(".")


def normalize_code(code, categorization):
    """Return the canonical code for the category."""
    return categorization[code].codes[0]


def main():
    """Generate the conversion file from the metadata in cc.IPCC2006."""
    convs_long = []
    for cat in cc.IPCC2006.values():
        for ipcc1996_cat in cat.info.get("corresponding_categories_IPCC1996", []):
            convs_long.append((cat.codes[0], normalize_code(ipcc1996_cat, cc.IPCC1996)))

    # algo idea:
    # Build groups at the same level of hierarchy which map to a group in the other
    # hierarchy. Within groups and hierarchies, categories are on the same level,
    # but the groups don't need to be at the same level.
    corresponding_groups = []
    for cat06, cat96 in convs_long:
        group06 = [
            c06
            for c06, c96 in convs_long
            if c96 == cat96 and level(c06) == level(cat06)
        ]
        group96 = [
            c96
            for c06, c96 in convs_long
            if c06 == cat06 and level(c96) == level(cat96)
        ]
        if (group06, group96) not in corresponding_groups:
            corresponding_groups.append((group06, group96))

    with open("./climate_categories/data/conversion.IPCC1996.IPCC2006.csv", "w") as fd:
        fd.write("IPCC1996,IPCC2006\n")
        for lg, rg in corresponding_groups:
            fd.write(" + ".join(lg) + "," + " + ".join(rg) + "\n")


if __name__ == "__main__":
    print(
        "./climate_categories/data/conversion.IPCC1996.IPCC2006.csv is now maintained"
        "by hand due to the many special cases that can't be handled automatically."
        " This script was only used to generate it initially."
    )
