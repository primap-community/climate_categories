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
    categories = add_basic(categories)
    categories = add_ldc(categories)
    categories = add_umbrella(categories)
    categories = add_OPEC(categories)
    categories = add_ARAB(categories)
    categories = add_LMDC(categories)
    categories = add_G35(categories)

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
UMBRELLA https://unfccc.int/process-and-meetings/parties-non-party-stakeholders/parties/party-groupings;
LDC https://www.un.org/development/desa/dpad/wp-content/uploads/sites/45/publication/ldc_list.pdf;
AOSIS members, https://www.aosis.org/about/member-states/;
OPEC https://www.opec.org/member-countries.html";
ARAB https://unfccc.int/party-groupings;
LMDC https://en.wikipedia.org/wiki/Like-Minded_Developing_Countries;
""",
        "institution": "UN",
        "last_update": "2025-07-31",
        "hierarchical": True,
        "version": "2025-07-31",
        "total_sum": False,
        "categories": categories,
        "canonical_top_level_category": "WORLD",
    }

    return climate_categories.HierarchicalCategorization.from_spec(spec)


def add_basic(categories):
    categories["BASIC"] = {
        "title": "BASIC countries",
        "children": [["BRA", "ZAF", "IND", "CHN"]],
    }
    return categories


def add_ldc(categories):
    categories["LDC"] = {
        "title": "Least Developed Countries",
        "children": [
            [
                "AGO",
                "BEN",
                "BFA",
                "BDI",
                "CAF",
                "TCD",
                "COM",
                "COD",
                "DJI",
                "ERI",
                "ETH",
                "GMB",
                "GIN",
                "GNB",
                "LSO",
                "LBR",
                "MDG",
                "MWI",
                "MLI",
                "MRT",
                "MOZ",
                "NER",
                "RWA",
                "SEN",
                "SLE",
                "SOM",
                "SSD",
                "SDN",
                "TGO",
                "UGA",
                "TZA",
                "ZMB",
                "AFG",
                "BGD",
                "KHM",
                "LAO",
                "MMR",
                "NPL",
                "TLS",
                "YEM",
                "HTI",
                "KIR",
                "SLB",
                "TUV",
            ]
        ],
    }
    return categories


def add_umbrella(categories):
    categories["UMBRELLA_2023"] = {
        "title": "The Umbrella Group",
        "comment": "The Umbrella Group is a coalition of Parties which formed following the adoption of the Kyoto Protocol. The United Kingdom formally joined the group in 2023.",
        "children": [
            [
                "AUS",
                "CAN",
                "ISL",
                "ISR",
                "JPN",
                "NZL",
                "KAZ",
                "NOR",
                "UKR",
                "USA",
                "GBR",
            ]
        ],
        "alternative_codes": ["UMBRELLA"],
    }
    return categories


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


def add_OPEC(categories):
    categories["OPEC"] = {
        "title": "Oranization of Petroleum Exporting Countries",
        "children": [
            [
                "IRN",
                "IRQ",
                "KWT",
                "SAU",
                "VEN",
                "LBY",
                "ARE",
                "DZA",
                "NGA",
                "GAB",
                "GNQ",
                "COG",
            ]
        ],
    }
    return categories


def add_ARAB(categories):
    categories["ARAB"] = {
        "title": "Arab Group",
        "children": [
            [
                "DZA",
                "BHR",
                "COM",
                "DJI",
                "EGY",
                "IRQ",
                "JOR",
                "KWT",
                "LBN",
                "LBY",
                "MAR",
                "MRT",
                "OMN",
                "PSE",
                "QAT",
                "SAU",
                "SOM",
                "SDN",
                "SYR",
                "TUN",
                "ARE",
                "YEM",
            ]
        ],
    }
    return categories


def add_LMDC(categories):
    categories["LMDC"] = {
        "title": "Like-minded developing countries",
        "children": [
            [
                "DZA",
                "BGD",
                "BOL",
                "CHN",
                "CUB",
                "ECU",
                "EGY",
                "SLV",
                "IND",
                "IDN",
                "IRN",
                "IRQ",
                "JOR",
                "KWT",
                "MYS",
                "MLI",
                "NIC",
                "PAK",
                "SAU",
                "LKA",
                "SDN",
                "SYR",
                "VEN",
                "VNM",
            ]
        ],
    }
    return categories


def add_G35(categories):
    categories["G35"] = {
        "title": "Group of 35",
        "children": [
            [
                "ARG",
                "AUS",
                "AZE",
                "BRA",
                "CAN",
                "CHL",
                "CHN",
                "COL",
                "EGY",
                "FRA",
                "DEU",
                "IND",
                "IDN",
                "IRN",
                "ITA",
                "JPN",
                "KAZ",
                "KEN",
                "KOR",
                "MYS",
                "MEX",
                "MNG",
                "NGA",
                "PAK",
                "PHL",
                "RUS",
                "SAU",
                "ZAF",
                "THA",
                "TUR",
                "GBR",
                "ARE",
                "USA",
                "VNM",
                "AUT",
                "BEL",
                "BGR",
                "HRV",
                "CYP",
                "CZE",
                "DNK",
                "EST",
                "FIN",
                "GRC",
                "HUN",
                "IRL",
                "LVA",
                "LTU",
                "LUX",
                "MLT",
                "NLD",
                "POL",
                "PRT",
                "ROU",
                "SVK",
                "SVN",
                "ESP",
                "SWE",
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


def load_countries() -> dict[
    str, typing.Union[str, dict[str, str], list[str], list[list[str]]]
]:
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
