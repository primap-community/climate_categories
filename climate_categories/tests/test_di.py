import climate_categories


def test_levels_crf():
    assert climate_categories.CRFDI.level("1") == 2
    assert climate_categories.CRFDI.level("1.A") == 3


def test_lulucf_crf():
    assert climate_categories.CRFDI["4"] in climate_categories.CRFDI["8677"].children[0]
    assert (
        climate_categories.CRFDI["4"]
        not in climate_categories.CRFDI["10464"].children[0]
    )


def test_levels_bur():
    assert climate_categories.BURDI.level("1") == 2
    assert climate_categories.BURDI.level("1.A") == 3


def test_lulucf_bur():
    assert (
        climate_categories.BURDI["5"] in climate_categories.BURDI["24540"].children[0]
    )
    assert (
        climate_categories.BURDI["5"]
        not in climate_categories.BURDI["15163"].children[0]
    )
