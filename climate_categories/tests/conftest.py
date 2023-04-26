import importlib
import importlib.resources

import pytest

import climate_categories
import climate_categories.tests
import climate_categories.tests.data


def read_cat(fragment):
    return climate_categories.from_yaml(
        importlib.resources.files("climate_categories.tests.data")
        .joinpath(f"{fragment}_categorization.yaml")
        .open("r")
    )


@pytest.fixture
def SimpleCat():
    return read_cat("simple")


@pytest.fixture
def HierCat():
    return read_cat("hierarchical")


@pytest.fixture(params=["hierarchical", "simple"])
def any_cat(request):
    """Test with all available valid example Categorizations."""
    return read_cat(request.param)


@pytest.fixture
def spec_simple():
    return {
        "name": "SimpleCat",
        "title": "Simple Categorization",
        "comment": "A simple example categorization without relationships between"
        " categories",
        "references": "doi:00000/00000",
        "institution": "PIK",
        "hierarchical": False,
        "last_update": "2021-02-23",
        "version": "1",
        "categories": {
            "1": {
                "title": "Category 1",
                "comment": "The first category",
                "alternative_codes": ["A", "CatA"],
                "info": {
                    "important_data": ["A", "B", "C"],
                    "other_important_thing": "ABC",
                },
            },
            "2": {
                "title": "Category 2",
                "comment": "The second category",
                "alternative_codes": ["B", "CatB"],
            },
            "3": {
                "title": "Category 3",
                "comment": "The third category",
                "alternative_codes": ["C", "CatC"],
            },
            "unnumbered": {"title": "The unnumbered category"},
        },
    }


@pytest.fixture
def spec_hier():
    return {
        "name": "HierCat",
        "title": "Hierarchical Categorization",
        "comment": "A simple hierarchical categorization with categories with"
        " relationships",
        "references": "doi:00000/00000",
        "institution": "PIK",
        "hierarchical": True,
        "last_update": "2021-02-23",
        "version": "one",
        "total_sum": False,
        "canonical_top_level_category": "0",
        "categories": {
            "0": {
                "title": "Category 0",
                "comment": "Top-most category",
                "alternative_codes": ["TOTAL"],
                "children": [["1", "2", "3"], ["0X3", "3"], ["1A", "1B", "2", "3"]],
            },
            "1": {
                "title": "Category 1",
                "comment": "The first category",
                "info": {"SomeInfo": "A", "OtherInfo": ["A", "B", "C"]},
                "children": [["1A", "1B"]],
            },
            "2": {
                "title": "Category 2",
                "comment": "The second category",
                "children": [["2A", "2B"]],
            },
            "3": {
                "title": "Category 3",
                "comment": "The third category",
                "children": [["3A"]],
            },
            "1A": {"title": "Category 1A", "alternative_codes": ["1a"]},
            "1B": {"title": "Category 1B", "alternative_codes": ["1b"]},
            "2A": {"title": "Category 2A", "alternative_codes": ["2a"]},
            "2B": {"title": "Category 2B", "alternative_codes": ["2b"]},
            "3A": {"title": "Category 3A", "alternative_codes": ["3a"]},
            "0X3": {
                "title": "Total excluding category 3",
                "alternative_codes": ["0E3"],
                "children": [["1", "2"]],
            },
            "OT": {"title": "Other top category", "children": [["1B", "2B"]]},
        },
    }
