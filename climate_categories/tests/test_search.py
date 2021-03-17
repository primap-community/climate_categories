import climate_categories


def test_search():
    assert climate_categories.find_code("1A") == {
        climate_categories.IPCC1996["1.A"],
        climate_categories.IPCC2006["1.A"],
    }
