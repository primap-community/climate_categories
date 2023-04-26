import climate_categories


def test_search():
    assert climate_categories.find_code("1A") == {
        climate_categories.IPCC1996["1.A"],
        climate_categories.IPCC2006["1.A"],
        climate_categories.IPCC2006_PRIMAP["1.A"],
        climate_categories.CRF1999["1.A"],
        climate_categories.CRF2013["1.A"],
        climate_categories.CRF2013_2021["1.A"],
        climate_categories.CRF2013_2022["1.A"],
        climate_categories.CRF2013_2023["1.A"],
        climate_categories.CRFDI["1.A"],
        climate_categories.CRFDI_class["1.A"],
        climate_categories.BURDI["1.A"],
        climate_categories.BURDI_class["1.A"],
    }
