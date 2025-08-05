import pytest

import climate_categories


def test_levels():
    assert climate_categories.FAO.level("0") == 1
    assert climate_categories.FAO.level("1") == 2
    assert climate_categories.FAO.level("1.A") == 3
    assert climate_categories.FAO.level("1.A.2") == 4
    assert climate_categories.FAO.level("1.A.2.a") == 5
    assert climate_categories.FAO.level("1.A.2.a.i") == 6


def test_number_of_categories():
    assert len(climate_categories.FAO) == 399


@pytest.mark.parametrize(
    "code",
    ["M.1.CR", "M.5.CO2", "M.5.N2O", "M.AG", "M.LULUCF"],
)
def test_custom_categories(code: str):
    assert code in climate_categories.FAO
