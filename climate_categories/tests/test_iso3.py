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


@pytest.mark.parametrize("code", ["UMBRELLA", "LDC", "G35", "LMDC"])
def test_country_groups_included(code: str):
    assert code in climate_categories.ISO3


def test_gcam():
    assert (
        len(climate_categories.ISO3_GCAM["GCAM 7.0|Southeast Asia"].leaf_children[0])
        == 37
    )

    assert climate_categories.ISO3.version == climate_categories.ISO3_GCAM.version


@pytest.mark.parametrize("version", ["4.0", "5.1", "6.0", "7.4", "8.0", "9.1"])
def test_gcam_versions(version: str):
    assert len(climate_categories.ISO3_GCAM[f"GCAM {version}|USA"].children[0]) >= 1


def test_gcam_identical_versions_share_categories():
    # GCAM versions with identical region definitions are one category with the other
    # versions as alternative codes, so that they compare equal
    gcam = climate_categories.ISO3_GCAM
    assert gcam["GCAM 9.1|Ukraine"] == gcam["GCAM 8.1|Ukraine"]
    assert gcam["GCAM 8.0|Europe_Eastern"] == gcam["GCAM 7.4|Europe_Eastern"]
    assert gcam["GCAM 8.1|Europe_Non_EU"] != gcam["GCAM 8.0|Europe_Non_EU"]


def test_gcam_8s():
    # runs labelled "GCAM 8s", like the CMIP7 runs, use the GCAM 8.0 regions
    gcam = climate_categories.ISO3_GCAM
    assert gcam["GCAM 8s|Europe_Eastern"] == gcam["GCAM 8.0|Europe_Eastern"]
    assert gcam["GCAM 8s|USA"] != gcam["GCAM 8.1|USA"]


def test_gcam_region_aliases():
    # both spellings which are in use for these regions work
    gcam = climate_categories.ISO3_GCAM
    assert gcam["GCAM 9.1|Australia and New Zealand"] == gcam["GCAM 9.1|Australia_NZ"]
    assert gcam["GCAM 3.0|Australia and New Zealand"] == gcam["GCAM 3.0|Australia_NZ"]
    assert (
        gcam["GCAM 5.1|Central America and the Caribbean"]
        == gcam["GCAM 5.1|Central America and Caribbean"]
    )


def test_gcam3():
    # the 14 regions of GCAM 3, inherited by all later versions as a mapping
    assert len(climate_categories.ISO3_GCAM["GCAM 3.0|Africa"].children[0]) > 40
    assert climate_categories.ISO3_GCAM["GCAM 3.0|Korea"].children[0] == {
        climate_categories.ISO3_GCAM["KOR"]
    }


def test_gcam_kosovo():
    # not an ISO 3166-1 country, but GCAM 7.4 and later use it
    assert "XKX" not in climate_categories.ISO3
    assert climate_categories.ISO3_GCAM["XKX"].title == "Kosovo"
    assert (
        climate_categories.ISO3_GCAM["XKX"]
        in climate_categories.ISO3_GCAM["GCAM 9.1|Europe_Non_EU"].children[0]
    )
