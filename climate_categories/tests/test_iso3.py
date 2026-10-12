"""Tests for the 'ISO3' categorization."""

import datetime
import re

import pytest

import climate_categories

ISO3_EU = climate_categories.cats["ISO3[EU]"]
ISO3_UNFCCC = climate_categories.cats["ISO3[EU,UNFCCC]"]
ISO3_EU_GROUPS = climate_categories.cats["ISO3[EU,groups]"]


def children(cat, code: str) -> set[str]:
    """The primary codes of the first child set of the category."""
    return {c.codes[0] for c in cat[code].children[0]}


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
    assert len(ISO3_EU_GROUPS["G7"].children[0]) == 8
    assert len(ISO3_EU_GROUPS["G8"].children[0]) == 9
    # in the G20, the EU is enumerated
    assert len(ISO3_EU_GROUPS["G20"].children[0]) == 20


def test_oecd():
    assert len(ISO3_EU_GROUPS["OECD"].leaf_children[0]) == 38


def test_aosis():
    assert len(ISO3_EU_GROUPS["AOSIS"].leaf_children[0]) == 39
    assert ISO3_GROUPS["AOSIS"].codes == ("AOSIS_2011", "AOSIS")


def test_ldc_versions():
    iso3 = ISO3_GROUPS
    versions = [code for code in iso3 if re.fullmatch(r"LDC_\d{4}", code)]
    assert versions[0] == "LDC_1991"
    assert iso3["LDC"].codes == ("LDC_2024", "LDC")
    assert len(children(iso3, "LDC_2024")) == 44
    assert len(children(iso3, "LDC_2012")) == 49
    assert {"SSD", "WSM"} <= children(iso3, "LDC_2012")
    assert "WSM" not in children(iso3, "LDC_2014")
    assert "SSD" not in children(iso3, "LDC_2011")
    # inclusions are documented by year, the categories describe the end of the year
    assert "graduated: STP" in iso3["LDC_2024"].comment
    # graduations which did not take effect yet are left out
    assert "LDC_2026" not in iso3


def test_annex_versions():
    iso3 = ISO3_UNFCCC
    assert iso3["Annex-I_2013"] == iso3["Annex-I_2013_01"]
    assert children(iso3, "Annex-I_2013_01") == children(iso3, "Annex-I")
    assert children(iso3, "Non-Annex-I_2022_10") == children(iso3, "Non-Annex-I")

    def at(prefix: str, month: str) -> set[str]:
        """The members of the latest version of prefix in or before month."""
        versions = [
            code
            for code in iso3
            if re.fullmatch(rf"{prefix}_\d{{4}}_\d{{2}}", code) and code[-7:] <= month
        ]
        return children(iso3, max(versions))

    # the amendments to Annex I move parties from Non-Annex-I to Annex-I
    for code, before, after in (
        ("CZE", "1998_07", "1998_08"),
        ("MLT", "2010_09", "2010_10"),
        ("CYP", "2012_12", "2013_01"),
    ):
        assert code in at("Non-Annex-I", before)
        assert code not in at("Annex-I", before)
        assert code in at("Annex-I", after)
        assert code not in at("Non-Annex-I", after)
    # Turkey is listed in Annex I, but became a party only in 2004
    assert "TUR" not in at("Annex-I", "2004_04")
    assert "TUR" in at("Annex-I", "2004_05")
    # Annex-I and Non-Annex-I together are the parties
    for code in iso3:
        match = re.fullmatch(r"UNFCCC_(\d{4}_\d{2})", code)
        if (
            match
            and f"Annex-I_{match[1]}" in iso3
            and f"Non-Annex-I_{match[1]}" in iso3
        ):
            annex = children(iso3, f"Annex-I_{match[1]}")
            non_annex = children(iso3, f"Non-Annex-I_{match[1]}")
            assert not annex & non_annex
            assert annex | non_annex == children(iso3, code)


@pytest.mark.parametrize("code", ["UMBRELLA", "LDC", "G35", "LMDC"])
def test_country_groups_included(code: str):
    assert code in ISO3_EU_GROUPS


