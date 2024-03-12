"""Run this via `make climate_categories/data/ISO3.yaml` in the main directory."""

import pathlib
import typing

import requests

import climate_categories

URL = (
    "https://salsa.debian.org/iso-codes-team/iso-codes/-/raw/main/data/"
    "iso_3166-1.json?inline=false"
)
OUTPATH = pathlib.Path("./climate_categories/data/ISO3.yaml")


def main():
    """Generate the categorization."""

    categories = load_countries()

    # add some widely used additional categories
    categories["World"] = {
        "title": "The world",
        "alternative_codes": ["EARTH", "Earth", "WORLD"],
        "children": [list(categories.keys())],
    }
    categories = add_eu_categories(categories)
    categories = add_unfccc_categories(categories)
    categories = add_unfccc_names(categories)
    categories = add_aosis(categories)
    categories = add_g7g20(categories)
    categories = add_oecd(categories)
    categories = add_historical_names(categories)

    spec = {
        "name": "ISO3",
        "title": "ISO 3166-1 countries with climate-relevant groupings",
        "comment": "Countries, regions, and other areas. Also includes information on "
        "groups like being included in Annex I of the UN Framework Convention on "
        "Climate Change.",
        "references": """ISO 3166, https://www.iso.org/iso-3166-country-codes.html;
iso-codes package, https://salsa.debian.org/iso-codes-team/iso-codes;
UNFCCC Parties & Observers, https://unfccc.int/parties-observers;
EU members,
https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:EU_enlargements;
G7 and G20, https://www.bmuv.de/themen/europa-internationales/internationales/g7-und-g20;
OECD members, https://www.oecd.org/about/document/ratification-oecd-convention.htm;
AOSIS members, https://www.aosis.org/about/member-states/""",
        "institution": "UN",
        "last_update": "2023-06-22",
        "hierarchical": True,
        "version": "2023-06-22",
        "total_sum": False,
        "categories": categories,
        "canonical_top_level_category": "WORLD",
    }

    return climate_categories.HierarchicalCategorization.from_spec(spec)


def add_aosis(categories):
    categories["AOSIS"] = {
        "title": "Alliance of Small Island States",
        "children": [
            [
                "ATG",
                "BHS",
                "BRB",
                "BLZ",
                "CUB",
                "DMA",
                "DOM",
                "GRD",
                "GUY",
                "HTI",
                "JAM",
                "KNA",
                "LCA",
                "VCT",
                "SUR",
                "TTO",
                "COK",
                "FSM",
                "FJI",
                "KIR",
                "NRU",
                "NIU",
                "PLW",
                "PNG",
                "MHL",
                "WSM",
                "SLB",
                "TON",
                "TUV",
                "VUT",
                "CPV",
                "COM",
                "GNB",
                "MDV",
                "MUS",
                "STP",
                "SYC",
                "SGP",
                "TLS",
            ]
        ],
    }
    return categories


def add_historical_names(categories):
    categories["TUR"]["info"]["historical_names"] = ["Turkey"]
    return categories


def add_oecd(categories):
    categories["OECD"] = {
        "title": "Organisation for Economic Co-operation and Development",
        "children": [
            [
                "AUS",
                "AUT",
                "BEL",
                "CAN",
                "CHL",
                "COL",
                "CRI",
                "CZE",
                "DNK",
                "EST",
                "FIN",
                "FRA",
                "DEU",
                "GRC",
                "HUN",
                "ISL",
                "IRL",
                "ISR",
                "ITA",
                "JPN",
                "KOR",
                "LVA",
                "LTU",
                "LUX",
                "MEX",
                "NLD",
                "NZL",
                "NOR",
                "POL",
                "PRT",
                "SVK",
                "SVN",
                "ESP",
                "SWE",
                "CHE",
                "TUR",
                "GBR",
                "USA",
            ]
        ],
    }
    return categories


def add_g7g20(categories):
    categories["G7"] = {
        "title": "Group of Seven",
        "children": [["DEU", "FRA", "GBR", "ITA", "JPN", "USA", "CAN", "EU"]],
    }
    categories["G8"] = {
        "title": "Group of Eight",
        "children": [categories["G7"]["children"][0] + ["RUS"]],
    }
    categories["G20"] = {
        "title": "Group of 20",
        "children": [
            categories["G8"]["children"][0]
            + [
                "ARG",
                "AUS",
                "BRA",
                "CHN",
                "IND",
                "IDN",
                "MEX",
                "SAU",
                "ZAF",
                "KOR",
                "TUR",
            ]
        ],
    }
    return categories


