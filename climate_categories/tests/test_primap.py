import climate_categories


def test_number_of_categories():
    assert (
        len(climate_categories.IPCC2006_PRIMAP) == len(climate_categories.IPCC2006) + 13
    )


def test_levels():
    assert climate_categories.IPCC2006_PRIMAP.level("1") == 2
    assert climate_categories.IPCC2006_PRIMAP.level("1.A.1.bc") == 5


def test_consistent():
    for cat in climate_categories.IPCC2006_PRIMAP.values():
        if "corresponding_categories_IPCC1996" in cat.info:
            for ccat in cat.info["corresponding_categories_IPCC1996"]:
                assert ccat in climate_categories.IPCC1996
