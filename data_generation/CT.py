"""Run this via `make climate_categories/data/CT.yaml` in the main directory."""

import pathlib

import climate_categories

OUTPATH = pathlib.Path("./climate_categories/data/CT.yaml")


ct_categories = {
    "agriculture": [
        # sub-sector and comment
        ("agriculture|crop-residues", "estimates compiled from FAOSTAT"),
        ("agriculture|cropland-fires", "compiled from EDGAR"),
        ("agriculture|enteric-fermentation-cattle-operation", ""),
        ("agriculture|enteric-fermentation-cattle-pasture", ""),
        (
            "agriculture|enteric-fermentation-other",
            "estimated using FAOSTAT data for years 2015 to 2021, with the remaining years forward filled.",
        ),
        ("agriculture|manure-applied-to-soils", ""),
        ("agriculture|manure-left-on-pasture-cattle", ""),
        ("agriculture|manure-management-cattle-operation", ""),
        (
            "agriculture|manure-management-other",
            "estimated using FAOSTAT data for years 2015 to 2021, with the remaining years forward filled.",
        ),
        (
            "agriculture|other-agricultural-soil-emissions",
            "compiled with FAOSTAT and EDGAR. See Moore et al. (2024)",
        ),
        ("agriculture|rice-cultivation", "Estimates using Sentinel-1A and -2A/B"),
        (
            "agriculture|synthetic-fertilizer-application",
            "Estimates using crop productivity data",
        ),
    ],
    "buildings": [
        (
            "buildings|non-residential-onsite-fuel-usage",
            "Disaggregation of EDGAR v8 data",
        ),
        ("buildings|other-onsite-fuel-usage", "Disaggregation of EDGAR v8 data"),
        ("buildings|residential-onsite-fuel-usage", "Disaggregation of EDGAR v8 data"),
    ],
    "fluorinated-gases": [("fluorinated-gases|fluorinated-gases", "Based on EDGAR")],
    "forestry-and-land-use": [
        ("forestry-and-land-use|forest-land-clearing", ""),
        ("forestry-and-land-use|forest-land-degradation", ""),
        ("forestry-and-land-use|forest-land-fires", ""),
        ("forestry-and-land-use|net-forest-land", ""),
        ("forestry-and-land-use|net-shrubgrass", ""),
        ("forestry-and-land-use|net-wetland", ""),
        ("forestry-and-land-use|removals", ""),
        ("forestry-and-land-use|shrubgrass-fires", ""),
        ("forestry-and-land-use|water-reservoirs", ""),
        ("forestry-and-land-use|wetland-fires", ""),
    ],
    "fossil-fuel-operations": [
        ("fossil-fuel-operations|coal-mining", ""),
        ("fossil-fuel-operations|oil-and-gas-production", ""),
        ("fossil-fuel-operations|oil-and-gas-refining", ""),
        ("fossil-fuel-operations|oil-and-gas-transport", ""),
        ("fossil-fuel-operations|other-fossil-fuel-operations", ""),
        ("fossil-fuel-operations|solid-fuel-transformation", ""),
    ],
    "manufacturing": [
        ("manufacturing|aluminum", ""),
        ("manufacturing|cement", ""),
        ("manufacturing|chemicals", ""),
        ("manufacturing|food-beverage-tobacco", ""),
        ("manufacturing|glass", ""),
        ("manufacturing|iron-and-steel", ""),
        ("manufacturing|lime", ""),
        ("manufacturing|other-chemicals", ""),
        ("manufacturing|other-manufacturing", ""),
        ("manufacturing|other-metals", ""),
        ("manufacturing|petrochemical-steam-cracking", ""),
        ("manufacturing|pulp-and-paper", ""),
        ("manufacturing|textiles-leather-apparel", ""),
        ("manufacturing|wood-and-wood-products", ""),
    ],
    "mineral-extraction": [
        ("mineral-extraction|bauxite-mining", ""),
        ("mineral-extraction|copper-mining", ""),
        ("mineral-extraction|iron-mining", ""),
        ("mineral-extraction|other-mining-quarrying", ""),
        ("mineral-extraction|rock-quarrying", ""),
        ("mineral-extraction|sand-quarrying", ""),
    ],
    "power": [
        ("power|electricity-generation", ""),
        ("power|heat-plants", ""),
        ("power|other-energy-use", ""),
    ],
    "transportation": [
        ("transportation|domestic-aviation", ""),
        ("transportation|domestic-shipping", ""),
        ("transportation|international-aviation", ""),
        ("transportation|international-shipping", ""),
        ("transportation|other-transport", ""),
        ("transportation|railways", ""),
        ("transportation|road-transportation", ""),
    ],
    "waste": [
        ("waste|biological-treatment-of-solid-waste-and-biogenic", ""),
        ("waste|domestic-wastewater-treatment-and-discharge", ""),
        ("waste|incineration-and-open-burning-of-waste", ""),
        ("waste|industrial-wastewater-treatment-and-discharge", ""),
        ("waste|solid-waste-disposal", ""),
    ],
}


def main():
    categories = {}

    sector_categories = list(ct_categories.keys())

    categories["all-emissions"] = {
        "title": "all-emissions",
        "children": [sector_categories],
    }

    for sector_category in sector_categories:
        categories[sector_category] = {
            "title": sector_category,
            "children": [[i for i, j in ct_categories[sector_category]]],
        }
        for name, comment in ct_categories[sector_category]:
            categories[name] = {"title": name}
            if comment:
                categories[name]["comment"] = comment

    spec = {
        "name": "CT",
        "title": "Climate Trace Inventory",
        "comment": "Categorisation may change with new releases. "
        "Changelog is here: https://github.com/climatetracecoalition/methodology-documents ",
        "references": (
            "Climate TRACE (2024), Climate TRACE Emissions Inventory, https://climatetrace.org"
        ),
        "institution": "Climate TRACE",
        "last_update": "2025-04-02",
        "hierarchical": True,
        "version": "v4",
        "total_sum": False,
        "categories": categories,
        "canonical_top_level_category": "all-emissions",
    }

    CT = climate_categories.HierarchicalCategorization.from_spec(spec.copy())

    CT.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