def add_unfccc_names(categories):
    categories["BOL"]["info"]["unfccc_name"] = "Bolivia (Plurinational State of)"
    categories["COD"]["info"] = {"unfccc_name": "Democratic Republic of the Congo"}
    categories["VAT"]["info"] = {"unfccc_name": "Holy See"}
    categories["IRN"]["info"]["unfccc_name"] = "Iran (Islamic Republic of)"
    categories["FSM"]["info"]["unfccc_name"] = "Micronesia (Federated States of)"
    categories["KOR"]["info"]["unfccc_name"] = "Republic of Korea"
    categories["PSE"]["info"]["unfccc_name"] = "State of Palestine"
    categories["VEN"]["info"]["unfccc_name"] = "Venezuela (Bolivarian Republic of)"
    return categories


def add_unfccc_categories(categories):
    categories["Annex-I"] = {
        "title": "Annex-I parties to the UNFCCC",
        "comment": "Parties to the UN Framework Convention on Climate Change "
        "listed in Annex I of the Convention.",
        "alternative_codes": ["ANNEXI"],
        "children": [
            [
                "AUS",
                "AUT",
                "BLR",
                "BEL",
                "BGR",
                "CAN",
                "HRV",
                "CYP",
                "CZE",
                "DNK",
                "EST",
                "FIN",
                "FRA",
                "DEU",
                "GRC",
                "HUN",
                "ISL",
                "IRL",
                "ITA",
                "JPN",
                "LVA",
                "LIE",
                "LTU",
                "LUX",
                "MLT",
                "MCO",
                "NLD",
                "NZL",
                "NOR",
                "POL",
                "PRT",
                "ROU",
                "RUS",
                "SVK",
                "SVN",
                "ESP",
                "SWE",
                "CHE",
                "TUR",
                "UKR",
                "GBR",
                "USA",
                "EU",
            ]
        ],
    }
    categories["Non-Annex-I"] = {
        "title": "Non-Annex-I parties to the UNFCCC",
        "comment": "Parties to the UN Framework Convention on Climate Change "
        "not listed in Annex I of the Convention.",
        "alternative_codes": ["NONANNEXI", "Non Annex-I"],
        "children": [
            [
                "AFG",
                "ALB",
                "DZA",
                "AND",
                "AGO",
                "ATG",
                "ARG",
                "ARM",
                "AZE",
                "BHS",
                "BHR",
                "BGD",
                "BRB",
                "BLZ",
                "BEN",
                "BTN",
                "BIH",
                "BWA",
                "BRA",
                "BRN",
                "BFA",
                "BDI",
                "CPV",
                "KHM",
                "CMR",
                "CAF",
                "TCD",
                "CHL",
                "CHN",
                "COL",
                "COM",
                "COG",
                "COK",
                "CRI",
                "CIV",
                "CUB",
                "DJI",
                "DMA",
                "DOM",
                "ECU",
                "EGY",
                "SLV",
                "GNQ",
                "ERI",
                "SWZ",
                "ETH",
                "FJI",
                "GAB",
                "GMB",
                "GEO",
                "GHA",
                "GRD",
                "GTM",
                "GIN",
                "GNB",
                "GUY",
                "HTI",
                "HND",
                "IND",
                "IDN",
                "IRQ",
                "ISR",
                "JAM",
                "JOR",
                "KAZ",
                "KEN",
                "KIR",
                "KWT",
                "KGZ",
                "LAO",
                "LBN",
                "LSO",
                "LBR",
                "LBY",
                "MDG",
                "MWI",
                "MYS",
                "MDV",
                "MLI",
                "MHL",
                "MRT",
                "MUS",
                "MEX",
                "MNG",
                "MNE",
                "MAR",
                "MOZ",
                "MMR",
                "NAM",
                "NRU",
                "NPL",
                "NIC",
                "NER",
                "NGA",
                "NIU",
                "MKD",
                "OMN",
                "PAK",
                "PLW",
                "PAN",
                "PNG",
                "PRY",
                "PER",
                "PHL",
                "QAT",
                "RWA",
                "KNA",
                "LCA",
                "VCT",
                "WSM",
                "SMR",
                "STP",
                "SAU",
                "SEN",
                "SRB",
                "SYC",
                "SLE",
                "SGP",
                "SLB",
                "SOM",
                "ZAF",
                "SSD",
                "LKA",
                "SDN",
                "SUR",
                "SYR",
                "TJK",
                "THA",
                "TLS",
                "TGO",
                "TON",
                "TTO",
                "TUN",
                "TKM",
                "TUV",
                "UGA",
                "ARE",
                "URY",
                "UZB",
                "VUT",
                "VNM",
                "YEM",
                "ZMB",
                "ZWE",
                "PRK",
                "COD",
                "VAT",
                "IRN",
                "FSM",
                "KOR",
                "MDA",
                "PSE",
                "TZA",
                "VEN",
                "BOL",
            ]
        ],
    }
    categories["UNFCCC"] = {
        "title": "Parties to the UNFCCC",
        "comment": "Parties to the UN Framework Convention on Climate Change.",
        "children": [
            categories["Annex-I"]["children"][0]
            + categories["Non-Annex-I"]["children"][0],
            ["Annex-I", "Non-Annex-I"],
        ],
    }

    return categories


