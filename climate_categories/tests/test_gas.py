"""Tests for the 'gas' categorization."""

import climate_categories


def test_categories():
    assert climate_categories.gas["CO2"].title == "carbon dioxide"
    assert (
        climate_categories.gas["HCFC414a"].comment
        == "The refrigerant HCFC414a, which is a mixture of 51% HCFC22, 28.5% HCFC124,"
        " 4% HC600a, 16.5% HCFC142b."
    )


def test_mixture_hierarchy():
    assert (
        climate_categories.gas["HFC417a"]
        in climate_categories.gas["mixtures"].children[0]
    )
