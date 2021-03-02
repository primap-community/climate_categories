import pathlib

import pytest

import climate_categories


@pytest.fixture
def SimpleCat():
    return climate_categories.Categorization.from_yaml(
        pathlib.Path(__file__).parent / "data" / "simple_categorization.yaml"
    )


@pytest.fixture
def HierCat():
    return climate_categories.HierarchicalCategorization.from_yaml(
        pathlib.Path(__file__).parent / "data" / "hierarchical_categorization.yaml"
    )
