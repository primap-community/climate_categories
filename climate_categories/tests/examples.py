import climate_categories


def HierEx():
    spec = {
        "name": "HierEx",
        "title": "Hierarchical Example Categorization",
        "comment": "A simple hierarchical categorization",
        "references": "mailto:mika.pflueger@pik-potsdam.de",
        "institution": "PIK",
        "last_update": "2021-10-12",
        "hierarchical": True,
        "version": "1",
        "total_sum": "True",
        "canonical_top_level_category": "0",
        "categories": {
            "0": {"title": "Total", "children": [["1", "2", "3"]]},
            "1": {"title": "Sector 1"},
            "2": {"title": "Sector 2"},
            "3": {"title": "Sector 3"},
        },
    }
    return climate_categories.HierarchicalCategorization.from_spec(spec)


def HierAltEx():
    spec = {
        "name": "HierAltEx",
        "title": "Hierarchical Example Categorization with Alternatives",
        "comment": "A simple hierarchical categorization with alternative child sets",
        "references": "mailto:mika.pflueger@pik-potsdam.de",
        "institution": "PIK",
        "last_update": "2021-10-12",
        "hierarchical": True,
        "version": "1",
        "total_sum": "True",
        "canonical_top_level_category": "0",
        "categories": {
            "0": {"title": "Total", "children": [["1", "2", "3"], ["a", "b", "c"]]},
            "1": {"title": "Sector 1"},
            "2": {"title": "Sector 2"},
            "3": {"title": "Sector 3"},
            "a": {"title": "Fuel a"},
            "b": {"title": "Fuel b"},
            "c": {"title": "Fuel c"},
        },
    }
    return climate_categories.HierarchicalCategorization.from_spec(spec)