def add_eu_categories(categories):
    categories["EU_1993"] = {
        "title": "European Union from 1993 to 1994",
        "comment": "The European Union from 1993-11-1 to 1994-12-31.",
        "alternative_codes": ["EU12", "EU-12"],
        "children": [
            [
                "BEL",
                "DNK",
                "FRA",
                "DEU",
                "GRC",
                "IRL",
                "ITA",
                "LUX",
                "NLD",
                "PRT",
                "ESP",
                "GBR",
            ]
        ],
    }
    categories["EU_1995"] = {
        "title": "European Union from 1995 to 2004",
        "comment": "The European Union from 1995-01-01 to 2004-04-30.",
        "alternative_codes": ["EU15", "EU-15"],
        "children": [categories["EU_1993"]["children"][0] + ["AUT", "FIN", "SWE"]],
    }
    categories["EU_2004"] = {
        "title": "European Union from 2004 to 2006",
        "comment": "The European Union from 2004-05-01 to 2006-12-31.",
        "alternative_codes": ["EU25", "EU-25"],
        "children": [
            categories["EU_1995"]["children"][0]
            + ["CYP", "CZE", "EST", "HUN", "LVA", "LTU", "MLT", "POL", "SVK", "SVN"]
        ],
    }
    # Do not include EU27 as it is unclear what it means
    categories["EU_2007"] = {
        "title": "European Union from 2007 to 2013",
        "comment": "The European Union from 2007-01-01 to 2013-06-30.",
        "alternative_codes": ["EU27_2007", "EU-27_2007"],
        "children": [categories["EU_2004"]["children"][0] + ["BGR", "ROU"]],
    }
    categories["EU_2013"] = {
        "title": "European Union from 2013 to 2020",
        "comment": "The European Union from 2013-07-01 to 2020-01-31.",
        "alternative_codes": ["EU28", "EU-28"],
        "children": [categories["EU_2007"]["children"][0] + ["HRV"]],
    }
    eu2020_children = categories["EU_2013"]["children"][0].copy()
    eu2020_children.remove("GBR")
    # Do not include EU27 as it is unclear what it means
    categories["EU_2020"] = {
        "title": "European Union",
        "comment": "The European Union since 2020-02-01 to date. Note that the 'EU' "
        "code will always refer to the current EU, use EU_2020 if you need "
        "a stable code.",
        "alternative_codes": ["EU27_2020", "EU-27_2020", "EU", "EU27BX"],
        "children": [eu2020_children],
    }

    return categories


def load_countries() -> (
    dict[str, typing.Union[str, dict[str, str], list[str], list[list[str]]]]
):
    """Load countries from the iso-codes debian package."""
    r = requests.get(
        URL,
        headers={"Accept": "application/json"},
    )

    categories: dict[str, typing.Union[str, dict[str, str]]] = {}
    for country in r.json()["3166-1"]:
        country_spec = {
            "title": country["name"],
            "alternative_codes": [country["alpha_2"], country["numeric"]],
        }

        info = {}
        if "official_name" in country:
            info["official_name"] = country["official_name"]
        if "common_name" in country:
            info["common_name"] = country["common_name"]
        if info:
            country_spec["info"] = info

        categories[country["alpha_3"]] = country_spec

    return categories


if __name__ == "__main__":
    ISO3 = main()

    ISO3.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)
