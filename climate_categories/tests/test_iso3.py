"""Tests for the 'ISO3' categorization."""

import re

import pytest

import climate_categories

ISO3_EU = climate_categories.cats["ISO3[eu]"]
ISO3_UNFCCC = climate_categories.cats["ISO3[eu,unfccc]"]
ISO3_GROUPS = climate_categories.cats["ISO3[eu,groups]"]


def test_categories():
    assert climate_categories.ISO3["DEU"].title == "Germany"
    assert len(climate_categories.ISO3) > 150


def test_eu():
    assert len(ISO3_EU["EU-12"].children[0]) == 12
    assert len(ISO3_EU["EU-15"].children[0]) == 15
    assert len(ISO3_EU["EU-25"].children[0]) == 25
    assert len(ISO3_EU["EU-27_2007"].children[0]) == 27
    assert len(ISO3_EU["EU-28"].children[0]) == 28
    assert len(ISO3_EU["EU-27_2020"].children[0]) == 27
    with pytest.raises(KeyError):
        ISO3_EU["EU27"]

    assert ISO3_EU["EU"] == ISO3_EU["EU_2020"]


def test_unfccc():
    assert len(ISO3_UNFCCC["Annex-I"].children[0]) == 43
    assert len(ISO3_UNFCCC["Non-Annex-I"].children[0]) == 155
    # leaf children excludes EU, because EU is not a leaf
    assert len(ISO3_UNFCCC["UNFCCC"].leaf_children[0]) == 197
    assert len(ISO3_UNFCCC["UNFCCC"].children[0]) == 198
    assert ISO3_UNFCCC["EU"] in ISO3_UNFCCC["UNFCCC"].children[0]
    assert ISO3_UNFCCC["Annex-I"] in ISO3_UNFCCC.descendants("UNFCCC")
    assert ISO3_UNFCCC["Non-Annex-I"] in ISO3_UNFCCC.descendants("UNFCCC")


@pytest.mark.parametrize(
    ("code", "n_parties"),
    [
        ("UNFCCC_1994_03", 52),
        ("UNFCCC_1994", 93),
        ("UNFCCC_2000", 185),
        ("UNFCCC_2022", 198),
    ],
)
def test_unfccc_versions_size(code: str, n_parties: int):
    assert len(ISO3_UNFCCC[code].children[0]) == n_parties


def test_unfccc_versions():
    iso3 = ISO3_UNFCCC

    def parties(code: str) -> set[str]:
        return {party.codes[0] for party in iso3[code].children[0]}

    # one category per month with changes, the last one per year has the year as code
    monthly = [code for code in iso3 if re.fullmatch(r"UNFCCC_\d{4}_\d{2}", code)]
    assert len(monthly) == 60
    assert iso3["UNFCCC_2007"] == iso3["UNFCCC_2007_11"]
    assert "UNFCCC_2005" not in iso3
    assert "UNFCCC_2022_09" not in iso3

    assert "TLS" in parties("UNFCCC_2007_01")
    assert "BRN" not in parties("UNFCCC_2007_01")
    assert "BRN" in parties("UNFCCC_2007")

    assert "USA" in parties("UNFCCC_2022")

    assert "SSD" not in parties("UNFCCC_2011")
    assert "SSD" in parties("UNFCCC_2014")

    assert "SRB" in parties("UNFCCC_2001")
    assert "MNE" not in parties("UNFCCC_2004")
    assert "MNE" in parties("UNFCCC_2006")

    assert set(iso3["UNFCCC_2022"].children[0]) == set(iso3["UNFCCC"].children[0])


@pytest.mark.parametrize(
    ("code", "n_parties"),
    [
        ("PARIS_2016_11", 89),
        ("PARIS_2016", 115),
        ("PARIS_2020", 189),
        ("PARIS_2021", 193),
        ("PARIS_2026_01", 194),
        ("PARIS", 194),
    ],
)
def test_paris_versions_size(code: str, n_parties: int):
    assert len(ISO3_UNFCCC[code].children[0]) == n_parties


