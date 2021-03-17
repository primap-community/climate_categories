import pytest

import climate_categories


def test_number_of_categories():
    assert len(climate_categories.IPCC1996) == 232
    assert len(climate_categories.IPCC2006) == 289


@pytest.mark.xfail  # no top-level category for IPCC
def test_levels():
    assert climate_categories.IPCC2006.level("1") == 1
    assert climate_categories.IPCC2006.level("1A") == 2


def test_consistent():
    for cat in climate_categories.IPCC2006.values():
        if "corresponding_categories_IPCC1996" in cat.info:
            for ccat in cat.info["corresponding_categories_IPCC1996"]:
                assert ccat in climate_categories.IPCC1996
