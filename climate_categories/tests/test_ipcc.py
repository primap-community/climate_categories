import climate_categories


def test_number_of_categories():
    assert len(climate_categories.IPCC1996) == 233
    assert len(climate_categories.IPCC2006) == 290


def test_levels():
    assert climate_categories.IPCC1996.level("1") == 2
    assert climate_categories.IPCC1996.level("1A") == 3
    assert climate_categories.IPCC2006.level("1") == 2
    assert climate_categories.IPCC2006.level("1A") == 3


def test_consistent():
    for cat in climate_categories.IPCC2006.values():
        if "corresponding_categories_IPCC1996" in cat.info:
            for ccat in cat.info["corresponding_categories_IPCC1996"]:
                assert ccat in climate_categories.IPCC1996


def test_conversion():
    conv = climate_categories.IPCC1996.conversion_to(climate_categories.IPCC2006)

    problems = conv.find_over_counting_problems()
    problematic_categories = list(
        sorted([problem.category.codes[0] for problem in problems])
    )
    assert problematic_categories == [
        "2.B.7",
        "2.B.9",
        "2.B.9.a",
        "2.B.9.b",
        "6.A.1",
        "6.A.2",
        "6.A.3",
        "6.B.3",
    ]

    # still a lot of unmapped categories )-:
    missing96, missing06 = conv.find_unmapped_categories()
    assert len(missing96) == 71
    assert len(missing06) == 110