def test_paris_versions():
    iso3 = ISO3_UNFCCC

    def parties(code: str) -> set[str]:
        return {party.codes[0] for party in iso3[code].children[0]}

    # one category per month with changes, the last one per year has the year as code
    monthly = [code for code in iso3 if re.fullmatch(r"PARIS_\d{4}_\d{2}", code)]
    assert len(monthly) == 38
    assert iso3["PARIS_2021"] == iso3["PARIS_2021_12"]
    assert "PARIS_2024" not in iso3
    assert "PARIS_2018_04" not in iso3

    # the USA joined, left, joined again, and left again
    assert "USA" in parties("PARIS_2016_11")
    assert "USA" not in parties("PARIS_2020_11")
    assert "USA" in parties("PARIS_2021_02")
    assert "USA" not in parties("PARIS_2026_01")

    assert "ERI" not in parties("PARIS_2022")
    assert "ERI" in parties("PARIS_2023_03")
    assert "VAT" in parties("PARIS_2022_10")
    assert "IRN" not in parties("PARIS")

    assert set(iso3["PARIS_2026_01"].children[0]) == set(iso3["PARIS"].children[0])
    assert parties("PARIS") == parties("UNFCCC") - {"IRN", "LBY", "YEM", "USA"}


def test_versions_only_stable_codes():
    # changes which did not take effect yet and codes for the current year are left
    # out, because they could still change
    iso3 = ISO3_UNFCCC
    for code in ("UNFCCC_2027", "UNFCCC_2027_02", "PARIS_2026"):
        assert code not in iso3
    for code in iso3:
        if re.fullmatch(r"(UNFCCC|PARIS)_\d{4}(_\d{2})?", code):
            assert "not stable" not in iso3[code].comment


def test_g7g20():
    # since the EU is a non-enumerated member, G7 has 8 members, G8 has 9.
    assert len(ISO3_GROUPS["G7"].children[0]) == 8
    assert len(ISO3_GROUPS["G8"].children[0]) == 9
    # in the G20, the EU is enumerated
    assert len(ISO3_GROUPS["G20"].children[0]) == 20


def test_oecd():
    assert len(ISO3_GROUPS["OECD"].leaf_children[0]) == 38


def test_aosis():
    assert len(ISO3_GROUPS["AOSIS"].leaf_children[0]) == 39


@pytest.mark.parametrize("code", ["UMBRELLA", "LDC", "G35", "LMDC"])
def test_country_groups_included(code: str):
    assert code in ISO3_GROUPS


def test_gcam():
    assert (
        len(climate_categories.ISO3_GCAM["GCAM 7.0|Southeast Asia"].leaf_children[0])
        == 37
    )

    assert climate_categories.ISO3.version == climate_categories.ISO3_GCAM.version
    assert climate_categories.ISO3_GCAM.canonical_name == (
        "ISO3[eu,gcam,groups,historical,kosovo,unfccc]"
    )


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


def test_base_only_iso():
    # the base contains only the countries from ISO 3166-1 and the world
    iso3 = climate_categories.ISO3
    assert iso3.canonical_name == "ISO3"
    assert set(iso3["World"].children[0]) == set(iso3.values()) - {iso3["World"]}
    for code in ("EU", "UNFCCC", "Annex-I", "PARIS", "G20", "XKX", "SUN"):
        assert code not in iso3
    assert "PSE" in iso3


def test_options():
    assert set(climate_categories.ISO3.available_options) == {
        "eu",
        "unfccc",
        "groups",
        "historical",
        "kosovo",
        "gcam",
        "pse_in_isr",
    }
    # options are sorted, and built only once
    assert climate_categories.ISO3.with_options(["unfccc", "eu"]) is ISO3_UNFCCC
    assert climate_categories.cats["ISO3[unfccc,eu]"] is ISO3_UNFCCC
    assert ISO3_UNFCCC.name == "ISO3[eu,unfccc]"


