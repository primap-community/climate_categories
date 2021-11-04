import climate_categories


def test_number_of_categories():
    assert len(climate_categories.RCMIP) == 87  # 86 from Excel sheet + top level


def test_levels():
    assert climate_categories.RCMIP.level("Emissions") == 1
    assert climate_categories.RCMIP.level("Emissions|F-Gases|HFC|HFC236fa") == 4