def test_gcam():
    assert (
        len(climate_categories.ISO3_GCAM["GCAM 7.0|Southeast Asia"].leaf_children[0])
        == 37
    )

    assert climate_categories.ISO3.version == climate_categories.ISO3_GCAM.version
    assert climate_categories.ISO3_GCAM.canonical_name == (
        "ISO3[EU,GCAM,groups,historical,Kosovo,UNFCCC]"
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
        "EU",
        "UNFCCC",
        "groups",
        "historical",
        "territories_in_sovereign_inventory",
        "no_unpopulated",
        "Antilles",
        "ESH_in_MAR",
        "MSR_PCN_in_GBR",
        "Kosovo",
        "GCAM",
        "PSE_in_ISR",
        "PRIMAP1",
    }
    # options are sorted, and built only once
    assert climate_categories.ISO3.with_options(["UNFCCC", "EU"]) is ISO3_UNFCCC
    assert climate_categories.cats["ISO3[UNFCCC,EU]"] is ISO3_UNFCCC
    assert ISO3_UNFCCC.name == "ISO3[EU,UNFCCC]"


def test_pse_in_isr():
    iso3 = climate_categories.cats["ISO3[PSE_in_ISR]"]
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


def test_groups():
    groups = climate_categories.ISO3_GROUPS
    assert groups.canonical_name == "ISO3[EU,groups,historical,UNFCCC]"
    assert "SUN" in groups
    assert "PSE" in children(groups, "UNFCCC")
    assert len(groups["UNFCCC"].children[0]) == 198


def test_pse_in_isr_groups():
    merged = climate_categories.cats["ISO3[EU,groups,historical,PSE_in_ISR,UNFCCC]"]
    assert "PSE" not in merged
    with_pse = climate_categories.ISO3_GROUPS
    for code in ("UNFCCC", "PARIS", "Non-Annex-I", "ARAB", "UNFCCC_2022"):
        assert "PSE" in children(with_pse, code)
        assert children(merged, code) == children(with_pse, code) - {"PSE"}
        assert "Palestine" in merged[code].comment
    assert len(merged["UNFCCC"].children[0]) == 197


def test_gcam_keeps_pse():
    gcam = climate_categories.ISO3_GCAM
    assert "PSE" in gcam
    assert gcam["PSE"] in gcam["UNFCCC"].children[0]


def test_gcam_pse_in_isr_unsupported():
    with pytest.raises(climate_categories.UnsupportedCombinationError):
        climate_categories.ISO3.with_options(["GCAM", "Kosovo", "PSE_in_ISR"])
    with pytest.raises(climate_categories.UnsupportedCombinationError):
        climate_categories.cats["ISO3[GCAM,Kosovo,PSE_in_ISR]"]
    assert "ISO3[GCAM,Kosovo,PSE_in_ISR]" not in climate_categories.cats
    with pytest.warns(climate_categories.UnsupportedCombinationWarning):
        iso3 = climate_categories.ISO3.with_options(
            ["GCAM", "Kosovo", "PSE_in_ISR"], allow_unsupported=True
        )
    assert "PSE" not in iso3


def test_requires():
    with pytest.raises(ValueError, match="requires"):
        climate_categories.ISO3.with_options(["UNFCCC"])
    with pytest.raises(ValueError, match="requires"):
        climate_categories.ISO3.with_options(["GCAM"])


def test_kosovo():
    iso3 = climate_categories.cats["ISO3[Kosovo]"]
    assert iso3["XKX"].title == "Kosovo"
    assert iso3["XK"] == iso3["XKX"]
    assert iso3["SRB"].info["excludes"] == ["XKX"]
    assert "Kosovo" in iso3["SRB"].comment
    assert "excludes" not in climate_categories.ISO3["SRB"].info
    assert climate_categories.ISO3_GCAM["SRB"].info["excludes"] == ["XKX"]
    # Kosovo is part of the world, but not a party to the UNFCCC
    assert iso3["XKX"] in iso3["World"].children[0]
    assert "XKX" not in children(climate_categories.ISO3_GCAM, "UNFCCC")


