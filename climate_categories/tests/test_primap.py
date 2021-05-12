import pytest

import climate_categories


def test_number_of_categories():
    assert len(climate_categories.IPCC2006_PRIMAP) == 289 + 14


@pytest.mark.xfail  # no top-level category for IPCC
def test_levels():
    assert climate_categories.IPCC2006_PRIMAP.level("1") == 1
    assert climate_categories.IPCC2006_PRIMAP.level("0") == 0
    assert climate_categories.IPCC2006_PRIMAP.level("M.AG") == 0
    assert climate_categories.IPCC2006_PRIMAP.level("3.A.1.") == 4


def test_consistent():
    for cat in climate_categories.IPCC2006_PRIMAP.values():
        if "corresponding_categories_IPCC1996" in cat.info:
            for ccat in cat.info["corresponding_categories_IPCC1996"]:
                assert ccat in climate_categories.IPCC1996
