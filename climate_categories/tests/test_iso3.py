"""Tests for the 'ISO3' categorization."""

import pytest

import climate_categories


def test_categories():
    assert climate_categories.ISO3["DEU"].title == "Germany"
    assert len(climate_categories.ISO3) > 150


def test_eu():
    assert len(climate_categories.ISO3["EU-12"].children[0]) == 12
    assert len(climate_categories.ISO3["EU-15"].children[0]) == 15
    assert len(climate_categories.ISO3["EU-25"].children[0]) == 25
    assert len(climate_categories.ISO3["EU-27_2007"].children[0]) == 27
    assert len(climate_categories.ISO3["EU-28"].children[0]) == 28
    assert len(climate_categories.ISO3["EU-27_2020"].children[0]) == 27
    with pytest.raises(KeyError):
        climate_categories.ISO3["EU27"]

    assert climate_categories.ISO3["EU"] == climate_categories.ISO3["EU_2020"]


def test_unfccc():
    assert len(climate_categories.ISO3["Annex-I"].children[0]) == 43
    assert len(climate_categories.ISO3["Non-Annex-I"].children[0]) == 155
    # leaf children excludes EU, because EU is not a leaf
    assert len(climate_categories.ISO3["UNFCCC"].leaf_children[0]) == 197
    assert len(climate_categories.ISO3["UNFCCC"].children[0]) == 198
    assert (
        climate_categories.ISO3["EU"] in climate_categories.ISO3["UNFCCC"].children[0]
    )
    assert climate_categories.ISO3["Annex-I"] in climate_categories.ISO3.descendants(
        "UNFCCC"
    )
    assert climate_categories.ISO3[
        "Non-Annex-I"
    ] in climate_categories.ISO3.descendants("UNFCCC")


def test_g7g20():
    # since the EU is a non-enumerated member, G7 has 8 members, G8 has 9.
    assert len(climate_categories.ISO3["G7"].children[0]) == 8
    assert len(climate_categories.ISO3["G8"].children[0]) == 9
    # in the G20, the EU is enumerated
    assert len(climate_categories.ISO3["G20"].children[0]) == 20


def test_oecd():
    assert len(climate_categories.ISO3["OECD"].leaf_children[0]) == 38


def test_aosis():
    assert len(climate_categories.ISO3["AOSIS"].leaf_children[0]) == 39


def test_gcam():
    assert (
        len(climate_categories.ISO3_GCAM["GCAM 7.0|Southeast Asia"].leaf_children[0])
        == 37
    )