def test_merge_into_historical():
    # historical countries are not members of any child set, so they take over the
    # memberships of their successors
    historical = climate_categories.cats["ISO3[historical]"]
    ant = climate_categories.CategorizationOption(
        name="ant",
        title="Netherlands Antilles",
        last_update=datetime.date(2026, 1, 1),
        merge_into={"CUW": "ANT", "SXM": "ANT", "BES": "ANT"},
    )
    cat = historical.apply(ant)
    world = children(cat, "World")
    assert "ANT" in world
    assert not {"CUW", "SXM", "BES"} & world
    assert len(world) == len(children(historical, "World")) - 2


def test_territories_in_sovereign_inventory():
    iso3 = climate_categories.cats["ISO3[territories_in_sovereign_inventory]"]
    assert iso3["DNK"].info["includes"] == ["FRO", "GRL"]
    assert "Greenland" in iso3["DNK"].comment
    assert set(iso3["GBR"].info["includes"]) == {
        "GGY",
        "IMN",
        "JEY",
        "BMU",
        "CYM",
        "FLK",
        "GIB",
    }
    assert len(iso3["FRA"].info["includes"]) == 11
    for code in ("GRL", "PRI", "REU", "NFK", "ALA", "SJM", "GL"):
        assert code not in iso3
    # not included in the inventory of their sovereign country
    for code in ("ABW", "AIA", "MSR", "PCN", "TKL", "HKG"):
        assert code in iso3
    # unpopulated and disputed territories are left to other options
    for code in ("HMD", "ATF", "UMI", "ESH"):
        assert code in iso3
    assert "includes" not in climate_categories.ISO3["DNK"].info
    assert (
        len(iso3["World"].children[0])
        == len(climate_categories.ISO3["World"].children[0]) - 30
    )


def test_no_unpopulated():
    iso3 = climate_categories.cats["ISO3[no_unpopulated]"]
    for code in ("ATA", "ATF", "BVT", "HMD", "IOT", "SGS", "UMI", "AQ"):
        assert code not in iso3
    assert "PCN" in iso3
    assert "permanent population" in iso3["World"].comment
    assert (
        len(iso3["World"].children[0])
        == len(climate_categories.ISO3["World"].children[0]) - 7
    )


def test_antilles():
    with pytest.raises(ValueError, match="requires"):
        climate_categories.ISO3.with_options(["Antilles"])
    iso3 = climate_categories.cats["ISO3[Antilles,historical]"]
    assert iso3["ANT"].info["includes"] == ["BES", "CUW", "SXM"]
    world = children(iso3, "World")
    assert "ANT" in world
    assert not {"CUW", "SXM", "BES"} & world
    assert "ANT" not in children(climate_categories.cats["ISO3[historical]"], "World")


def test_esh_in_mar():
    iso3 = climate_categories.cats["ISO3[ESH_in_MAR]"]
    assert "ESH" not in iso3
    assert iso3["MAR"].info["includes"] == ["ESH"]
    assert "Western Sahara" in iso3["MAR"].comment
    # ESH and MAR are in the same GCAM regions
    gcam = climate_categories.cats[
        "ISO3[ESH_in_MAR,EU,GCAM,groups,historical,Kosovo,UNFCCC]"
    ]
    assert "ESH" not in gcam


def test_msr_pcn_in_gbr():
    iso3 = climate_categories.cats["ISO3[MSR_PCN_in_GBR]"]
    assert "MSR" not in iso3
    assert "PCN" not in iso3
    assert iso3["GBR"].info["includes"] == ["MSR", "PCN"]
    # together with the territories in the UK inventory
    iso3 = climate_categories.cats[
        "ISO3[MSR_PCN_in_GBR,territories_in_sovereign_inventory]"
    ]
    assert set(iso3["GBR"].info["includes"]) == {
        "GGY",
        "IMN",
        "JEY",
        "BMU",
        "CYM",
        "FLK",
        "GIB",
        "MSR",
        "PCN",
    }
    assert (
        len(iso3["World"].children[0])
        == len(climate_categories.ISO3["World"].children[0]) - 32
    )


