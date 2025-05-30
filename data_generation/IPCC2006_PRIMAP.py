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
        "M.BIO": {
            "title": "CO₂ emissions from biomass burning",
            "comment": "CO₂ emissions from biomass burning for energy use",
        },
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
        "M.3.C.45.AG": {
            "title": "The sum of agriculture-related emissions of 3.C.4 and 3.C.5",
            "comment": "Needed for conversion from BURDI to IPCC2006_PRIMAP.",
        },
        "M.3.C.4.SF": {
            "title": "Direct synthetic fertilisers emissions from managed soils",
            "comment": "The share of emissions that come from synthetic fertilisers",
        },
        "M.3.C.5.SF": {
            "title": "Indirect synthetic fertilisers emissions from managed soils",
            "comment": "The share of emissions that come from synthetic fertilisers",
        },
        "M.NFC": {
            "title": "Net forest conversion",
            "comment": "Needed to map net forest conversion from FAOSTAT dataset",
        },
        "M.3.C.1.AG": {
            "title": "The share of agriculture-related emissions of 3.C.1",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.C.AG": {
            "title": "The share of agriculture-related emissions of 3.C",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.B.2.FOS": {
            "title": "Share of emissions from fires in organic soils of 3.B.2",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.B.2.DOS": {
            "title": "Share of emissions from drained organic soils of 3.B.2",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.B.3.DOS": {
            "title": "Share of emissions from drained organic soils of 3.B.3",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.C.1.a": {
            "title": "Biomass burning in forest lands, but not in 3.C.1. sum",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.C.1.c": {
            "title": "Biomass burning in grasslands, but not in 3.C.1. sum",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "3.C.4.a": {
            "title": "Inorganic N fertilisers",
        },
        "3.C.4.b": {
            "title": "Manure applied to soils",
            "comment": "Organic N applied as fertiliser (manure and sewage sludge)",
        },
        "3.C.4.c": {
            "title": "Manure left on pasture",
            "comment": "Urine and dung N deposited on pasture, range and paddock by grazing animals",
        },
        "3.C.4.d": {
            "title": "Crop residues",
        },
        "M.3.C.45.MA": {
            "title": "Direct and indirect emissions from manure applied to soils",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.C.4.MA": {
            "title": "Direct emissions from manure applied to soils",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.C.5.MA": {
            "title": "Indirect emissions from manure applied to soils",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.C.45.MP": {
            "title": "Direct and indirect emissions from manure left on pasture",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.C.4.MP": {
            "title": "Direct emissions from manure left on pasture",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.C.5.MP": {
            "title": "Indirect emissions from manure left on pasture",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.C.45.CR": {
            "title": "Direct and indirect emissions from crop residues",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.C.4.CR": {
            "title": "Direct emissions from crop residues",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.C.5.CR": {
            "title": "Indirect emissions from crop residues",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.C.4.DOS.GL": {
            "title": "Direct emissions from drained organic soils on grass land",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.3.C.4.DOS.CL": {
            "title": "Direct emissions from drained organic soils on crop land",
            "comment": "Needed for conversion from FAO to IPCC2006_PRIMAP.",
        },
        "M.fluorinated_gases": {
            "title": "Fluorinated gases",
            "comment": "Needed for conversion from climate TRACE dataset",
        },
        "M.3.B.REM": {
            "title": "Forestry and land-use removals",
            "comment": "Needed for conversion from climate TRACE dataset.",
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
        ("3.C.4", ("3.C.4.a", "3.C.4.b", "3.C.4.c", "3.C.4.d")),
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
        last_update=datetime.date.fromisoformat("2025-01-12"),
        categories=categories,
        children=children,
    )
    ipcc2006_primap.institution = "Climate Resource"
    ipcc2006_primap.canonical_top_level_category = ipcc2006_primap["0"]

    ipcc2006_primap.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
