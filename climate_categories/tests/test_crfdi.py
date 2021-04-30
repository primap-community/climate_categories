import climate_categories


def test_levels():
    assert climate_categories.CRFDI.level("1") == 2
    assert climate_categories.CRFDI.level("1.A") == 3


def test_lulucf():
    assert climate_categories.CRFDI["4"] in climate_categories.CRFDI["8677"].children[0]
    assert (
        climate_categories.CRFDI["4"]
        not in climate_categories.CRFDI["10464"].children[0]
    )