@pytest.mark.parametrize(
    "option", ["Antilles", "MSR_PCN_in_GBR", "territories_in_sovereign_inventory"]
)
def test_gcam_territories_unsupported(option: str):
    with pytest.raises(climate_categories.UnsupportedCombinationError):
        climate_categories.ISO3.with_options(
            ["EU", "GCAM", "groups", "historical", "Kosovo", option, "UNFCCC"]
        )


def test_primap_territories():
    # the territory options give the PRIMAP-hist country list
    iso3 = climate_categories.ISO3_PRIMAP2
    assert iso3.canonical_name == (
        "ISO3[Antilles,ESH_in_MAR,EU,groups,historical,no_unpopulated,PSE_in_ISR,"
        "territories_in_sovereign_inventory,UNFCCC]"
    )
    world = children(iso3, "World")
    assert len(world) == 208
    assert {"ANT", "MSR", "PCN"} <= world
    assert not {"ATA", "CUW", "GRL", "ESH", "PSE"} & world
    # no territory is a party to the UNFCCC
    without = climate_categories.cats["ISO3[EU,groups,historical,PSE_in_ISR,UNFCCC]"]
    for code in ("UNFCCC", "Annex-I", "Non-Annex-I", "AOSIS", "LDC"):
        assert children(iso3, code) == children(without, code)


def test_primap1():
    iso3 = climate_categories.ISO3_PRIMAP1
    assert iso3.canonical_name == (
        "ISO3[Antilles,ESH_in_MAR,EU,groups,historical,PRIMAP1,PSE_in_ISR,"
        "territories_in_sovereign_inventory,UNFCCC]"
    )
    # the country list of PRIMAP-hist v2.x
    world = children(iso3, "EARTH")
    assert len(world) == 207
    assert {"ANT", "ATA"} <= world
    assert not {"MSR", "HMD", "ATF", "UMI", "BVT", "IOT", "PCN", "SGS"} & world
    assert {"MSR", "GGY"} <= set(iso3["GBR"].info["includes"])
    # the regions of PRIMAP-hist v2.x
    assert iso3["LDC"].codes[0] == "LDC_2012"
    assert len(children(iso3, "LDC")) == 49
    assert iso3["UMBRELLA"].codes[0] == "UMBRELLA_PRIMAP1"
    assert "RUS" in children(iso3, "UMBRELLA")
    assert iso3["NONANNEXI"].codes[0] == "NONANNEXI_PRIMAP1"
    assert len(children(iso3, "NONANNEXI")) == 149
    assert iso3["ANNEXI"] == iso3["Annex-I"]
    assert iso3["EU27BX"] == iso3["EU_2020"]
    # the observers ASM, GUM, and VIR are included in USA, the Netherlands Antilles
    # are included via their successors
    aosis = children(iso3, "AOSIS")
    assert iso3["AOSIS"].codes[0] == "AOSIS_PRIMAP1"
    assert "ANT" in aosis
    assert not {"ASM", "CUW", "GUM", "VIR"} & aosis
    assert len(aosis) == 40
    # the current definitions are still available under their dated codes
    assert len(children(iso3, "LDC_2024")) == 44
    assert "RUS" not in children(iso3, "UMBRELLA_2023")


@pytest.mark.parametrize("option", ["Kosovo", "MSR_PCN_in_GBR", "no_unpopulated"])
def test_primap1_conflicts(option: str):
    options = [*climate_categories.ISO3_PRIMAP1.enabled_options, option]
    with pytest.raises(ValueError, match="conflicts"):
        climate_categories.ISO3.with_options(options)


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
    assert climate_categories.ISO3["DEU"] == climate_categories.ISO3_GROUPS["DEU"]
    assert hash(climate_categories.ISO3["DEU"]) == hash(
        climate_categories.ISO3_GCAM["DEU"]
    )
    assert climate_categories.ISO3_GROUPS["EU"] == ISO3_EU["EU_2020"]
