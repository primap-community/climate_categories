import climate_categories


def test_levels():
    assert climate_categories.CT.level("all-emissions") == 1
    assert climate_categories.CT.level("agriculture") == 2
    assert climate_categories.CT.level("mineral-extraction|bauxite-mining") == 3


def test_number_of_categories():
    assert len(climate_categories.CT) == 78
