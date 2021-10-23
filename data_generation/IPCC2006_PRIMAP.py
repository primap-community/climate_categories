"""Run this via `make climate_categories/data/IPCC2006_PRIMAP.yaml` in the main
directory."""
import datetime
import pathlib

import climate_categories

OUTPATH = pathlib.Path("./climate_categories/data/IPCC2006_PRIMAP.yaml")

# IPCC2006 categorization amended with custom categories


def main():
    categories = {
        "M.0.EL": {
            "title": "Total emissions excluding LULUCF",
            "comment": "All emissions and removals except for Land Use, Land "
            "Use Change, and Forestry",
        },
        "M.1.A.2.m": {
            "title": "Other manufacturing (CRF)",
            "comment": "Other Manufacturing (as in CRF tables) "
            "(Table 1.A(a)s2, row Other (please specify)",
        },
        "M.1.B.1.c": {
            "title": "Other emission from solid fuels (CRF)",
            "comment": "Table 1s2: c.  Other (as specified in table 1.B.1)",
        },
        "M.LULUCF": {
            "title": "Land Use, Land Use Change, and Forestry",
            "comment": "LULUCF part of AFOLU",
        },
        "M.AG": {"title": "Agriculture", "comment": "Agricultural part of AFOLU"},
        "M.AG.ELV": {
            "title": "Agriculture excluding Livestock",
            "comment": "Agricultural part of AFOLU excluding livestock",
        },
        "3.A.1.i": {"title": "Poultry", "comment": "From CRF data"},
        "M.BK": {
            "title": "International Bunkers",
            "comment": "M category as not included in national total in CRF data",
        },
        "M.BK.A": {
            "title": "International Aviation",
            "comment": "International aviation bunkers. same as 1.A.3.a.i, "
            "excluded from CRF total",
        },
        "M.BK.M": {
            "title": "International Navigation",
            "comment": "International marine bunkers. same as 1.A.3.d.i, "
            "excluded from CRF total",
        },
        "M.MULTIOP": {
            "title": "Multilateral Operations",
            "comment": "Multilateral operations, same as 1.A.5.c, excluded "
            "from CRF total",
        },
        "1.A.1.bc": {
            "title": "Petroleum Refining - Manufacture of Solid Fuels and "
            "Other Energy Industries",
            "comment": "Sum of 1.A.1.b and 1.A.1.c",
        },
        "1.A.3.b_noRES": {
            "title": "Road Transportation no resuspension",
            "comment": "Emissions for Road transportation without the "
            "effect from resuspension of particles.",
        },
    }
    children = [
        ("0", ("M.0.EL", "M.LULUCF")),
        ("M.0.EL", ("1", "2", "M.AG", "4", "5")),
        ("1.A.1.bc", ("1.A.1.b", "1.A.1.c")),
        ("1.A.1", ("1.A.1.a", "1.A.1.bc")),
        (
            "1.A.2",
            (
                "1.A.2.a",
                "1.A.2.b",
                "1.A.2.c",
                "1.A.2.d",
                "1.A.2.e",
                "1.A.2.f",
                "M.1.A.2.m",
            ),
        ),
        ("1.A.3", ("1.A.3.a", "1.A.3.b_noRES", "1.A.3.c", "1.A.3.d", "1.A.3.e")),
        ("M.AG", ("3.A", "M.AG.ELV")),
        ("3", ("M.AG", "M.LULUCF")),
        (
            "3.A.1",
            (
                "3.A.1.a",
                "3.A.1.b",
                "3.A.1.c",
                "3.A.1.d",
                "3.A.1.e",
                "3.A.1.f",
                "3.A.1.g",
                "3.A.1.h",
                "3.A.1.i",
                "3.A.1.j",
            ),
        ),
        ("M.BK", ("M.BK.A", "M.BK.M")),
    ]
    name = "PRIMAP"
    title = " with custom categories used in PRIMAP"
    comment = (
        " with additional categories needed for analyses "
        "and for datasets like PRIMAP-crf or EDGAR v6.0"
    )

    ipcc2006_primap = climate_categories.IPCC2006.extend(
        name=name,
        title=title,
        comment=comment,
        last_update=datetime.date.fromisoformat("2021-10-12"),
        categories=categories,
        children=children,
    )
    ipcc2006_primap.institution = "PIK"
    ipcc2006_primap.canonical_top_level_category = ipcc2006_primap["0"]

    ipcc2006_primap.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
