"""Run this via `make climate_categories/data/ISO3.py` in the main directory.

Generates the base ISO3 categorization with all its options, including the ``GCAM``
option generated in ISO3_GCAM.py.
"""

import copy
import datetime
import itertools
import pathlib
import typing

import ISO3_GCAM
import requests
from utils import all_codes, write_option_family

import climate_categories

URL = (
    "https://salsa.debian.org/iso-codes-team/iso-codes/-/raw/main/data/"
    "iso_3166-1.json?inline=false"
)
URL_WITHDRAWN = (
    "https://salsa.debian.org/iso-codes-team/iso-codes/-/raw/main/data/"
    "iso_3166-3.json?inline=false"
)
DATA_DIR = pathlib.Path("./climate_categories/data")
LAST_UPDATE = datetime.date(2026, 9, 24)
# Last update of the options introduced with the option mechanism.
OPTIONS_LAST_UPDATE = datetime.date(2026, 10, 12)

# Kosovo is not part of ISO 3166-1, but used in some data sources like GCAM.
KOSOVO = {
    "XKX": {
        "title": "Kosovo",
        "comment": "Kosovo, which is not part of ISO 3166-1. XKX is the user-assigned "
        "code commonly used for it.",
        "alternative_codes": ["XK"],
    },
}

# Dependent territories which are included in the national inventory of their
# sovereign country under the UNFCCC, by sovereign country. Territories without
# permanent population are left out, they are removed by the no_unpopulated option.
TERRITORIES_IN_SOVEREIGN_INVENTORY = {
    # Crown Dependencies and the Overseas Territories which joined the UK's ratification
    # of the UNFCCC. Montserrat was included in earlier inventories (until about 2010),
    # but is not any more. Other Overseas Territories are not included.
    "GBR": ["GGY", "IMN", "JEY", "BMU", "CYM", "FLK", "GIB"],
    # The Convention perimeter, i.e. all overseas territories.
    "FRA": [
        "GLP",
        "GUF",
        "MTQ",
        "MYT",
        "REU",
        "MAF",
        "BLM",
        "SPM",
        "WLF",
        "PYF",
        "NCL",
    ],
    # U.S. Territories in the energy sector: American Samoa, Guam, Puerto Rico,
    # U.S. Virgin Islands, Wake Island, and other outlying U.S. Pacific Islands. The
    # Northern Mariana Islands are not named, we assume they are among the latter.
    "USA": ["ASM", "GUM", "MNP", "PRI", "VIR"],
    # External territories: Norfolk Island and the Indian Ocean Territories.
    "AUS": ["NFK", "CXR", "CCK"],
    # The UNFCCC submission is for Denmark, Greenland and the Faroe Islands.
    "DNK": ["FRO", "GRL"],
    # Svalbard, except for LULUCF.
    "NOR": ["SJM"],
    # The autonomous territory of Åland, not reported separately.
    "FIN": ["ALA"],
}

# The Least Developed Countries with the year of their inclusion in the list, from the
# list of the UN Department of Economic and Social Affairs and figure I.3 of the
# Handbook on the Least Developed Country Category (2024). The list is available from
# LDC_FIRST_YEAR on, earlier lists included Sikkim and the Yemen Arab Republic and the
# People's Democratic Republic of Yemen, which merged in 1990 into the Republic of
# Yemen, which was confirmed as an LDC in 1991.
LDC_FIRST_YEAR = 1991
LDC_INCLUDED: list[tuple[str, int]] = [
    *(
        (code, 1971)
        for code in (
            "AFG",
            "BEN",
            "BTN",
            "BWA",
            "BFA",
            "BDI",
            "TCD",
            "ETH",
            "GIN",
            "HTI",
            "LAO",
            "LSO",
            "MWI",
            "MDV",
            "MLI",
            "NPL",
            "NER",
            "RWA",
            "WSM",
            "SOM",
            "SDN",
            "UGA",
            "TZA",
            "YEM",
        )
    ),
    *((code, 1975) for code in ("BGD", "CAF", "GMB")),
    *((code, 1977) for code in ("CPV", "COM")),
    ("GNB", 1981),
    *((code, 1982) for code in ("DJI", "GNQ", "STP", "SLE", "TGO")),
    ("VUT", 1985),
    *((code, 1986) for code in ("KIR", "MRT", "TUV")),
    ("MMR", 1987),
    ("MOZ", 1988),
    ("LBR", 1990),
    *((code, 1991) for code in ("KHM", "COD", "MDG", "SLB", "ZMB")),
    *((code, 1994) for code in ("AGO", "ERI")),
    ("SEN", 2000),
    ("TLS", 2003),
    ("SSD", 2012),
]
# The countries which graduated from the list, with the year of graduation.
LDC_GRADUATED: list[tuple[str, int]] = [
    ("BWA", 1994),
    ("CPV", 2007),
    ("MDV", 2011),
    ("WSM", 2014),
    ("GNQ", 2017),
    ("VUT", 2020),
    ("BTN", 2023),
    ("STP", 2024),
]

# Territories without permanent population.
UNPOPULATED = ("ATA", "ATF", "BVT", "HMD", "IOT", "SGS", "UMI")

# Definitions of PRIMAP-hist up to v2.x, from the primap1 country table
# (SIMCAP_EM_COUNTRYTABLE_v8.3.xlsx). They reproduce the regions of PRIMAP-hist v2.5 to
# v2.8 exactly.
# PRIMAP-hist up to v2.x included these unpopulated territories in their sovereign
# country, and MSR in GBR.
PRIMAP1_MERGED = {"MSR": "GBR", "HMD": "AUS", "ATF": "FRA", "UMI": "USA"}
# PRIMAP-hist up to v2.x did not report these territories.
PRIMAP1_REMOVED = ("BVT", "IOT", "PCN", "SGS")
# The Umbrella Group, without a formal member list (2011-11-03).
PRIMAP1_UMBRELLA = ["AUS", "CAN", "JPN", "NOR", "NZL", "RUS", "UKR", "USA"]
# The observers of AOSIS in addition to its members (sidsnet.org, 2011-11-20). The
# observer Netherlands Antilles is given by CUW, SXM, and BES, which the Antilles option
# merges into ANT.
PRIMAP1_AOSIS_OBSERVERS = ["ASM", "BES", "CUW", "GUM", "SXM", "VIR"]
# The parties not listed in Annex I, without AND, BRN, IRQ, SOM, and VAT, which became
# parties from 2007 on, and without PSE.
PRIMAP1_NONANNEXI = [
    "AFG",
    "AGO",
    "ALB",
    "ARE",
    "ARG",
    "ARM",
    "ATG",
    "AZE",
    "BDI",
    "BEN",
    "BFA",
    "BGD",
    "BHR",
    "BHS",
    "BIH",
    "BLZ",
    "BOL",
    "BRA",
    "BRB",
    "BTN",
    "BWA",
    "CAF",
    "CHL",
    "CHN",
    "CIV",
    "CMR",
    "COD",
    "COG",
    "COK",
    "COL",
    "COM",
    "CPV",
    "CRI",
    "CUB",
    "DJI",
    "DMA",
    "DOM",
    "DZA",
    "ECU",
    "EGY",
    "ERI",
    "ETH",
    "FJI",
    "FSM",
    "GAB",
    "GEO",
    "GHA",
    "GIN",
    "GMB",
    "GNB",
    "GNQ",
    "GRD",
    "GTM",
    "GUY",
    "HND",
    "HTI",
    "IDN",
    "IND",
    "IRN",
    "ISR",
    "JAM",
    "JOR",
    "KAZ",
    "KEN",
    "KGZ",
    "KHM",
    "KIR",
    "KNA",
    "KOR",
    "KWT",
    "LAO",
    "LBN",
    "LBR",
    "LBY",
    "LCA",
    "LKA",
    "LSO",
    "MAR",
    "MDA",
    "MDG",
    "MDV",
    "MEX",
    "MHL",
    "MKD",
    "MLI",
    "MMR",
    "MNE",
    "MNG",
    "MOZ",
    "MRT",
    "MUS",
    "MWI",
    "MYS",
    "NAM",
    "NER",
    "NGA",
    "NIC",
    "NIU",
    "NPL",
    "NRU",
    "OMN",
    "PAK",
    "PAN",
    "PER",
    "PHL",
    "PLW",
    "PNG",
    "PRK",
    "PRY",
    "QAT",
    "RWA",
    "SAU",
    "SDN",
    "SEN",
    "SGP",
    "SLB",
    "SLE",
    "SLV",
    "SMR",
    "SRB",
    "SSD",
    "STP",
    "SUR",
    "SWZ",
    "SYC",
    "SYR",
    "TCD",
    "TGO",
    "THA",
    "TJK",
    "TKM",
    "TLS",
    "TON",
    "TTO",
    "TUN",
    "TUV",
    "TZA",
    "UGA",
    "URY",
    "UZB",
    "VCT",
    "VEN",
    "VNM",
    "VUT",
    "WSM",
    "YEM",
    "ZAF",
    "ZMB",
    "ZWE",
]

