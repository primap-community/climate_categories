import climate_categories


def test_number_of_categories():
    assert len(climate_categories.CRF1999) == 400
    assert len(climate_categories.CRF2013) == 729
    assert len(climate_categories.CRF2013_2021) == 960
    assert len(climate_categories.CRF2013_2022) == 966
    assert len(climate_categories.CRF2013_2023) == 967


def test_levels():
    assert climate_categories.CRF1999.level("1") == 2
    assert climate_categories.CRF1999.level("1.A") == 3
    assert climate_categories.CRF2013.level("1") == 2
    assert climate_categories.CRF2013.level("1.A") == 3
    assert climate_categories.CRF2013_2021.level("1") == 2
    assert climate_categories.CRF2013_2021.level("1.A") == 3
    assert climate_categories.CRF2013_2021.level("5.B.2.b.iii") == 6
    assert climate_categories.CRF2013_2022.level("1") == 2
    assert climate_categories.CRF2013_2022.level("1.A") == 3
    assert climate_categories.CRF2013_2022.level("5.B.2.b.iii") == 6
    assert climate_categories.CRF2013_2023.level("1") == 2
    assert climate_categories.CRF2013_2023.level("1.A") == 3
    assert climate_categories.CRF2013_2023.level("5.B.2.b.iii") == 6


# TODO: add conversion tests once conversion to IPCC cats is defined
