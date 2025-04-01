"""Run this via `make climate_categories/data/FAO.yaml` in the main
directory."""

import pathlib

import climate_categories as cc

OUTPATH = pathlib.Path("./climate_categories/data/FAO.yaml")


def main():
    spec = {
        "name": "FAO",
        "title": (
            "Food and Agriculture Organization of the United Nations (FAO) "
            "FAOSTAT data set categorisation"
        ),
        "comment": "Needed to add FAOSTAT data to PRIMAP-hist",
        "references": "",
        "institution": "FAO",
        "hierarchical": True,
        "last_update": "2024-12-10",
        "version": "2024",
        "total_sum": True,
        "canonical_top_level_category": "0",
    }

    categories = {}

    # 0. main categories
    categories["0"] = {
        "title": "Total",
        "comment": "All emissions and removals",
        "children": [["1", "2", "3", "4", "5", "6", "7"]],
    }
    children_1 = ["1.A", "1.B"]
    children_2 = ["2.A", "2.B", "2.C", "2.D", "2.E"]
    children_3 = [f"3.{i}" for i in "ABCDEFGHIJKLMNOPQR"]

    main_categories = (
        # category code, name and comment, gases, children
        ("1", "Crops", ["CH4", "N2O"], children_1),
        (
            "2",
            "Energy use in agriculture",
            ["CH4", "N2O", "CO2"],
            children_2,
        ),
        ("3", "Livestock", ["CH4", "N2O"], children_3),
    )
    for code, name, gases, children in main_categories:
        categories[code] = {
            "title": name,
            "comment": name,
            "children": [children],
            "info": {"gases": gases},
        }

    # 1. crops
    # all crops category
    code_all_crops = "1.A"
    codes_crops = [f"1.A.{i}" for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
    categories[code_all_crops] = {
        "title": "All crops",
        "comment": "All crops",
        "children": [codes_crops],
        "info": {"gases": ["CH4", "N2O"]},
    }

    crops = [
        "Wheat",
        "Rice",
        "Potatoes",
        "Millet",
        "Barley",
        "Maize (corn)",
        "Sugar cane",
        "Beans, dry",
        "Oats",
        "Rye",
        "Sorghum",
        "Soya beans",
    ]

    crop_burnings = [
        True,
        True,
        False,
        False,
        False,
        True,
        True,
        False,
        False,
        False,
        False,
        False,
    ]
    rice_cultivations = [
        False,
        True,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    ]

    for crop, code, crop_burning, rice_cultivation in zip(
        crops, codes_crops, crop_burnings, rice_cultivations
    ):
        # all crops have at least N2O emissions
        gases_main = "N2O"

        if crop_burning or rice_cultivation:
            gases_main = ["CH4", "N2O"]

        # all crops have at least crop residues as child
        children_main = [f"{code}.a"]

        if crop_burning:
            children_main.append(f"{code}.b")

        if rice_cultivation:
            children_main.append(f"{code}.c")

        categories[f"{code}"] = {
            "title": f"{crop}",
            "comment": f"{crop}",
            "info": {"gases": gases_main},
            "children": [children_main],
        }

        # crop residues (every crop has it)
        categories[f"{code}.a.i"] = {
            "title": f"{crop} crop residues direct emissions",
            "comment": f"{crop} crop residues direct emissions",
            "info": {"gases": ["N2O"]},
        }

        categories[f"{code}.a.ii"] = {
            "title": f"{crop} crop residues indirect emissions",
            "comment": f"{crop} crop residues indirect emissions",
            "info": {"gases": ["N2O"]},
        }

        categories[f"{code}.a"] = {
            "title": f"{crop} crop residues",
            "comment": f"{crop} crop residues",
            "info": {"gases": ["N2O"]},
            "children": [[f"{code}.a.ii", f"{code}.a.i"]],
        }

        if crop_burning:
            categories[f"{code}.b"] = {
                "title": f"{crop} burning crop residues",
                "comment": f"{crop} burning crop residues",
                "info": {"gases": ["CH4", "N2O"]},
            }
        if rice_cultivation:
            categories[f"{code}.c"] = {
                "title": "Rice cultivation",
                "comment": "Rice cultivation",
                "info": {"gases": ["CH4"]},
            }

    # synthetic fertilisers
    codes_synthetic_fertilisers = ["1.B", "1.B.1", "1.B.2", "1.B.2.a", "1.B.2.b"]
    names = [
        "Synthetic fertilisers",
        "Direct emissions",
        "Indirect emissions",
        "Indirect emissions that volatilise",
        "Indirect emissions that leach",
    ]
    children_cats = [["1.B.1", "1.B.2"], None, ["1.B.2.a", "1.B.2.b"], None, None]

    for code, name, child_cat in zip(codes_synthetic_fertilisers, names, children_cats):
        categories[code] = {
            "title": name,
            "comment": name,
            "info": {"gases": ["N2O"]},
        }
        if child_cat:
            categories[code]["children"] = [child_cat]

    # 2. energy use
    names = [
        "Natural gas",
        "Electricity",
        "Coal",
        "Heat",
        "Petroleum",
    ]
    codes = children_2
    for name, code in zip(names, codes):
        categories[code] = {
            "title": name,
            "comment": name,
            "info": {"gases": ["CH4", "N2O", "CO2"]},
        }

    # 3 livestock
    animals = [
        "Asses",
        "Camels",
        "Cattle, dairy",
        "Cattle, non-dairy",
        "Chickens, broilers",
        "Chickens, layers",
        "Goats",
        "Horses",
        "Mules and hinnies",
        "Sheep",
        "Llamas",
        "Chickens",
        "Poultry Birds",
        "Buffalo",
        "Ducks",
        "Swine, breeding",
        "Swine, market",
        "Turkeys",
    ]

    codes_animals = [f"3.{i}" for i in "ABCDEFGHIJKLMNOPQR"]

    enteric_fermentation = [
        "Asses",
        "Camels",
        "Cattle, dairy",
        "Cattle, non-dairy",
        "Goats",
        "Horses",
        "Sheep",
        "Mules and hinnies",
        "Buffalo",
        "Swine, breeding",
        "Swine, market",
        "Llamas",
    ]

    for animal, code in zip(animals, codes_animals):
        if animal in enteric_fermentation:
            animal_children = [f"{code}.{i}" for i in "1234"]
            categories[f"{code}.4"] = {
                "title": f"{animal} enteric fermentation",
                "comment": f"{animal} enteric fermentation",
                "info": {"gases": "CH4"},
            }
        else:
            animal_children = [f"{code}.{i}" for i in "123"]

        categories[code] = {
            "title": animal,
            "comment": animal,
            "info": {"gases": ["N2O", "CH4"]},
            "children": [animal_children],
        }

        # manure management branch
        manure_management_children = [f"{code}.1.{i}" for i in "abc"]
        categories[f"{code}.1"] = {
            "title": f"{animal} manure management",
            "comment": f"{animal} manure management",
            "info": {"gases": ["N2O", "CH4"]},
            "children": [manure_management_children],
        }

        categories[f"{code}.1.a"] = {
            "title": f"{animal} decomposition of organic matter",
            "comment": f"{animal} decomposition of organic matter",
            "info": {"gases": "CH4"},
        }

        categories[f"{code}.1.b"] = {
            "title": f"{animal} manure management (Direct emissions N2O)",
            "comment": f"{animal} manure management (Direct emissions N2O)",
            "info": {"gases": "N2O"},
        }

        categories[f"{code}.1.c"] = {
            "title": f"{animal} manure management (Indirect emissions N2O)",
            "comment": f"{animal} manure management (Indirect emissions N2O)",
            "info": {"gases": "N2O"},
        }

        # manure left on pasture branch
        manure_left_on_pasture_children = [f"{code}.2.{i}" for i in "ab"]
        categories[f"{code}.2"] = {
            "title": f"{animal} manure left on pasture",
            "comment": f"{animal} manure left on pasture",
            "info": {"gases": "N2O"},
            "children": [manure_left_on_pasture_children],
        }

        categories[f"{code}.2.a"] = {
            "title": f"{animal} manure left on pasture (direct emissions N2O)",
            "comment": f"{animal} manure left on pasture (direct emissions N2O)",
            "info": {"gases": "N2O"},
        }

        categories[f"{code}.2.b"] = {
            "title": f"{animal} manure left on pasture (indirect emissions N2O)",
            "comment": f"{animal} manure left on pasture (indirect emissions N2O)",
            "info": {"gases": "N2O"},
            "children": [[f"{code}.2.b.i", f"{code}.2.b.ii"]],
        }

        categories[f"{code}.2.b.i"] = {
            "title": (
                f"{animal} manure left on pasture "
                f"(indirect emissions, N2O that leaches)"
            ),
            "comment": (
                f"{animal} manure left on pasture (indirect "
                f"emissions, N2O that leaches)"
            ),
            "info": {"gases": "N2O"},
        }

        categories[f"{code}.2.b.ii"] = {
            "title": (
                f"{animal} manure left on pasture "
                f"(indirect emissions, N2O that volatilises)"
            ),
            "comment": (
                f"{animal} manure left on pasture (indirect "
                f"emissions, N2O that volatilises)"
            ),
            "info": {"gases": "N2O"},
        }

        # manure applied branch
        manure_applied_children = [f"{code}.3.{i}" for i in "ab"]
        categories[f"{code}.3"] = {
            "title": f"{animal} manure applied",
            "comment": f"{animal} manure applied",
            "info": {"gases": "N2O"},
            "children": [manure_applied_children],
        }

        categories[f"{code}.3.a"] = {
            "title": f"{animal} manure applied (direct emissions N2O)",
            "comment": f"{animal} manure applied (direct emissions N2O)",
            "info": {"gases": "N2O"},
        }

        categories[f"{code}.3.b"] = {
            "title": f"{animal} manure applied (indirect emissions N2O)",
            "comment": f"{animal} manure applied (indirect emissions N2O)",
            "info": {"gases": "N2O"},
            "children": [[f"{code}.3.b.i", f"{code}.3.b.ii"]],
        }

        categories[f"{code}.3.b.i"] = {
            "title": (
                f"{animal} manure applied (indirect emissions, N2O that leaches)"
            ),
            "comment": (
                f"{animal} manure applied (indirect emissions, N2O that leaches)"
            ),
            "info": {"gases": "N2O"},
        }

        categories[f"{code}.3.b.ii"] = {
            "title": (
                f"{animal} manure applied (indirect emissions, N2O that volatilises)"
            ),
            "comment": (
                f"{animal} manure applied (indirect emissions, N2O that volatilises)"
            ),
            "info": {"gases": "N2O"},
        }

    # forests
    categories["4"] = {
        "title": "Carbon stock change in forests",
        "comment": "Carbon stock change in forests",
        "info": {"gases": "CO2"},
        "children": [["4.A", "4.B"]],
    }

    categories["4.A"] = {
        "title": "Forest land",
        "comment": "Forest land",
        "info": {"gases": "CO2"},
    }

    categories["4.B"] = {
        "title": "Net Forest conversion",
        "comment": "Net Forest conversion",
        "info": {"gases": "CO2"},
    }

    # 5 drained organic soils
    categories["5"] = {
        "title": "Drained organic soils",
        "comment": "Drained organic soils",
        "info": {"gases": ["CO2", "N2O"]},
        "children": [["5.A", "5.B"]],
    }

    categories["5.A"] = {
        "title": "Drained grassland",
        "comment": "Drained grassland",
        "info": {"gases": ["CO2", "N2O"]},
    }

    categories["5.B"] = {
        "title": "Drained cropland",
        "comment": "Drained cropland",
        "info": {"gases": ["CO2", "N2O"]},
    }

    # 6 Fires
    # Forest fires
    forest_fires_children = ["Humid tropical forests", "Other forests"]
    forest_fires_children_codes = ["6.A.1", "6.A.2"]
    for cat_name, code in zip(forest_fires_children, forest_fires_children_codes):
        categories[code] = {
            "title": cat_name,
            "comment": cat_name,
            "info": {"gases": ["CO2", "N2O", "CH4"]},
        }
    categories["6.A"] = {
        "title": "Forest fires",
        "comment": "Forest fires",
        "info": {"gases": ["CO2", "N2O", "CH4"]},
        "children": [forest_fires_children_codes],
    }

    # Savanna fires
    savanna_fires_children = [
        "Closed shrubland",
        "Grassland",
        "Open shrubland",
        "Savanna",
        "Woody savanna",
    ]
    savanna_fires_children_codes = ["6.B.1", "6.B.2", "6.B.3", "6.B.4", "6.B.5"]
    for cat_name, code in zip(savanna_fires_children, savanna_fires_children_codes):
        categories[code] = {
            "title": cat_name,
            "comment": cat_name,
            "info": {"gases": ["CO2", "N2O", "CH4"]},
        }
    categories["6.B"] = {
        "title": "Savanna fires",
        "comment": "Savanna fires",
        "info": {"gases": ["CO2", "N2O", "CH4"]},
        "children": [savanna_fires_children_codes],
    }

    # fires in organic soils
    categories["6.C"] = {
        "title": "Fires in organic soils",
        "comment": "Fires in organic soils",
        "info": {"gases": ["CO2", "N2O", "CH4"]},
    }

    # 6 fires
    categories["6"] = {
        "title": "Fires",
        "comment": "Fires",
        "info": {"gases": ["CO2", "N2O", "CH4"]},
        "children": [["6.A", "6.B", "6.C"]],
    }

    # 7 pre and post production
    pre_post_production_categories = [
        "Fertilizers Manufacturing",
        "Food Transport",
        "Food Retail",
        "Food Household Consumption",
        "Solid Food Waste",
        "Domestic Wastewater",
        "Industrial Wastewater",
        "Incineration",
        "Pre- and Post- Production",
        "Energy Use (Pre- and Post-Production)",
        "Agrifood Systems Waste Disposal",
        "Cold Chain F-Gas",
        "Pesticides Manufacturing",
        "Food Processing",
        "Food Packaging",
    ]
    pre_post_production_categories_codes = ["7." + i for i in "ABCDEFGHIJKLMNO"]
    pre_post_production_categories_gases = [
        ["CO2", "N2O", "KYOTOGHG (AR5GWP100)"],
        ["CO2", "CH4", "N2O", "KYOTOGHG (AR5GWP100)", "FGASES (AR5GWP100)"],
        ["CO2", "CH4", "N2O", "KYOTOGHG (AR5GWP100)", "FGASES (AR5GWP100)"],
        ["CO2", "CH4", "N2O", "KYOTOGHG (AR5GWP100)", "FGASES (AR5GWP100)"],
        ["KYOTOGHG (AR5GWP100)", "CH4"],
        ["KYOTOGHG (AR5GWP100)", "CH4", "N2O"],
        ["KYOTOGHG (AR5GWP100)", "CH4", "N2O"],
        ["CO2", "KYOTOGHG (AR5GWP100)"],  # incineration
        ["CO2", "CH4", "N2O", "KYOTOGHG (AR5GWP100)", "FGASES (AR5GWP100)"],
        ["CO2", "CH4", "N2O", "KYOTOGHG (AR5GWP100)"],
        ["CO2", "CH4", "N2O", "KYOTOGHG (AR5GWP100)"],
        ["FGASES (AR5GWP100)"],
        ["CO2", "CH4", "N2O", "KYOTOGHG (AR5GWP100)"],
        ["CO2", "CH4", "N2O", "KYOTOGHG (AR5GWP100)", "FGASES (AR5GWP100)"],
        ["CO2", "CH4", "N2O", "KYOTOGHG (AR5GWP100)"],
    ]
    for cat_name, code, gases in zip(
        pre_post_production_categories,
        pre_post_production_categories_codes,
        pre_post_production_categories_gases,
    ):
        categories[code] = {
            "title": cat_name,
            "comment": cat_name,
            "info": {"gases": gases},
        }
    categories["7"] = {
        "title": "Pre and post agricultural production",
        "comment": "Pre and post agricultural production",
        "info": {
            "gases": [
                "CO2",
                "CH4",
                "N2O",
                "KYOTOGHG (AR5GWP100)",
                "FGASES (AR5GWP100)",
            ],
        },
        "children": [pre_post_production_categories_codes],
    }

    # M categories
    categories["M.3.EF"] = {
        "title": "All animals enteric fermentation",
        "comment": "The sum of enteric fermentation emissions of all animals",
        "info": {
            "gases": [
                "CH4",
            ],
        },
    }

    categories["M.3.MM"] = {
        "title": "All Animals - Manure management",
        "comment": "The sum of manure management emissions of all animals",
        "info": {
            "gases": [
                "N2O",
                "CH4",
            ],
        },
    }

    categories["M.3.MP"] = {
        "title": "All Animals - Manure left on pasture",
        "comment": "The sum of manure left on pasture emissions of all animals",
        "info": {
            "gases": [
                "N2O",
            ],
        },
        "children": [["M.3.MP.direct", "M.3.MP.indirect"]],
    }

    categories["M.3.MP.direct"] = {
        "title": "All Animals - Manure left on pasture (Direct emissions N2O)",
        "comment": "The sum of manure left on pasture emissions of all animals - only direct emissions",
        "info": {
            "gases": [
                "N2O",
            ],
        },
    }

    categories["M.3.MP.indirect"] = {
        "title": "All Animals - Manure left on pasture (Indirect emissions N2O)",
        "comment": "The sum of manure left on pasture emissions of all animals - only indirect emissions",
        "info": {
            "gases": [
                "N2O",
            ],
        },
    }

    categories["M.1.CR"] = {
        "title": "All crops - crop residues",
        "info": {
            "gases": [
                "N2O",
            ],
        },
        "children": [["M.1.CR.direct", "M.1.CR.indirect"]],
    }

    categories["M.1.CR.direct"] = {
        "title": "All Crops - Crop residues (Direct emissions N2O)",
        "info": {
            "gases": [
                "N2O",
            ],
        },
    }

    categories["M.1.CR.indirect"] = {
        "title": "All Crops - Crop residues (Indirect emissions N2O)",
        "info": {
            "gases": [
                "N2O",
            ],
        },
    }

    categories["M.1.BCR"] = {
        "title": "All crops - burning crop residues",
        "info": {
            "gases": ["N2O", "CH4"],
        },
    }

    categories["M.3.MA"] = {
        "title": "All Animals - Manure applied",
        "comment": "The sum of manure applied to soils emissions of all animals",
        "info": {
            "gases": [
                "N2O",
            ],
        },
        "children": [["M.3.MA.direct", "M.3.MA.indirect"]],
    }

    categories["M.3.MA.direct"] = {
        "title": "All Animals - Manure applied to soils (Direct emissions N2O)",
        "comment": "The sum of manure applied to soils emissions of all animals - only direct emissions",
        "info": {
            "gases": [
                "N2O",
            ],
        },
    }

    categories["M.3.MA.indirect"] = {
        "title": "All Animals - Manure applied to soils (Indirect emissions N2O)",
        "comment": "The sum of manure applied to soils emissions of all animals - only indirect emissions",
        "info": {
            "gases": [
                "N2O",
            ],
        },
    }

    categories["M.5.CO2"] = {
        "title": "CO2 emissions from drained organic soils",
        "comment": "The split by gas is needed to build M.AG and M.LULUCF",
        "info": {
            "gases": [
                "CO2",
            ],
        },
    }

    categories["M.5.N2O"] = {
        "title": "N2O emissions from drained organic soils",
        "comment": "The split by gas is needed to build M.AG and M.LULUCF",
        "info": {
            "gases": [
                "N2O",
            ],
        },
    }

    categories["M.AG"] = {
        "title": "Agriculture",
        "comment": "Agricultural part of AFOLU as defined in FAOSTAT data explorer",
        "children": [
            [
                "M.5.N2O",  # N2O drained organic soils
                "1.B",  # synthetic fertilisers
                "M.3.MA",  # manure applied to soils
                "M.3.MP",  # manure left on pasture
                "M.1.CR",  # crop residues
                "M.1.BCR",  # burning crop residues
                "M.3.EF",  # enteric fermentation
                "6.B",  # savanna fires
                "1.A.2.c",  # rice cultivation
            ]
        ],
    }

    categories["M.LULUCF"] = {
        "title": "Land Use, Land Use Change, and Forestry",
        "comment": "LULUCF part of AFOLU as defined in FAOSTAT data explorer",
        "children": [
            [
                "M.5.CO2",  # CO2 drained organic soils
                "4.A",  # forest land
                "4.B",  # net forest conversion
                "6.A",  # fires in organic soils
                "6.C",  # forest fires
            ]
        ],
    }

    spec["categories"] = categories
    fao_cats = cc.HierarchicalCategorization.from_spec(spec.copy())

    fao_cats.to_yaml(OUTPATH)
    cc.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