# Options which make up commonly used categorizations.
ALIASES = {
    "ISO3_GROUPS": ("EU", "groups", "historical", "UNFCCC"),
    "ISO3_GCAM": ("EU", "GCAM", "groups", "historical", "Kosovo", "UNFCCC"),
    # PRIMAP-hist from v3.0 on
    "ISO3_PRIMAP2": (
        "Antilles",
        "ESH_in_MAR",
        "EU",
        "groups",
        "historical",
        "no_unpopulated",
        "PSE_in_ISR",
        "territories_in_sovereign_inventory",
        "UNFCCC",
    ),
    # PRIMAP-hist up to v2.x
    "ISO3_PRIMAP1": (
        "Antilles",
        "ESH_in_MAR",
        "EU",
        "groups",
        "historical",
        "PRIMAP1",
        "PSE_in_ISR",
        "territories_in_sovereign_inventory",
        "UNFCCC",
    ),
}

# Combinations of options which are not quality-controlled.
UNSUPPORTED = (
    climate_categories.UnsupportedCombination(
        options=("GCAM", "PSE_in_ISR"),
        comment="the GCAM regions have PSE separately",
    ),
    climate_categories.UnsupportedCombination(
        options=("GCAM", "territories_in_sovereign_inventory"),
        comment="the GCAM regions have many territories in other regions than their "
        "sovereign country",
    ),
    climate_categories.UnsupportedCombination(
        options=("Antilles", "GCAM"),
        comment="some GCAM regions have only some of CUW, SXM, and BES",
    ),
    climate_categories.UnsupportedCombination(
        options=("GCAM", "MSR_PCN_in_GBR"),
        comment="the GCAM regions have MSR and PCN in other regions than GBR",
    ),
)

# Status of the UNFCCC at its depositary, the Secretary-General of the United Nations.
# Lists the date on which every party deposited its instrument of ratification,
# acceptance, approval, accession, or succession.
UNTC_UNFCCC_STATUS = (
    "https://treaties.un.org/Pages/ViewDetailsIII.aspx?src=TREATY&mtdsg_no=XXVII-7"
    "&chapter=27&Temp=mtdsg3&clang=_en"
)

