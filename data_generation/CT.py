"""Run this via `make climate_categories/data/CT.yaml` in the main directory."""

import pathlib

import climate_categories

# import ctrace as ct  # type: ignore
# from ctrace.constants import GAS_LIST  # type: ignore

OUTPATH = pathlib.Path("./climate_categories/data/CT.yaml")

# Ideally this list will be auto-generated
ct_categories = [
    "agriculture|crop-residues",
    "agriculture|cropland-fires",
    "agriculture|enteric-fermentation-cattle-operation",
    "agriculture|enteric-fermentation-cattle-pasture",
    "agriculture|enteric-fermentation-other",
    "agriculture|manure-applied-to-soils",
    "agriculture|manure-left-on-pasture-cattle",
    "agriculture|manure-management-cattle-operation",
    "agriculture|manure-management-other",
    "agriculture|other-agricultural-soil-emissions",
    "agriculture|rice-cultivation",
    "agriculture|synthetic-fertilizer-application",
    "buildings|non-residential-onsite-fuel-usage",
    "buildings|other-onsite-fuel-usage",
    "buildings|residential-onsite-fuel-usage",
    "fluorinated-gases|fluorinated-gases",
    "forestry-and-land-use|forest-land-clearing",
    "forestry-and-land-use|forest-land-degradation",
    "forestry-and-land-use|forest-land-fires",
    "forestry-and-land-use|net-forest-land",
    "forestry-and-land-use|net-shrubgrass",
    "forestry-and-land-use|net-wetland",
    "forestry-and-land-use|removals",
    "forestry-and-land-use|shrubgrass-fires",
    "forestry-and-land-use|water-reservoirs",
    "forestry-and-land-use|wetland-fires",
    "fossil-fuel-operations|coal-mining",
    "fossil-fuel-operations|oil-and-gas-production",
    "fossil-fuel-operations|oil-and-gas-refining",
    "fossil-fuel-operations|oil-and-gas-transport",
    "fossil-fuel-operations|other-fossil-fuel-operations",
    "fossil-fuel-operations|solid-fuel-transformation",
    "manufacturing|aluminum",
    "manufacturing|cement",
    "manufacturing|chemicals",
    "manufacturing|food-beverage-tobacco",
    "manufacturing|glass",
    "manufacturing|iron-and-steel",
    "manufacturing|lime",
    "manufacturing|other-chemicals",
    "manufacturing|other-manufacturing",
    "manufacturing|other-metals",
    "manufacturing|petrochemical-steam-cracking",
    "manufacturing|pulp-and-paper",
    "manufacturing|textiles-leather-apparel",
    "manufacturing|wood-and-wood-products",
    "mineral-extraction|bauxite-mining",
    "mineral-extraction|copper-mining",
    "mineral-extraction|iron-mining",
    "mineral-extraction|other-mining-quarrying",
    "mineral-extraction|rock-quarrying",
    "mineral-extraction|sand-quarrying",
    "power|electricity-generation",
    "power|heat-plants",
    "power|other-energy-use",
    "transportation|domestic-aviation",
    "transportation|domestic-shipping",
    "transportation|international-aviation",
    "transportation|international-shipping",
    "transportation|other-transport",
    "transportation|railways",
    "transportation|road-transportation",
    "waste|biological-treatment-of-solid-waste-and-biogenic",
    "waste|domestic-wastewater-treatment-and-discharge",
    "waste|incineration-and-open-burning-of-waste",
    "waste|industrial-wastewater-treatment-and-discharge",
    "waste|solid-waste-disposal",
]


def main():
    categories = {}

    for name in ct_categories:
        categories[name] = {"title": name}

    categories["Emissions"] = {"title": "CT Emissions", "children": [[]]}

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
        "total_sum": True,
        "categories": categories,
        "canonical_top_level_category": "Emissions",
    }

    CT = climate_categories.HierarchicalCategorization.from_spec(spec.copy())

    CT.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