def test_pse_in_isr():
    iso3 = climate_categories.cats["ISO3[pse_in_isr]"]
    assert "PSE" not in iso3
    assert "ISR" in iso3
    assert "PS" not in iso3
    assert "Palestine" in iso3["World"].comment
    assert iso3["ISR"].info["includes"] == ["PSE"]
    assert "Palestine" in iso3["ISR"].comment
    assert "includes" not in climate_categories.ISO3["ISR"].info
    assert (
        len(iso3["World"].children[0])
        == len(climate_categories.ISO3["World"].children[0]) - 1
    )


def test_primap():
    primap = climate_categories.ISO3_PRIMAP
    assert primap.canonical_name == "ISO3[eu,groups,historical,pse_in_isr,unfccc]"
    assert "PSE" not in primap
    with_pse = climate_categories.cats["ISO3[eu,groups,unfccc]"]

    def children(cat, code: str) -> set[str]:
        return {c.codes[0] for c in cat[code].children[0]}

    for code in ("UNFCCC", "PARIS", "Non-Annex-I", "ARAB", "UNFCCC_2022"):
        assert "PSE" in children(with_pse, code)
        assert children(primap, code) == children(with_pse, code) - {"PSE"}
        assert "Palestine" in primap[code].comment
    assert len(primap["UNFCCC"].children[0]) == 197


def test_gcam_keeps_pse():
    gcam = climate_categories.ISO3_GCAM
    assert "PSE" in gcam
    assert gcam["PSE"] in gcam["UNFCCC"].children[0]


def test_gcam_pse_in_isr_unsupported():
    with pytest.raises(climate_categories.UnsupportedCombinationError):
        climate_categories.ISO3.with_options(["gcam", "kosovo", "pse_in_isr"])
    with pytest.raises(climate_categories.UnsupportedCombinationError):
        climate_categories.cats["ISO3[gcam,kosovo,pse_in_isr]"]
    assert "ISO3[gcam,kosovo,pse_in_isr]" not in climate_categories.cats
    with pytest.warns(climate_categories.UnsupportedCombinationWarning):
        iso3 = climate_categories.ISO3.with_options(
            ["gcam", "kosovo", "pse_in_isr"], allow_unsupported=True
        )
    assert "PSE" not in iso3


def test_requires():
    with pytest.raises(ValueError, match="requires"):
        climate_categories.ISO3.with_options(["unfccc"])
    with pytest.raises(ValueError, match="requires"):
        climate_categories.ISO3.with_options(["gcam"])


def test_kosovo():
    iso3 = climate_categories.cats["ISO3[kosovo]"]
    assert iso3["XKX"].title == "Kosovo"
    assert iso3["XK"] == iso3["XKX"]
    assert iso3["SRB"].info["excludes"] == ["XKX"]
    assert "Kosovo" in iso3["SRB"].comment
    assert "excludes" not in climate_categories.ISO3["SRB"].info
    assert climate_categories.ISO3_GCAM["SRB"].info["excludes"] == ["XKX"]


def test_historical():
    iso3 = climate_categories.cats["ISO3[historical]"]
    assert iso3["SUN"].title.startswith("USSR")
    assert iso3["YUG"].info["former_alpha_2"] == "YU"
    assert iso3["TUR"].info["historical_names"] == ["Turkey"]
    # alpha-2 and numeric codes were re-used, so they are not codes of withdrawn
    # countries
    assert iso3["BY"] == iso3["BLR"]
    # ATF was re-used for the French Southern Territories
    assert iso3["ATF"].title == "French Southern Territories"
    assert iso3["FQHH"].info["former_alpha_3"] == "ATF"


def test_categories_comparable_across_options():
    assert climate_categories.ISO3["DEU"] == climate_categories.ISO3_PRIMAP["DEU"]
    assert hash(climate_categories.ISO3["DEU"]) == hash(
        climate_categories.ISO3_GCAM["DEU"]
    )
    assert climate_categories.ISO3_PRIMAP["EU"] == ISO3_EU["EU_2020"]