# Parties to the UNFCCC with the date on which the Convention entered into force for
# them and a reference for it, in the order in which they joined. According to
# article 23 of the Convention (https://unfccc.int/resource/docs/convkp/conveng.pdf),
# the Convention entered into force on 1994-03-21 for all parties which deposited
# their instrument until 1993-12-21, and enters into force 90 days after the deposit
# for all later parties. For parties which joined until 2000, we give the depositary's
# status page as reference, for later parties the depositary notification. The
# Federal Republic of Yugoslavia acceded in 2001, the depositary lists this as the
# accession of Serbia. Montenegro became a party by succession, effective from its
# independence.
UNFCCC_JOINED: list[tuple[str, datetime.date, str]] = [
    ("ARM", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("ATG", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("AUS", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("BFA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("CAN", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("CHE", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("CHN", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("COK", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("CZE", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("DEU", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("DMA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("DNK", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("DZA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("ECU", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("ESP", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("EU", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("FJI", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("FSM", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("GBR", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("GIN", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("IND", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("ISL", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("JOR", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("JPN", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("KNA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("KOR", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("LCA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("LKA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("MCO", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("MDV", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("MEX", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("MHL", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("MNG", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("MUS", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("NLD", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("NOR", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("NRU", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("NZL", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("PER", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("PNG", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("PRT", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("SDN", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("SWE", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("SYC", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("TUN", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("TUV", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("UGA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("USA", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("UZB", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("VUT", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("ZMB", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("ZWE", datetime.date(1994, 3, 21), UNTC_UNFCCC_STATUS),
    ("CUB", datetime.date(1994, 4, 5), UNTC_UNFCCC_STATUS),
    ("MRT", datetime.date(1994, 4, 20), UNTC_UNFCCC_STATUS),
    ("BWA", datetime.date(1994, 4, 27), UNTC_UNFCCC_STATUS),
    ("HUN", datetime.date(1994, 5, 25), UNTC_UNFCCC_STATUS),
    ("PRY", datetime.date(1994, 5, 25), UNTC_UNFCCC_STATUS),
    ("AUT", datetime.date(1994, 5, 29), UNTC_UNFCCC_STATUS),
    ("BRA", datetime.date(1994, 5, 29), UNTC_UNFCCC_STATUS),
    ("ARG", datetime.date(1994, 6, 9), UNTC_UNFCCC_STATUS),
    ("MLT", datetime.date(1994, 6, 15), UNTC_UNFCCC_STATUS),
    ("BRB", datetime.date(1994, 6, 21), UNTC_UNFCCC_STATUS),
    ("FRA", datetime.date(1994, 6, 23), UNTC_UNFCCC_STATUS),
    ("BHS", datetime.date(1994, 6, 27), UNTC_UNFCCC_STATUS),
    ("ETH", datetime.date(1994, 7, 4), UNTC_UNFCCC_STATUS),
    ("BGD", datetime.date(1994, 7, 14), UNTC_UNFCCC_STATUS),
    ("ITA", datetime.date(1994, 7, 14), UNTC_UNFCCC_STATUS),
    ("IRL", datetime.date(1994, 7, 19), UNTC_UNFCCC_STATUS),
    ("MWI", datetime.date(1994, 7, 20), UNTC_UNFCCC_STATUS),
    ("NPL", datetime.date(1994, 7, 31), UNTC_UNFCCC_STATUS),
    ("FIN", datetime.date(1994, 8, 1), UNTC_UNFCCC_STATUS),
    ("LUX", datetime.date(1994, 8, 7), UNTC_UNFCCC_STATUS),
    ("PAK", datetime.date(1994, 8, 30), UNTC_UNFCCC_STATUS),
    ("TCD", datetime.date(1994, 9, 5), UNTC_UNFCCC_STATUS),
    ("ROU", datetime.date(1994, 9, 6), UNTC_UNFCCC_STATUS),
    ("GMB", datetime.date(1994, 9, 8), UNTC_UNFCCC_STATUS),
    ("LIE", datetime.date(1994, 9, 20), UNTC_UNFCCC_STATUS),
    ("TTO", datetime.date(1994, 9, 22), UNTC_UNFCCC_STATUS),
    ("BEN", datetime.date(1994, 9, 28), UNTC_UNFCCC_STATUS),
    ("MYS", datetime.date(1994, 10, 11), UNTC_UNFCCC_STATUS),
    ("EST", datetime.date(1994, 10, 25), UNTC_UNFCCC_STATUS),
    ("POL", datetime.date(1994, 10, 26), UNTC_UNFCCC_STATUS),
    ("GEO", datetime.date(1994, 10, 27), UNTC_UNFCCC_STATUS),
    ("PHL", datetime.date(1994, 10, 31), UNTC_UNFCCC_STATUS),
    ("GRC", datetime.date(1994, 11, 2), UNTC_UNFCCC_STATUS),
    ("GRD", datetime.date(1994, 11, 9), UNTC_UNFCCC_STATUS),
    ("URY", datetime.date(1994, 11, 16), UNTC_UNFCCC_STATUS),
    ("IDN", datetime.date(1994, 11, 21), UNTC_UNFCCC_STATUS),
    ("SVK", datetime.date(1994, 11, 23), UNTC_UNFCCC_STATUS),
    ("CRI", datetime.date(1994, 11, 24), UNTC_UNFCCC_STATUS),
    ("GUY", datetime.date(1994, 11, 27), UNTC_UNFCCC_STATUS),
    ("NGA", datetime.date(1994, 11, 27), UNTC_UNFCCC_STATUS),
    ("KEN", datetime.date(1994, 11, 28), UNTC_UNFCCC_STATUS),
    ("ALB", datetime.date(1995, 1, 1), UNTC_UNFCCC_STATUS),
    ("BOL", datetime.date(1995, 1, 1), UNTC_UNFCCC_STATUS),
    ("SEN", datetime.date(1995, 1, 15), UNTC_UNFCCC_STATUS),
    ("CMR", datetime.date(1995, 1, 17), UNTC_UNFCCC_STATUS),
    ("SMR", datetime.date(1995, 1, 26), UNTC_UNFCCC_STATUS),
    ("BLZ", datetime.date(1995, 1, 29), UNTC_UNFCCC_STATUS),
    ("COM", datetime.date(1995, 1, 29), UNTC_UNFCCC_STATUS),
    ("VNM", datetime.date(1995, 2, 14), UNTC_UNFCCC_STATUS),
    ("MMR", datetime.date(1995, 2, 23), UNTC_UNFCCC_STATUS),
    ("CIV", datetime.date(1995, 2, 27), UNTC_UNFCCC_STATUS),
    ("WSM", datetime.date(1995, 2, 27), UNTC_UNFCCC_STATUS),
    ("EGY", datetime.date(1995, 3, 5), UNTC_UNFCCC_STATUS),
    ("PRK", datetime.date(1995, 3, 5), UNTC_UNFCCC_STATUS),
    ("LBN", datetime.date(1995, 3, 15), UNTC_UNFCCC_STATUS),
    ("CHL", datetime.date(1995, 3, 22), UNTC_UNFCCC_STATUS),
    ("BHR", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("KWT", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("MLI", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("RUS", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("SAU", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("SLB", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("THA", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("VEN", datetime.date(1995, 3, 28), UNTC_UNFCCC_STATUS),
    ("LAO", datetime.date(1995, 4, 4), UNTC_UNFCCC_STATUS),
    ("JAM", datetime.date(1995, 4, 6), UNTC_UNFCCC_STATUS),
    ("COD", datetime.date(1995, 4, 9), UNTC_UNFCCC_STATUS),
    ("KIR", datetime.date(1995, 5, 8), UNTC_UNFCCC_STATUS),
    ("LSO", datetime.date(1995, 5, 8), UNTC_UNFCCC_STATUS),
    ("OMN", datetime.date(1995, 5, 9), UNTC_UNFCCC_STATUS),
    ("TGO", datetime.date(1995, 6, 6), UNTC_UNFCCC_STATUS),
    ("CAF", datetime.date(1995, 6, 8), UNTC_UNFCCC_STATUS),
    ("COL", datetime.date(1995, 6, 20), UNTC_UNFCCC_STATUS),
    ("LVA", datetime.date(1995, 6, 21), UNTC_UNFCCC_STATUS),
    ("LTU", datetime.date(1995, 6, 22), UNTC_UNFCCC_STATUS),
    ("CPV", datetime.date(1995, 6, 27), UNTC_UNFCCC_STATUS),
    ("ERI", datetime.date(1995, 7, 23), UNTC_UNFCCC_STATUS),
    ("BGR", datetime.date(1995, 8, 10), UNTC_UNFCCC_STATUS),
    ("AZE", datetime.date(1995, 8, 14), UNTC_UNFCCC_STATUS),
    ("NAM", datetime.date(1995, 8, 14), UNTC_UNFCCC_STATUS),
    ("KAZ", datetime.date(1995, 8, 15), UNTC_UNFCCC_STATUS),
    ("PAN", datetime.date(1995, 8, 21), UNTC_UNFCCC_STATUS),
    ("TKM", datetime.date(1995, 9, 3), UNTC_UNFCCC_STATUS),
    ("MDA", datetime.date(1995, 9, 7), UNTC_UNFCCC_STATUS),
    ("SLE", datetime.date(1995, 9, 20), UNTC_UNFCCC_STATUS),
    ("NER", datetime.date(1995, 10, 23), UNTC_UNFCCC_STATUS),
    ("BTN", datetime.date(1995, 11, 23), UNTC_UNFCCC_STATUS),
    ("MOZ", datetime.date(1995, 11, 23), UNTC_UNFCCC_STATUS),
    ("DJI", datetime.date(1995, 11, 25), UNTC_UNFCCC_STATUS),
    ("GHA", datetime.date(1995, 12, 5), UNTC_UNFCCC_STATUS),
    ("HND", datetime.date(1996, 1, 17), UNTC_UNFCCC_STATUS),
    ("GNB", datetime.date(1996, 1, 25), UNTC_UNFCCC_STATUS),
    ("NIC", datetime.date(1996, 1, 29), UNTC_UNFCCC_STATUS),
    ("SVN", datetime.date(1996, 2, 29), UNTC_UNFCCC_STATUS),
    ("SLV", datetime.date(1996, 3, 3), UNTC_UNFCCC_STATUS),
    ("GTM", datetime.date(1996, 3, 14), UNTC_UNFCCC_STATUS),
    ("KHM", datetime.date(1996, 3, 17), UNTC_UNFCCC_STATUS),
    ("MAR", datetime.date(1996, 3, 27), UNTC_UNFCCC_STATUS),
    ("ARE", datetime.date(1996, 3, 28), UNTC_UNFCCC_STATUS),
    ("SYR", datetime.date(1996, 4, 3), UNTC_UNFCCC_STATUS),
    ("BEL", datetime.date(1996, 4, 15), UNTC_UNFCCC_STATUS),
    ("YEM", datetime.date(1996, 5, 21), UNTC_UNFCCC_STATUS),
    ("NIU", datetime.date(1996, 5, 28), UNTC_UNFCCC_STATUS),
    ("HRV", datetime.date(1996, 7, 7), UNTC_UNFCCC_STATUS),
    ("TZA", datetime.date(1996, 7, 16), UNTC_UNFCCC_STATUS),
    ("QAT", datetime.date(1996, 7, 17), UNTC_UNFCCC_STATUS),
    ("ISR", datetime.date(1996, 9, 2), UNTC_UNFCCC_STATUS),
    ("IRN", datetime.date(1996, 10, 16), UNTC_UNFCCC_STATUS),
    ("HTI", datetime.date(1996, 12, 24), UNTC_UNFCCC_STATUS),
    ("SWZ", datetime.date(1997, 1, 5), UNTC_UNFCCC_STATUS),
    ("COG", datetime.date(1997, 1, 12), UNTC_UNFCCC_STATUS),
    ("VCT", datetime.date(1997, 3, 2), UNTC_UNFCCC_STATUS),
    ("BDI", datetime.date(1997, 4, 6), UNTC_UNFCCC_STATUS),
    ("UKR", datetime.date(1997, 8, 11), UNTC_UNFCCC_STATUS),
    ("SGP", datetime.date(1997, 8, 27), UNTC_UNFCCC_STATUS),
    ("ZAF", datetime.date(1997, 11, 27), UNTC_UNFCCC_STATUS),
    ("SUR", datetime.date(1998, 1, 12), UNTC_UNFCCC_STATUS),
    ("CYP", datetime.date(1998, 1, 13), UNTC_UNFCCC_STATUS),
    ("TJK", datetime.date(1998, 4, 7), UNTC_UNFCCC_STATUS),
    ("GAB", datetime.date(1998, 4, 21), UNTC_UNFCCC_STATUS),
    ("MKD", datetime.date(1998, 4, 28), UNTC_UNFCCC_STATUS),
    ("TON", datetime.date(1998, 10, 18), UNTC_UNFCCC_STATUS),
    ("RWA", datetime.date(1998, 11, 16), UNTC_UNFCCC_STATUS),
    ("DOM", datetime.date(1999, 1, 5), UNTC_UNFCCC_STATUS),
    ("MDG", datetime.date(1999, 8, 31), UNTC_UNFCCC_STATUS),
    ("LBY", datetime.date(1999, 9, 12), UNTC_UNFCCC_STATUS),
    ("STP", datetime.date(1999, 12, 28), UNTC_UNFCCC_STATUS),
    ("PLW", datetime.date(2000, 3, 9), UNTC_UNFCCC_STATUS),
    ("BLR", datetime.date(2000, 8, 9), UNTC_UNFCCC_STATUS),
    ("AGO", datetime.date(2000, 8, 15), UNTC_UNFCCC_STATUS),
    ("KGZ", datetime.date(2000, 8, 23), UNTC_UNFCCC_STATUS),
    ("GNQ", datetime.date(2000, 11, 14), UNTC_UNFCCC_STATUS),
    ("BIH", datetime.date(2000, 12, 6), UNTC_UNFCCC_STATUS),
    (
        "SRB",
        datetime.date(2001, 6, 10),
        "https://treaties.un.org/doc/Publication/CN/2001/CN.283.2001-Eng.pdf",
    ),
    (
        "AFG",
        datetime.date(2002, 12, 18),
        "https://treaties.un.org/doc/Publication/CN/2002/CN.1019.2002-Eng.pdf",
    ),
    (
        "LBR",
        datetime.date(2003, 2, 3),
        "https://treaties.un.org/doc/Publication/CN/2002/CN.1165.2002-Eng.pdf",
    ),
    (
        "TUR",
        datetime.date(2004, 5, 24),
        "https://treaties.un.org/doc/Publication/CN/2004/CN.154.2004-Eng.pdf",
    ),
    (
        "MNE",
        datetime.date(2006, 6, 3),
        "https://treaties.un.org/doc/Publication/CN/2006/CN.1359.2006-Eng.pdf",
    ),
    (
        "TLS",
        datetime.date(2007, 1, 8),
        "https://treaties.un.org/doc/Publication/CN/2006/CN.830.2006-Eng.pdf",
    ),
    (
        "BRN",
        datetime.date(2007, 11, 5),
        "https://treaties.un.org/doc/Publication/CN/2007/CN.801.2007-Eng.pdf",
    ),
    (
        "IRQ",
        datetime.date(2009, 10, 26),
        "https://treaties.un.org/doc/Publication/CN/2009/CN.488.2009-Eng.pdf",
    ),
    (
        "SOM",
        datetime.date(2009, 12, 10),
        "https://treaties.un.org/doc/Publication/CN/2009/CN.734.2009-Eng.pdf",
    ),
    (
        "AND",
        datetime.date(2011, 5, 31),
        "https://treaties.un.org/doc/Publication/CN/2011/CN.90.2011-Eng.pdf",
    ),
    (
        "SSD",
        datetime.date(2014, 5, 18),
        "https://treaties.un.org/doc/Publication/CN/2014/CN.91.2014-Eng.pdf",
    ),
    (
        "PSE",
        datetime.date(2016, 3, 17),
        "https://treaties.un.org/doc/Publication/CN/2015/CN.699.2015-Eng.pdf",
    ),
    (
        "VAT",
        datetime.date(2022, 10, 4),
        "https://treaties.un.org/doc/Publication/CN/2022/CN.184.2022-Eng.pdf",
    ),
]

# Parties which withdrew from the UNFCCC, with the date on which the withdrawal took
# effect according to article 25 of the Convention, and the depositary notification.
UNFCCC_LEFT: list[tuple[str, datetime.date, str]] = [
    (
        "USA",
        datetime.date(2027, 2, 27),
        "https://treaties.un.org/doc/Publication/CN/2026/CN.102.2026-Eng.pdf",
    ),
]

# The chapter of the UNFCCC in the treaty collection of its depositary, which lists the
# depositary notifications of the amendments to Annex I.
UNTC_UNFCCC_CHAPTER = (
    "https://treaties.un.org/doc/Publication/MTDSG/Volume%20II/Chapter%20XXVII/"
    "XXVII-7.en.pdf"
)
UNFCCC_TEXT = (
    "https://unfccc.int/sites/default/files/convention_text_with_annexes_english_for_"
    "posting.pdf"
)

# Countries listed in Annex I of the Convention, with the date from which they are
# listed. Amendments to Annex I enter into force six months after the depositary
# communicated their adoption (Article 16, paragraph 3 of the Convention). The original
# Annex I also listed Czechoslovakia, which was never a party to the Convention and was
# removed by the first amendment.
ANNEX_I_ADDED: list[tuple[str, datetime.date, str]] = [
    *(
        (code, datetime.date(1994, 3, 21), UNFCCC_TEXT)
        for code in (
            "AUS",
            "AUT",
            "BLR",
            "BEL",
            "BGR",
            "CAN",
            "DNK",
            "EU",
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
            "LTU",
            "LUX",
            "NLD",
            "NZL",
            "NOR",
            "POL",
            "PRT",
            "ROU",
            "RUS",
            "ESP",
            "SWE",
            "CHE",
            "TUR",
            "UKR",
            "GBR",
            "USA",
        )
    ),
    # decision 4/CP.3, communicated on 1998-02-13
    *(
        (code, datetime.date(1998, 8, 13), UNTC_UNFCCC_CHAPTER)
        for code in ("HRV", "CZE", "LIE", "MCO", "SVK", "SVN")
    ),
    # decision 3/CP.15, communicated on 2010-04-26
    ("MLT", datetime.date(2010, 10, 26), UNTC_UNFCCC_CHAPTER),
    # decision 10/CP.17, communicated on 2012-07-09
    ("CYP", datetime.date(2013, 1, 9), UNTC_UNFCCC_CHAPTER),
]

# Status of the Paris Agreement at its depositary, the Secretary-General of the United
# Nations. Lists the date on which every party deposited its instrument of
# ratification, acceptance, approval, or accession.
UNTC_PARIS_STATUS = (
    "https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=XXVII-7-d"
    "&chapter=27&clang=_en"
)

# Parties to the Paris Agreement with the date on which the Agreement entered into
# force for them and a reference for it, in the order in which they joined. According
# to article 21 of the Agreement
# (https://unfccc.int/sites/default/files/english_paris_agreement.pdf), the Agreement
# entered into force on 2016-11-04 for all parties which deposited their instrument
# until 2016-10-05, and enters into force 30 days after the deposit for all later
# parties. We give the depositary's status page as reference, except for the USA,
# which joined twice, for which we give the depositary notifications.
PARIS_JOINED: list[tuple[str, datetime.date, str]] = [
    ("ALB", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("ARE", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("ARG", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("ATG", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("AUT", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BGD", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BHS", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BLR", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BLZ", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BOL", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BRA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BRB", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("BRN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("CAN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("CHN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("CMR", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("COK", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("DEU", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("DMA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("EU", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("FJI", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("FRA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("FSM", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("GHA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("GIN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("GRD", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("GUY", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("HND", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("HUN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("IND", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("ISL", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("KIR", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("KNA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("LAO", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("LCA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("LKA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MAR", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MDG", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MDV", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MEX", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MHL", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MLI", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MLT", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MNG", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("MUS", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("NAM", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("NER", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("NOR", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("NPL", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("NRU", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("NZL", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PAN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PER", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PLW", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PNG", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PRK", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PRT", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("PSE", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SEN", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SGP", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SLB", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SOM", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SVK", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SWZ", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("SYC", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("THA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("TON", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("TUV", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("UGA", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("UKR", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    (
        "USA",
        datetime.date(2016, 11, 4),
        "https://treaties.un.org/doc/Publication/CN/2016/CN.612.2016-Eng.pdf",
    ),
    ("VCT", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("VUT", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("WSM", datetime.date(2016, 11, 4), UNTC_PARIS_STATUS),
    ("RWA", datetime.date(2016, 11, 5), UNTC_PARIS_STATUS),
    ("POL", datetime.date(2016, 11, 6), UNTC_PARIS_STATUS),
    ("CAF", datetime.date(2016, 11, 10), UNTC_PARIS_STATUS),
    ("CRI", datetime.date(2016, 11, 12), UNTC_PARIS_STATUS),
    ("SWE", datetime.date(2016, 11, 12), UNTC_PARIS_STATUS),
    ("GRC", datetime.date(2016, 11, 13), UNTC_PARIS_STATUS),
    ("PRY", datetime.date(2016, 11, 13), UNTC_PARIS_STATUS),
    ("URY", datetime.date(2016, 11, 18), UNTC_PARIS_STATUS),
    ("DZA", datetime.date(2016, 11, 19), UNTC_PARIS_STATUS),
    ("TKM", datetime.date(2016, 11, 19), UNTC_PARIS_STATUS),
    ("MCO", datetime.date(2016, 11, 23), UNTC_PARIS_STATUS),
    ("CIV", datetime.date(2016, 11, 24), UNTC_PARIS_STATUS),
    ("NIU", datetime.date(2016, 11, 27), UNTC_PARIS_STATUS),
    ("BEN", datetime.date(2016, 11, 30), UNTC_PARIS_STATUS),
    ("IDN", datetime.date(2016, 11, 30), UNTC_PARIS_STATUS),
    ("DNK", datetime.date(2016, 12, 1), UNTC_PARIS_STATUS),
    ("SLE", datetime.date(2016, 12, 1), UNTC_PARIS_STATUS),
    ("ZAF", datetime.date(2016, 12, 1), UNTC_PARIS_STATUS),
    ("GAB", datetime.date(2016, 12, 2), UNTC_PARIS_STATUS),
    ("STP", datetime.date(2016, 12, 2), UNTC_PARIS_STATUS),
    ("KOR", datetime.date(2016, 12, 3), UNTC_PARIS_STATUS),
    ("SAU", datetime.date(2016, 12, 3), UNTC_PARIS_STATUS),
    ("VNM", datetime.date(2016, 12, 3), UNTC_PARIS_STATUS),
    ("EST", datetime.date(2016, 12, 4), UNTC_PARIS_STATUS),
    ("IRL", datetime.date(2016, 12, 4), UNTC_PARIS_STATUS),
    ("JOR", datetime.date(2016, 12, 4), UNTC_PARIS_STATUS),
    ("LUX", datetime.date(2016, 12, 4), UNTC_PARIS_STATUS),
    ("GMB", datetime.date(2016, 12, 7), UNTC_PARIS_STATUS),
    ("JPN", datetime.date(2016, 12, 8), UNTC_PARIS_STATUS),
    ("AUS", datetime.date(2016, 12, 9), UNTC_PARIS_STATUS),
    ("PAK", datetime.date(2016, 12, 10), UNTC_PARIS_STATUS),
    ("BFA", datetime.date(2016, 12, 11), UNTC_PARIS_STATUS),
    ("BWA", datetime.date(2016, 12, 11), UNTC_PARIS_STATUS),
    ("DJI", datetime.date(2016, 12, 11), UNTC_PARIS_STATUS),
    ("ITA", datetime.date(2016, 12, 11), UNTC_PARIS_STATUS),
    ("FIN", datetime.date(2016, 12, 14), UNTC_PARIS_STATUS),
    ("MYS", datetime.date(2016, 12, 16), UNTC_PARIS_STATUS),
    ("GBR", datetime.date(2016, 12, 18), UNTC_PARIS_STATUS),
    ("ISR", datetime.date(2016, 12, 22), UNTC_PARIS_STATUS),
    ("COM", datetime.date(2016, 12, 23), UNTC_PARIS_STATUS),
    ("BGR", datetime.date(2016, 12, 29), UNTC_PARIS_STATUS),
    ("KAZ", datetime.date(2017, 1, 5), UNTC_PARIS_STATUS),
    ("ZMB", datetime.date(2017, 1, 8), UNTC_PARIS_STATUS),
    ("SVN", datetime.date(2017, 1, 15), UNTC_PARIS_STATUS),
    ("BHR", datetime.date(2017, 1, 22), UNTC_PARIS_STATUS),
    ("CUB", datetime.date(2017, 1, 27), UNTC_PARIS_STATUS),
    ("KEN", datetime.date(2017, 1, 27), UNTC_PARIS_STATUS),
    ("CYP", datetime.date(2017, 2, 3), UNTC_PARIS_STATUS),
    ("AZE", datetime.date(2017, 2, 8), UNTC_PARIS_STATUS),
    ("ESP", datetime.date(2017, 2, 11), UNTC_PARIS_STATUS),
    ("TCD", datetime.date(2017, 2, 11), UNTC_PARIS_STATUS),
    ("LSO", datetime.date(2017, 2, 19), UNTC_PARIS_STATUS),
    ("GTM", datetime.date(2017, 2, 24), UNTC_PARIS_STATUS),
    ("LTU", datetime.date(2017, 3, 4), UNTC_PARIS_STATUS),
    ("KHM", datetime.date(2017, 3, 8), UNTC_PARIS_STATUS),
    ("CHL", datetime.date(2017, 3, 12), UNTC_PARIS_STATUS),
    ("TUN", datetime.date(2017, 3, 12), UNTC_PARIS_STATUS),
    ("AFG", datetime.date(2017, 3, 17), UNTC_PARIS_STATUS),
    ("MRT", datetime.date(2017, 3, 29), UNTC_PARIS_STATUS),
    ("ETH", datetime.date(2017, 4, 8), UNTC_PARIS_STATUS),
    ("BIH", datetime.date(2017, 4, 15), UNTC_PARIS_STATUS),
    ("LVA", datetime.date(2017, 4, 15), UNTC_PARIS_STATUS),
    ("TJK", datetime.date(2017, 4, 21), UNTC_PARIS_STATUS),
    ("ARM", datetime.date(2017, 4, 22), UNTC_PARIS_STATUS),
    ("PHL", datetime.date(2017, 4, 22), UNTC_PARIS_STATUS),
    ("AND", datetime.date(2017, 4, 23), UNTC_PARIS_STATUS),
    ("SLV", datetime.date(2017, 4, 26), UNTC_PARIS_STATUS),
    ("BEL", datetime.date(2017, 5, 6), UNTC_PARIS_STATUS),
    ("JAM", datetime.date(2017, 5, 10), UNTC_PARIS_STATUS),
    ("COG", datetime.date(2017, 5, 21), UNTC_PARIS_STATUS),
    ("GEO", datetime.date(2017, 6, 7), UNTC_PARIS_STATUS),
    ("NGA", datetime.date(2017, 6, 15), UNTC_PARIS_STATUS),
    ("HRV", datetime.date(2017, 6, 23), UNTC_PARIS_STATUS),
    ("ROU", datetime.date(2017, 7, 1), UNTC_PARIS_STATUS),
    ("MDA", datetime.date(2017, 7, 20), UNTC_PARIS_STATUS),
    ("QAT", datetime.date(2017, 7, 23), UNTC_PARIS_STATUS),
    ("TGO", datetime.date(2017, 7, 28), UNTC_PARIS_STATUS),
    ("EGY", datetime.date(2017, 7, 29), UNTC_PARIS_STATUS),
    ("MWI", datetime.date(2017, 7, 29), UNTC_PARIS_STATUS),
    ("VEN", datetime.date(2017, 8, 20), UNTC_PARIS_STATUS),
    ("SRB", datetime.date(2017, 8, 24), UNTC_PARIS_STATUS),
    ("NLD", datetime.date(2017, 8, 27), UNTC_PARIS_STATUS),
    ("HTI", datetime.date(2017, 8, 30), UNTC_PARIS_STATUS),
    ("SDN", datetime.date(2017, 9, 1), UNTC_PARIS_STATUS),
    ("ZWE", datetime.date(2017, 9, 6), UNTC_PARIS_STATUS),
    ("TLS", datetime.date(2017, 9, 15), UNTC_PARIS_STATUS),
    ("BTN", datetime.date(2017, 10, 19), UNTC_PARIS_STATUS),
    ("MMR", datetime.date(2017, 10, 19), UNTC_PARIS_STATUS),
    ("ECU", datetime.date(2017, 10, 20), UNTC_PARIS_STATUS),
    ("LIE", datetime.date(2017, 10, 20), UNTC_PARIS_STATUS),
    ("CPV", datetime.date(2017, 10, 21), UNTC_PARIS_STATUS),
    ("DOM", datetime.date(2017, 10, 21), UNTC_PARIS_STATUS),
    ("CZE", datetime.date(2017, 11, 4), UNTC_PARIS_STATUS),
    ("CHE", datetime.date(2017, 11, 5), UNTC_PARIS_STATUS),
    ("NIC", datetime.date(2017, 11, 22), UNTC_PARIS_STATUS),
    ("SYR", datetime.date(2017, 12, 13), UNTC_PARIS_STATUS),
    ("COD", datetime.date(2018, 1, 12), UNTC_PARIS_STATUS),
    ("MNE", datetime.date(2018, 1, 19), UNTC_PARIS_STATUS),
    ("MKD", datetime.date(2018, 2, 8), UNTC_PARIS_STATUS),
    ("BDI", datetime.date(2018, 2, 16), UNTC_PARIS_STATUS),
    ("TTO", datetime.date(2018, 3, 24), UNTC_PARIS_STATUS),
    ("KWT", datetime.date(2018, 5, 23), UNTC_PARIS_STATUS),
    ("TZA", datetime.date(2018, 6, 17), UNTC_PARIS_STATUS),
    ("MOZ", datetime.date(2018, 7, 4), UNTC_PARIS_STATUS),
    ("COL", datetime.date(2018, 8, 11), UNTC_PARIS_STATUS),
    ("LBR", datetime.date(2018, 9, 26), UNTC_PARIS_STATUS),
    ("SMR", datetime.date(2018, 10, 26), UNTC_PARIS_STATUS),
    ("GNB", datetime.date(2018, 11, 21), UNTC_PARIS_STATUS),
    ("GNQ", datetime.date(2018, 11, 29), UNTC_PARIS_STATUS),
    ("UZB", datetime.date(2018, 12, 9), UNTC_PARIS_STATUS),
    ("SUR", datetime.date(2019, 3, 15), UNTC_PARIS_STATUS),
    ("OMN", datetime.date(2019, 6, 21), UNTC_PARIS_STATUS),
    ("RUS", datetime.date(2019, 11, 6), UNTC_PARIS_STATUS),
    ("LBN", datetime.date(2020, 3, 6), UNTC_PARIS_STATUS),
    ("KGZ", datetime.date(2020, 3, 19), UNTC_PARIS_STATUS),
    ("AGO", datetime.date(2020, 12, 16), UNTC_PARIS_STATUS),
    (
        "USA",
        datetime.date(2021, 2, 19),
        "https://treaties.un.org/doc/Publication/CN/2021/CN.10.2021-Eng.pdf",
    ),
    ("SSD", datetime.date(2021, 3, 25), UNTC_PARIS_STATUS),
    ("TUR", datetime.date(2021, 11, 10), UNTC_PARIS_STATUS),
    ("IRQ", datetime.date(2021, 12, 1), UNTC_PARIS_STATUS),
    ("VAT", datetime.date(2022, 10, 4), UNTC_PARIS_STATUS),
    ("ERI", datetime.date(2023, 3, 9), UNTC_PARIS_STATUS),
]

# Parties which withdrew from the Paris Agreement, with the date on which the
# withdrawal took effect according to article 28 of the Agreement, and the depositary
# notification.
PARIS_LEFT: list[tuple[str, datetime.date, str]] = [
    (
        "USA",
        datetime.date(2020, 11, 4),
        "https://treaties.un.org/doc/Publication/CN/2019/CN.575.2019-Eng.pdf",
    ),
    (
        "USA",
        datetime.date(2026, 1, 27),
        "https://treaties.un.org/doc/Publication/CN/2025/CN.71.2025-Eng.pdf",
    ),
]


def main():
    """Generate the base categorization and its options."""
    base = base_categories()
    base_codes = all_codes(base)

    eu = eu_option()
    options = [
        eu,
        unfccc_option(known_codes=base_codes | all_codes(eu.add_categories)),
        groups_option(),
        historical_option(known_codes=base_codes),
        kosovo_option(),
        ISO3_GCAM.gcam_option(base_codes | all_codes(KOSOVO)),
        pse_in_isr_option(),
        territories_in_sovereign_inventory_option(),
        no_unpopulated_option(),
        antilles_option(),
        esh_in_mar_option(),
        msr_pcn_in_gbr_option(),
        primap1_option(),
    ]
    manifest = climate_categories.OptionManifest(
        base="ISO3",
        options=tuple(option.name for option in options),
        unsupported=UNSUPPORTED,
        aliases=ALIASES,
    )

    spec = {
        "name": "ISO3",
        "title": "ISO 3166-1 countries",
        "comment": "Countries, regions, and other areas as defined in ISO 3166-1, and "
        "the world. Groupings like the parties to the UN Framework Convention on "
        "Climate Change are available as options, see ISO3.available_options. The "
        "alias ISO3_GROUPS includes all groupings commonly used in climate policy "
        "analysis and the historical countries.",
        "references": "ISO 3166, https://www.iso.org/iso-3166-country-codes.html;\n"
        "iso-codes package, https://salsa.debian.org/iso-codes-team/iso-codes",
        "institution": "ISO",
        "last_update": LAST_UPDATE.isoformat(),
        "hierarchical": True,
        "version": LAST_UPDATE.isoformat(),
        "total_sum": False,
        # from_spec modifies the categories
        "categories": copy.deepcopy(base),
        "canonical_top_level_category": "WORLD",
    }

    return (
        climate_categories.HierarchicalCategorization.from_spec(spec),
        options,
        manifest,
    )


def base_categories() -> dict[str, dict]:
    """The countries from ISO 3166-1 and the world."""
    categories = load_countries()
    # the world is needed as the canonical top level category
    categories["World"] = {
        "title": "The world",
        "alternative_codes": ["EARTH", "Earth", "WORLD"],
        "children": [list(categories.keys())],
    }
    return categories


def eu_option() -> climate_categories.CategorizationOption:
    return climate_categories.CategorizationOption(
        name="EU",
        title="European Union members",
        comment="The European Union at different points in time, use EU for the "
        "current European Union.",
        references="EU members, "
        "https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:EU_enlargements",
        last_update=LAST_UPDATE,
        add_categories=eu_categories(),
    )


def unfccc_option(known_codes: set[str]) -> climate_categories.CategorizationOption:
    """The UNFCCC option, all parties have to be in ``known_codes``."""
    categories = unfccc_categories()
    categories.update(unfccc_versions(categories, known_codes))
    categories.update(annex_versions(categories, known_codes))
    categories.update(paris_categories(categories, known_codes))
    return climate_categories.CategorizationOption(
        name="UNFCCC",
        title="UNFCCC and Paris Agreement parties",
        comment="Parties to the UN Framework Convention on Climate Change and to the "
        "Paris Agreement under it, currently (UNFCCC, PARIS) and over time "
        "(UNFCCC_YYYY_MM, PARIS_YYYY_MM), parties listed in Annex I of the "
        "Convention and other parties, currently (Annex-I, Non-Annex-I) and over "
        "time (Annex-I_YYYY_MM, Non-Annex-I_YYYY_MM), and the names of parties as "
        "used by the UNFCCC.",
        references="""UNFCCC Parties & Observers, https://unfccc.int/parties-observers;
UNFCCC status at the depositary,
https://treaties.un.org/Pages/ViewDetailsIII.aspx?src=TREATY&mtdsg_no=XXVII-7&chapter=27&Temp=mtdsg3&clang=_en;
Paris Agreement status at the depositary,
https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=XXVII-7-d&chapter=27&clang=_en;
Convention text with Annex I, https://unfccc.int/sites/default/files/convention_text_with_annexes_english_for_posting.pdf;
Amendments to Annex I, https://treaties.un.org/doc/Publication/MTDSG/Volume%20II/Chapter%20XXVII/XXVII-7.en.pdf""",
        last_update=LAST_UPDATE,
        requires=("EU",),
        add_categories=categories,
        update_categories=unfccc_names(),
    )


def groups_option() -> climate_categories.CategorizationOption:
    return climate_categories.CategorizationOption(
        name="groups",
        title="country groups",
        comment="Groups of countries in climate negotiations and international "
        "politics: AOSIS, BASIC, the Least Developed Countries (currently LDC, and "
        "over time LDC_YYYY), the Umbrella Group, the Arab Group, LMDC, G35, G7, G8, "
        "G20, OECD, and OPEC.",
        references="""G7 and G20, https://www.bmuv.de/themen/europa-internationales/internationales/g7-und-g20;
OECD members, https://www.oecd.org/about/document/ratification-oecd-convention.htm;
UMBRELLA https://unfccc.int/process-and-meetings/parties-non-party-stakeholders/parties/party-groupings;
LDC https://www.un.org/development/desa/dpad/wp-content/uploads/sites/45/publication/ldc_list.pdf;
LDC history, Handbook on the Least Developed Country Category, figure I.3, https://www.un.org/development/desa/dpad/wp-content/uploads/sites/45/LDC-Handbook-2024.pdf;
AOSIS members, https://www.aosis.org/about/member-states/;
OPEC https://www.opec.org/member-countries.html;
ARAB https://unfccc.int/party-groupings;
LMDC https://en.wikipedia.org/wiki/Like-Minded_Developing_Countries""",
        last_update=LAST_UPDATE,
        # the EU is a member of the G7 and G20
        requires=("EU",),
        add_categories={
            **aosis_categories(),
            **g7g20_categories(),
            **oecd_categories(),
            **basic_categories(),
            **ldc_categories(),
            **umbrella_categories(),
            **opec_categories(),
            **arab_categories(),
            **lmdc_categories(),
            **g35_categories(),
        },
    )


def historical_option(
    known_codes: set[str],
) -> climate_categories.CategorizationOption:
    """The historical option, withdrawn countries must not re-use ``known_codes``."""
    return climate_categories.CategorizationOption(
        name="historical",
        title="historical countries and names",
        comment="Countries which were withdrawn from ISO 3166-1, like the USSR (SUN) "
        "or Yugoslavia (YUG), and historical names of current countries. The "
        "alpha-2 and numeric codes of withdrawn countries were partly re-used for "
        "other countries, so they are only given in the info. If the alpha-3 code was "
        "re-used, the alpha-4 code from ISO 3166-3 is the primary code.",
        references="ISO 3166-3 in the iso-codes package, "
        "https://salsa.debian.org/iso-codes-team/iso-codes",
        last_update=OPTIONS_LAST_UPDATE,
        add_categories=withdrawn_countries(known_codes),
        update_categories=historical_names(),
    )


def kosovo_option() -> climate_categories.CategorizationOption:
    return climate_categories.CategorizationOption(
        name="Kosovo",
        title="Kosovo",
        comment="Kosovo, which is not part of ISO 3166-1, with the user-assigned code "
        "XKX which is commonly used for it.",
        last_update=OPTIONS_LAST_UPDATE,
        add_categories=KOSOVO,
        split_from={"XKX": "SRB"},
        join_parents={"XKX": ["World"]},
    )


def pse_in_isr_option() -> climate_categories.CategorizationOption:
    return climate_categories.CategorizationOption(
        name="PSE_in_ISR",
        title="Palestine included in Israel",
        comment="Palestine (PSE) is not listed separately, it is assumed to be "
        "included in Israel (ISR), so that sums over countries stay complete. Use "
        "this for data sources which do not report Palestine separately.",
        last_update=OPTIONS_LAST_UPDATE,
        merge_into={"PSE": "ISR"},
    )


def territories_in_sovereign_inventory_option() -> (
    climate_categories.CategorizationOption
):
    return climate_categories.CategorizationOption(
        name="territories_in_sovereign_inventory",
        title="territories included in the inventory of their sovereign country",
        comment="Dependent territories which are included in the national greenhouse "
        "gas inventory of their sovereign country under the UNFCCC are not listed "
        "separately, but included in their sovereign country, like the Faroe Islands "
        "(FRO) and Greenland (GRL) in Denmark (DNK). Territories which are not "
        "included in the inventory of their sovereign country, like Aruba (ABW), "
        "Anguilla (AIA), or Montserrat (MSR), are kept. Territories without "
        "permanent population are not included, use the option no_unpopulated to "
        "remove them.",
        references="""UK Greenhouse Gas Inventory, 1990 to 2024, chapter 1, https://unfccc.int/sites/default/files/resource/NID%2090-24.pdf;
Inventaire des émissions de gaz à effet de serre en France de 1990 à 2019, section 1.7, https://citepa.org/?p=20926;
Inventory of U.S. Greenhouse Gas Emissions and Sinks 1990-2022, chapter 3, https://www.epa.gov/system/files/documents/2024-04/us-ghg-inventory-2024-chapter-3-energy.pdf;
National Inventory Report 2022, volume 1, section 1.7.2, https://www.dcceew.gov.au/climate-change/publications/national-inventory-reports;
Denmark's National Inventory Document 2026, chapter 1, https://unfccc.int/sites/default/files/resource/Denmark%27s%20National%20Inventory%20Document%202026.pdf;
Greenhouse Gas Emissions 1990-2024, National Inventory Document (Norway), section 1.7.1, https://unfccc.int/sites/default/files/resource/Norway%20National%20Inventory%20Document%202026.pdf;
Greenhouse gas emissions in Finland 1990 to 2019, section 1.7, https://stat.fi/meta/kas/nir_en.html""",
        last_update=OPTIONS_LAST_UPDATE,
        merge_into={
            territory: sovereign
            for sovereign, territories in TERRITORIES_IN_SOVEREIGN_INVENTORY.items()
            for territory in territories
        },
    )


def no_unpopulated_option() -> climate_categories.CategorizationOption:
    return climate_categories.CategorizationOption(
        name="no_unpopulated",
        title="no unpopulated territories",
        comment="Territories without permanent population, like Antarctica (ATA) "
        "or Bouvet Island (BVT), are removed. Use this for data sources which do "
        "not report them.",
        last_update=OPTIONS_LAST_UPDATE,
        remove_categories=climate_categories.CategoryRemoval(
            codes=UNPOPULATED,
            comment="Territories without permanent population are removed.",
        ),
    )


def antilles_option() -> climate_categories.CategorizationOption:
    return climate_categories.CategorizationOption(
        name="Antilles",
        title="Netherlands Antilles",
        comment="Curaçao (CUW), Sint Maarten (SXM), and Bonaire, Sint Eustatius and "
        "Saba (BES) are not listed separately, but included in the Netherlands "
        "Antilles (ANT), which were dissolved on 2010-10-10. Use this for data "
        "sources which report the Netherlands Antilles instead of their successors.",
        last_update=OPTIONS_LAST_UPDATE,
        requires=("historical",),
        merge_into={"CUW": "ANT", "SXM": "ANT", "BES": "ANT"},
    )


def esh_in_mar_option() -> climate_categories.CategorizationOption:
    return climate_categories.CategorizationOption(
        name="ESH_in_MAR",
        title="Western Sahara included in Morocco",
        comment="Western Sahara (ESH) is not listed separately, it is assumed to be "
        "included in Morocco (MAR), so that sums over countries stay complete. Use "
        "this for data sources which do not report Western Sahara separately.",
        last_update=OPTIONS_LAST_UPDATE,
        merge_into={"ESH": "MAR"},
    )


def msr_pcn_in_gbr_option() -> climate_categories.CategorizationOption:
    return climate_categories.CategorizationOption(
        name="MSR_PCN_in_GBR",
        title="Montserrat and Pitcairn included in the United Kingdom",
        comment="Montserrat (MSR) and Pitcairn (PCN) are not listed separately, they "
        "are assumed to be included in the United Kingdom (GBR). Their population is "
        "tiny, so for many applications it is sensible to include them, even though "
        "the national greenhouse gas inventory of the United Kingdom does not cover "
        "them. Use this together with territories_in_sovereign_inventory for data "
        "sources which do not report them separately.",
        last_update=OPTIONS_LAST_UPDATE,
        merge_into={"MSR": "GBR", "PCN": "GBR"},
    )


def primap1_option() -> climate_categories.CategorizationOption:
    return climate_categories.CategorizationOption(
        name="PRIMAP1",
        title="PRIMAP-hist up to v2.x",
        comment="The countries and regions of PRIMAP-hist up to v2.x, which was "
        "produced with the primap1 library. Montserrat (MSR) and the unpopulated "
        "territories HMD, ATF, and UMI are included in their sovereign country, BVT, "
        "IOT, PCN, and SGS are removed, so that World contains the countries and "
        "territories of PRIMAP-hist. The region codes of PRIMAP-hist v2.x refer to "
        "the definitions of PRIMAP-hist v2.x: LDC to LDC_2012, AOSIS to "
        "AOSIS_PRIMAP1, UMBRELLA to UMBRELLA_PRIMAP1, and NONANNEXI to "
        "NONANNEXI_PRIMAP1. ANNEXI, EU27BX, BASIC, and EARTH are unchanged.",
        references="""PRIMAP-hist v2.8, https://zenodo.org/records/22876287;
Gütschow et al. (2016), The PRIMAP-hist national historical emissions time series, https://doi.org/10.5194/essd-8-571-2016""",
        last_update=OPTIONS_LAST_UPDATE,
        requires=(
            "Antilles",
            "ESH_in_MAR",
            "EU",
            "groups",
            "historical",
            "PSE_in_ISR",
            "territories_in_sovereign_inventory",
            "UNFCCC",
        ),
        conflicts=("Kosovo", "MSR_PCN_in_GBR", "no_unpopulated"),
        add_categories={
            "AOSIS_PRIMAP1": {
                "title": "Alliance of Small Island States with observers "
                "(PRIMAP-hist v2.x)",
                "comment": "The members and observers of the Alliance of Small Island "
                "States as of 2011-11-20, as used in PRIMAP-hist up to v2.x.",
                "children": [
                    sorted(
                        aosis_categories()["AOSIS_2011"]["children"][0]
                        + PRIMAP1_AOSIS_OBSERVERS
                    )
                ],
            },
            "UMBRELLA_PRIMAP1": {
                "title": "The Umbrella Group (PRIMAP-hist v2.x)",
                "comment": "The Umbrella Group as used in PRIMAP-hist up to v2.x, "
                "following the UNFCCC website in 2011, which gave no formal list.",
                "children": [PRIMAP1_UMBRELLA],
            },
            "NONANNEXI_PRIMAP1": {
                "title": "Non-Annex-I parties to the UNFCCC (PRIMAP-hist v2.x)",
                "comment": "The parties to the UNFCCC not listed in Annex I of the "
                "Convention as used in PRIMAP-hist up to v2.x, without Andorra, "
                "Brunei, Iraq, Somalia, and the Holy See, which became parties from "
                "2007 on.",
                "children": [PRIMAP1_NONANNEXI],
            },
        },
        remove_alternative_codes={
            "LDC": "LDC_2024",
            "AOSIS": "AOSIS_2011",
            "UMBRELLA": "UMBRELLA_2023",
            "NONANNEXI": "Non-Annex-I",
        },
        add_alternative_codes={
            "LDC": "LDC_2012",
            "AOSIS": "AOSIS_PRIMAP1",
            "UMBRELLA": "UMBRELLA_PRIMAP1",
            "NONANNEXI": "NONANNEXI_PRIMAP1",
        },
        merge_into=PRIMAP1_MERGED,
        remove_categories=climate_categories.CategoryRemoval(
            codes=PRIMAP1_REMOVED,
            comment="Territories which are not in PRIMAP-hist up to v2.x are removed.",
        ),
    )


def basic_categories() -> dict[str, dict]:
    categories = {}
    categories["BASIC"] = {
        "title": "BASIC countries",
        "children": [["BRA", "ZAF", "IND", "CHN"]],
    }
    return categories


def ldc_categories() -> dict[str, dict]:
    """The Least Developed Countries over time, from LDC_INCLUDED and LDC_GRADUATED.

    Inclusions are only documented by year, so for every year from 1991 in which
    countries were included or graduated, there is a category LDC_YYYY containing the
    LDCs at the end of the year. The latest category additionally has the code LDC.
    Years from the year of LAST_UPDATE on are left out, so that all codes are stable.
    """
    changes = sorted(
        {
            max(year, LDC_FIRST_YEAR)
            for _, year in (*LDC_INCLUDED, *LDC_GRADUATED)
            if year < LAST_UPDATE.year
        }
    )
    categories = {}
    for i, year in enumerate(changes):
        included = [c for c, y in LDC_INCLUDED if y <= year]
        graduated = [c for c, y in LDC_GRADUATED if y <= year]
        members = [c for c in included if c not in graduated]

        if i + 1 < len(changes):
            end = changes[i + 1] - 1
            validity = f"from {year} to {end}" if end > year else f"in {year}"
        else:
            validity = f"since {year}"
        if i == 0:
            comment = (
                f"The Least Developed Countries at the end of {year}, after the Republic "
                "of Yemen was confirmed as an LDC. Earlier lists included Sikkim and the "
                "two Yemeni states, so they are not available."
            )
        else:
            descriptions = []
            for kind, countries in (
                ("included", [c for c, y in LDC_INCLUDED if y == year]),
                ("graduated", [c for c, y in LDC_GRADUATED if y == year]),
            ):
                if countries:
                    descriptions.append(f"{kind}: {', '.join(countries)}")
            comment = (
                f"The Least Developed Countries at the end of {year}. Changes in "
                f"{year}, {'; '.join(descriptions)}."
            )
        comment += (
            " Inclusions in the list are only documented by year, so the category "
            "describes the list at the end of the year."
        )
        spec = {
            "title": f"Least Developed Countries {validity}",
            "comment": comment,
            "children": [members],
        }
        if i + 1 == len(changes):
            spec["comment"] += (
                " Note that the 'LDC' code will always refer to the current list, use "
                f"LDC_{year} if you need a stable code."
            )
            spec["alternative_codes"] = ["LDC"]
        categories[f"LDC_{year}"] = spec

    assert len(categories["LDC_2012"]["children"][0]) == 49
    assert len(categories["LDC_2024"]["children"][0]) == 44

    return categories


def umbrella_categories() -> dict[str, dict]:
    categories = {}
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


def aosis_categories() -> dict[str, dict]:
    categories = {}
    categories["AOSIS_2011"] = {
        "title": "Alliance of Small Island States",
        "comment": "The members of the Alliance of Small Island States. The "
        "membership is unchanged since at least 2011-11-20, when the earliest list we "
        "checked was published (sidsnet.org, as used in PRIMAP-hist up to v2.x). "
        "Note that the 'AOSIS' code will always refer to the current members, use "
        "AOSIS_2011 if you need a stable code.",
        "alternative_codes": ["AOSIS"],
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


def opec_categories() -> dict[str, dict]:
    categories = {}
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


def arab_categories() -> dict[str, dict]:
    categories = {}
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


def lmdc_categories() -> dict[str, dict]:
    categories = {}
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


def g35_categories() -> dict[str, dict]:
    categories = {}
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


def historical_names() -> dict[str, dict]:
    """Historical names of current countries, as category updates."""
    return {"TUR": {"info": {"historical_names": ["Turkey"]}}}


def withdrawn_countries(known_codes: set[str]) -> dict[str, dict]:
    """Countries withdrawn from ISO 3166-1, from the iso-codes debian package.

    Codes in ``known_codes`` are not re-used."""
    r = requests.get(URL_WITHDRAWN, headers={"Accept": "application/json"})
    r.raise_for_status()

    known_codes = set(known_codes)
    categories = {}

    for country in r.json()["3166-3"]:
        # alpha-3 codes were partly re-used, use the unique alpha-4 code then
        if country["alpha_3"] in known_codes:
            codes = [country["alpha_4"]]
        else:
            codes = [country["alpha_3"], country["alpha_4"]]
        assert not set(codes) & known_codes, codes
        known_codes.update(codes)

        date = country["withdrawal_date"]
        comment = (
            f"Withdrawn from ISO 3166-1 {'in' if len(date) == 4 else 'on'} {date}."
        )
        if "comment" in country:
            comment += f" {country['comment'][0].upper()}{country['comment'][1:]}."
        info = {
            "withdrawal_date": country["withdrawal_date"],
            "former_alpha_3": country["alpha_3"],
            "former_alpha_2": country["alpha_2"],
        }
        if "numeric" in country:
            info["former_numeric"] = country["numeric"]

        spec = {"title": country["name"], "comment": comment, "info": info}
        if len(codes) > 1:
            spec["alternative_codes"] = codes[1:]
        categories[codes[0]] = spec

    return categories


def oecd_categories() -> dict[str, dict]:
    categories = {}
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


def g7g20_categories() -> dict[str, dict]:
    categories = {}
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


def unfccc_names() -> dict[str, dict]:
    """The names used by the UNFCCC where they differ, as category updates."""
    names = {
        "BOL": "Bolivia (Plurinational State of)",
        "COD": "Democratic Republic of the Congo",
        "VAT": "Holy See",
        "IRN": "Iran (Islamic Republic of)",
        "FSM": "Micronesia (Federated States of)",
        "KOR": "Republic of Korea",
        "PSE": "State of Palestine",
        "VEN": "Venezuela (Bolivarian Republic of)",
    }
    return {code: {"info": {"unfccc_name": name}} for code, name in names.items()}


def unfccc_categories() -> dict[str, dict]:
    categories = {}
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
        "comment": "Parties to the UN Framework Convention on Climate Change. Note "
        "that the 'UNFCCC' code will always refer to the current parties, use the "
        "UNFCCC_YYYY_MM or UNFCCC_YYYY codes for past months or years if you need a "
        "stable code.",
        "children": [
            categories["Annex-I"]["children"][0]
            + categories["Non-Annex-I"]["children"][0],
            ["Annex-I", "Non-Annex-I"],
        ],
    }

    return categories


def unfccc_versions(unfccc: dict[str, dict], known_codes: set[str]) -> dict[str, dict]:
    """The parties to the UNFCCC over time, see party_versions.

    ``unfccc`` are the categories from unfccc_categories."""
    categories = party_versions(
        known_codes,
        prefix="UNFCCC",
        joined=UNFCCC_JOINED,
        left=UNFCCC_LEFT,
        title="Parties to the UNFCCC",
        description="Parties to the UN Framework Convention on Climate Change",
        instrument="Convention",
    )

    assert set(categories["UNFCCC_2022_10"]["children"][0]) == set(
        unfccc["UNFCCC"]["children"][0]
    )

    return categories


def annex_versions(unfccc: dict[str, dict], known_codes: set[str]) -> dict[str, dict]:
    """The parties listed in Annex I of the Convention and the other parties over
    time, see party_versions.

    A party is in Annex-I from the date on which it is a party and listed in Annex I,
    and in Non-Annex-I while it is a party and not listed in Annex I.

    ``unfccc`` are the categories from unfccc_categories."""
    listed = {code: date for code, date, _ in ANNEX_I_ADDED}
    references = {code: reference for code, _, reference in ANNEX_I_ADDED}
    references.update({code: reference for code, _, reference in UNFCCC_JOINED})
    references.update({code: reference for code, _, reference in UNFCCC_LEFT})
    dates = sorted(
        {date for _, date, _ in (*UNFCCC_JOINED, *UNFCCC_LEFT, *ANNEX_I_ADDED)}
    )

    def parties(date: datetime.date) -> set[str]:
        joined = {code for code, d, _ in UNFCCC_JOINED if d <= date}
        left = {code for code, d, _ in UNFCCC_LEFT if d <= date}
        return joined - left

    def listed_at(date: datetime.date) -> set[str]:
        return {code for code, d in listed.items() if d <= date}

    def changes(
        members: typing.Callable[[datetime.date], set[str]],
    ) -> tuple[
        list[tuple[str, datetime.date, str]], list[tuple[str, datetime.date, str]]
    ]:
        joined, left = [], []
        previous: set[str] = set()
        for date in dates:
            current = members(date)
            joined += [(c, date, references[c]) for c in sorted(current - previous)]
            left += [(c, date, references[c]) for c in sorted(previous - current)]
            previous = current
        return joined, left

    annex_joined, annex_left = changes(lambda d: parties(d) & listed_at(d))
    categories = party_versions(
        known_codes,
        prefix="Annex-I",
        joined=annex_joined,
        left=annex_left,
        title="Annex-I parties to the UNFCCC",
        description="Parties to the UN Framework Convention on Climate Change listed "
        "in Annex I of the Convention",
        instrument="Convention",
    )
    non_annex_joined, non_annex_left = changes(lambda d: parties(d) - listed_at(d))
    categories.update(
        party_versions(
            known_codes,
            prefix="Non-Annex-I",
            joined=non_annex_joined,
            left=non_annex_left,
            title="Non-Annex-I parties to the UNFCCC",
            description="Parties to the UN Framework Convention on Climate Change not "
            "listed in Annex I of the Convention",
            instrument="Convention",
        )
    )

    for code in ("Annex-I", "Non-Annex-I"):
        latest = max(c for c in categories if c.startswith(f"{code}_"))
        assert set(categories[latest]["children"][0]) == set(
            unfccc[code]["children"][0]
        ), latest

    return categories


def paris_categories(unfccc: dict[str, dict], known_codes: set[str]) -> dict[str, dict]:
    """The parties to the Paris Agreement, currently and over time.

    ``unfccc`` are the categories from unfccc_categories."""
    categories = party_versions(
        known_codes,
        prefix="PARIS",
        joined=PARIS_JOINED,
        left=PARIS_LEFT,
        title="Parties to the Paris Agreement",
        description="Parties to the Paris Agreement",
        instrument="Agreement",
    )

    parties = []
    for _, code, kind in party_changes(PARIS_JOINED, PARIS_LEFT):
        if kind == "joined":
            parties.append(code)
        else:
            parties.remove(code)
    categories["PARIS"] = {
        "title": "Parties to the Paris Agreement",
        "comment": "Parties to the Paris Agreement. Note that the 'PARIS' code will "
        "always refer to the current parties, use the PARIS_YYYY_MM or PARIS_YYYY "
        "codes for past months or years if you need a stable code.",
        "children": [sorted(parties)],
    }

    assert set(parties) == set(categories["PARIS_2026_01"]["children"][0])
    # all parties to the UNFCCC except the non-parties to the Paris Agreement
    assert set(parties) == set(unfccc["UNFCCC"]["children"][0]) - {
        "IRN",
        "LBY",
        "YEM",
        "USA",
    }

    return categories


def party_changes(
    joined: list[tuple[str, datetime.date, str]],
    left: list[tuple[str, datetime.date, str]],
) -> list[tuple[datetime.date, str, str]]:
    """All changes of the parties to a treaty as (date, code, kind), sorted by date.

    Only changes which took effect up to LAST_UPDATE are included.
    """
    return sorted(
        [(date, code, "joined") for code, date, _ in joined if date <= LAST_UPDATE]
        + [(date, code, "left") for code, date, _ in left if date <= LAST_UPDATE]
    )


def party_versions(
    known_codes: set[str],
    *,
    prefix: str,
    joined: list[tuple[str, datetime.date, str]],
    left: list[tuple[str, datetime.date, str]],
    title: str,
    description: str,
    instrument: str,
):
    """The parties to a treaty over time. All parties have to be in ``known_codes``.

    ``title`` and ``description`` describe the parties in the title and comment of the
    categories, like "Parties to the UNFCCC", and are followed by the validity.

    For every month in which parties joined or left, there is a category
    {prefix}_YYYY_MM containing the parties after all changes in that month took
    effect. The last category of every year additionally has the code {prefix}_YYYY.
    Only changes which took effect up to LAST_UPDATE are included, and codes for the
    month and year of LAST_UPDATE are left out because further changes could still take
    effect in them, so that all codes are stable.
    """
    months = [
        (month, list(month_changes))
        for month, month_changes in itertools.groupby(
            party_changes(joined, left),
            key=lambda change: (change[0].year, change[0].month),
        )
    ]

    categories = {}
    parties = []
    for i, ((year, month), month_changes) in enumerate(months):
        for _, code, kind in month_changes:
            assert code in known_codes, code
            if kind == "joined":
                assert code not in parties, code
                parties.append(code)
            else:
                assert code in parties, code
                parties.remove(code)

        if (year, month) >= (LAST_UPDATE.year, LAST_UPDATE.month):
            continue

        start = month_changes[-1][0]
        if i + 1 < len(months):
            next_month_changes = months[i + 1][1]
            end = next_month_changes[0][0] - datetime.timedelta(days=1)
            validity = f"from {start.isoformat()} to {end.isoformat()}"
        else:
            validity = f"since {start.isoformat()}"

        descriptions = []
        for kind in ("joined", "left"):
            changed = [
                f"{', '.join(code for _, code, _ in date_changes)} ({date.isoformat()})"
                for date, date_changes in itertools.groupby(
                    (change for change in month_changes if change[2] == kind),
                    key=lambda change: change[0],
                )
            ]
            if changed:
                descriptions.append(f"{kind}: {', '.join(changed)}")
        comment = (
            f"{description} {validity}. "
            f"Changes in {year}-{month:02}, {'; '.join(descriptions)}."
        )
        if i == 0:
            entry_into_force = month_changes[0][0]
            comment += (
                f" The {instrument} entered into force on "
                f"{entry_into_force.isoformat()}."
            )
        if len({date for date, _, _ in month_changes}) > 1:
            comment += (
                " The category contains the parties after all changes in "
                f"{year}-{month:02} took effect."
            )

        spec = {
            "title": f"{title} {validity}",
            "comment": comment,
            "children": [parties.copy()],
        }
        is_last_of_year = i + 1 == len(months) or months[i + 1][0][0] != year
        if is_last_of_year and year < LAST_UPDATE.year:
            spec["alternative_codes"] = [f"{prefix}_{year}"]
        categories[f"{prefix}_{year}_{month:02}"] = spec

    return categories


def eu_categories() -> dict[str, dict]:
    categories = {}
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


def load_countries() -> dict[str, str | dict[str, str] | list[str] | list[list[str]]]:
    """Load countries from the iso-codes debian package."""
    r = requests.get(
        URL,
        headers={"Accept": "application/json"},
    )

    categories: dict[str, str | dict[str, str]] = {}
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
    write_option_family(*main(), DATA_DIR)
