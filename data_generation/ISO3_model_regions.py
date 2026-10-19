"""The ``AR5``, ``RCP``, and ``EDGAR_HYDE`` options of ISO3, adding the regions of the
IPCC Fifth Assessment Report, the Representative Concentration Pathways, and the
EDGAR-HYDE historical emissions data set.

This is not run directly, the options are generated as part of ISO3 by
`make climate_categories/data/ISO3.py` in the main directory.

The region definitions are transcribed from the primary sources. Countries which
dissolved since the source was published are replaced by their successors, unless the
source lists the successors separately. The Netherlands Antilles are always given by
Curaçao (CUW), Sint Maarten (SXM), and Bonaire, Sint Eustatius and Saba (BES), so that
the Antilles option can merge them into ANT.
"""

import datetime

import climate_categories

TERRITORIES_COMMENT = (
    "Dependent territories are in the region of their location, which is not "
    "always the region of their sovereign country. If they are merged into their "
    "sovereign country, for example with the option "
    "territories_in_sovereign_inventory, they are not part of any region of this "
    "option, and their sovereign country stays in its own region."
)

# IPCC AR5 WGIII Annex II, section A.II.2.1. The source also lists the Channel Islands
# (given by GGY and JEY, which it lists as well), Serbia and Montenegro (given by SRB
# and MNE), and the Netherlands Antilles next to Curaçao and Sint Maarten (given by BES).
AR5_RC10 = {
    "NAM": ("North America", "CAN GUM SPM USA"),
    "WEU": (
        "Western Europe",
        (
            "ALA AND AUT BEL CHE DEU DNK ESP FIN FRA FRO GBR GGY GIB GRC GRL IMN IRL ISL "
            "ITA JEY LIE LUX MCO NLD NOR PRT SJM SMR SWE TUR VAT"
        ),
    ),
    "POECD": ("Pacific OECD", "AUS JPN NZL"),
    "EIT": (
        "Economies in Transition",
        (
            "ALB ARM AZE BGR BIH BLR CYP CZE EST GEO HRV HUN KAZ KGZ LTU LVA MDA MKD MLT "
            "MNE POL ROU RUS SRB SVK SVN TJK TKM UKR UZB"
        ),
    ),
    "LAM": (
        "Latin America and Caribbean",
        (
            "ABW AIA ARG ATA ATF ATG BES BHS BLZ BMU BOL BRA BRB BVT CHL COL CRI CUB CUW "
            "CYM DMA DOM ECU FLK GLP GRD GTM GUF GUY HND HTI JAM KNA LCA MEX MSR MTQ NIC "
            "PAN PER PRI PRY SGS SLV SUR SXM TCA TTO URY VCT VEN VGB VIR"
        ),
    ),
    "SSA": (
        "Sub-Saharan Africa",
        (
            "AGO BDI BEN BFA BWA CAF CIV CMR COD COG COM CPV DJI ERI ETH GAB GHA GIN GMB "
            "GNB GNQ KEN LBR LSO MDG MLI MOZ MRT MUS MWI MYT NAM NER NGA REU RWA SEN SHN "
            "SLE SOM STP SWZ SYC TCD TGO TZA UGA ZAF ZMB ZWE"
        ),
    ),
    "MNA": (
        "Middle East and North Africa",
        (
            "ARE BHR DZA EGY ESH IRN IRQ ISR JOR KWT LBN LBY MAR OMN PSE QAT SAU SDN SSD "
            "SYR TUN YEM"
        ),
    ),
    "EAS": ("East Asia", "CHN KOR MNG PRK"),
    "SAS": ("South Asia", "AFG BGD BTN IND IOT LKA MDV NPL PAK"),
    "PAS": (
        "South-East Asia and Pacific",
        (
            "ASM BRN CCK COK CXR FJI FSM HMD IDN KHM KIR LAO MHL MMR MNP MYS NCL NFK NIU "
            "NRU PCN PHL PLW PNG PYF SGP SLB THA TKL TLS TON TUV UMI VNM VUT WLF WSM"
        ),
    ),
}

# Table A.II.8: the RC5 regions EIT and LAM are the RC10 regions of the same name.
AR5_RC5 = {
    "OECD-1990": ("OECD Countries in 1990", ("NAM", "WEU", "POECD")),
    "MAF": ("Middle East and Africa", ("SSA", "MNA")),
    "ASIA": ("Non-OECD Asia", ("EAS", "SAS", "PAS")),
}

# RCP Database (version 2.0), region definitions. The source lists Yugoslavia next to
# its other successors (given by SRB and MNE), the Netherlands Antilles (given by BES,
# CUW, and SXM), and Sudan before the independence of South Sudan (given by SDN and
# SSD).
RCP_R10 = {
    "R10NAM": ("Northern America", "CAN USA"),
    "R10WEU": (
        "Western Europe",
        "AUT BEL CHE DEU DNK ESP FIN FRA GBR GRC IRL ISL ITA LUX NLD NOR PRT SWE TUR",
    ),
    "R10PAO": ("Pacific OECD", "AUS FJI GUM JPN NCL NZL PYF SLB VUT WSM"),
    "R10REF": (
        "Reforming Economies",
        (
            "ALB ARM AZE BGR BIH BLR CYP CZE EST GEO HRV HUN KAZ KGZ LTU LVA MDA MKD MLT "
            "MNE POL ROU RUS SRB SVK SVN TJK TKM UKR UZB"
        ),
    ),
    "R10CHN": ("China +", "CHN HKG MAC MNG TWN"),
    "R10IND": ("India +", "AFG BGD BTN IND LKA MDV NPL PAK"),
    "R10ROA": (
        "Rest of Asia",
        "BRN IDN KHM KOR LAO MMR MYS PHL PNG PRK SGP THA TLS VNM",
    ),
    "R10AFR": (
        "Africa",
        (
            "AGO BDI BEN BFA BWA CAF CIV CMR COD COG COM CPV DJI DZA EGY ERI ESH ETH GAB "
            "GHA GIN GMB GNB GNQ KEN LBR LBY LSO MAR MDG MLI MOZ MRT MUS MWI NAM NER NGA "
            "REU RWA SDN SEN SLE SOM SSD SWZ TCD TGO TUN TZA UGA ZAF ZMB ZWE"
        ),
    ),
    "R10MES": (
        "Middle East",
        "ARE BHR IRN IRQ ISR JOR KWT LBN OMN QAT SAU SYR YEM",
    ),
    "R10LAM": (
        "Latin America",
        (
            "ARG BES BHS BLZ BOL BRA BRB CHL COL CRI CUB CUW DOM ECU GLP GTM GUY HND HTI "
            "JAM MEX MTQ NIC PAN PER PRI PRY SLV SUR SXM TTO URY VEN"
        ),
    ),
}

RCP_R5 = {
    "OECD90": ("OECD 90", ("R10NAM", "R10WEU", "R10PAO")),
    "REF": ("Reforming Economies", ("R10REF",)),
    "ASIA": ("Asia", ("R10CHN", "R10IND", "R10ROA")),
    "MAF": ("Middle East and Africa", ("R10AFR", "R10MES")),
    "LAM": ("Latin America", ("R10LAM",)),
}

# The 13 regions of EDGAR 2.0 (Olivier et al. 1996, appendix 1, table R.1.1), which
# EDGAR-HYDE uses. The source gives the countries of 1996: Czechoslovakia (given by CZE
# and SVK), Yugoslavia (BIH, HRV, MKD, MNE, SRB, SVN), the USSR (its 15 successors),
# the German Democratic Republic (part of DEU, which is listed as well), the
# Iraq-Saudi Arabia Neutral Zone (divided between IRQ and SAU, which are listed as
# well), Zaire (COD), East Timor (TLS), Ethiopia including Eritrea (ETH and ERI), Sudan
# including South Sudan (SDN and SSD), and the Netherlands Antilles (BES, CUW, SXM).
# Its further regions "Sea (oceans)" and "Antarctica" (ATA) are not part of EDGAR-HYDE.
EDGAR_HYDE_REGIONS = {
    "Canada": "CAN",
    "USA": "USA",
    "Latin America": (
        "ABW AIA ARG ATG BES BHS BLZ BOL BRA BRB BVT CHL COL CRI CUB CUW CYM DMA DOM "
        "ECU FLK GLP GRD GTM GUF GUY HND HTI JAM KNA LCA MEX MSR MTQ NIC PAN PER PRI "
        "PRY SLV SUR SXM TCA TTO URY VCT VEN VIR"
    ),
    "Africa": (
        "AGO BDI BEN BFA BWA CAF CIV CMR COD COG COM CPV DJI DZA EGY ERI ESH ETH GAB "
        "GHA GIN GMB GNB GNQ IOT KEN LBR LBY LSO MAR MDG MLI MOZ MRT MUS MWI NAM NER "
        "NGA REU RWA SDN SEN SHN SLE SOM SSD STP SWZ SYC TCD TGO TUN TZA UGA ZAF ZMB "
        "ZWE"
    ),
    "OECD Europe": (
        "AND AUT BEL CHE DEU DNK ESP FIN FRA FRO GBR GIB GRC GRL IRL ISL ITA LIE LUX "
        "MCO MLT NLD NOR PRT SJM SMR SWE VAT"
    ),
    "Eastern Europe": "ALB BGR BIH CZE HRV HUN MKD MNE POL ROU SRB SVK SVN",
    "CIS": "ARM AZE BLR EST GEO KAZ KGZ LTU LVA MDA RUS TJK TKM UKR UZB",
    "Middle East": "AFG ARE BHR CYP IRN IRQ ISR JOR KWT LBN OMN QAT SAU SYR TUR YEM",
    "India Region": "BGD BTN IND LKA MDV MMR NPL PAK",
    "China Region": "CHN HKG KHM LAO MAC MNG PRK TWN VNM",
    "East Asia": "BRN IDN KOR MYS PHL PNG SGP THA TLS",
    "Oceania": (
        "ASM AUS CCK COK CXR FJI FSM GUM HMD KIR MHL MNP NCL NFK NIU NRU NZL PCN PLW "
        "PYF SLB TKL TON TUV VUT WLF WSM"
    ),
    "Japan": "JPN",
}

# The codes primap1, which produced PRIMAP-hist up to v2.x, used for these regions in
# its input data.
PRIMAP1_INPUT_CODES = {
    "RC10NAM": "AR5|NAM",
    "RC10WEU": "AR5|WEU",
    "RC10POECD": "AR5|POECD",
    "RC10EIT": "AR5|EIT",
    "RC10LAM": "AR5|LAM",
    "RC10SSA": "AR5|SSA",
    "RC10MNA": "AR5|MNA",
    "RC10EAS": "AR5|EAS",
    "RC10SAS": "AR5|SAS",
    "RC10PAS": "AR5|PAS",
    "R5OECD": "RCP|OECD90",
    "R5REF": "RCP|REF",
    "R5ASIA": "RCP|ASIA",
    "R5MAF": "RCP|MAF",
    "R5LAM": "RCP|LAM",
    "LATINAMER2": "EDGAR-HYDE|Latin America",
    "AFR": "EDGAR-HYDE|Africa",
    "WEUR2": "EDGAR-HYDE|OECD Europe",
    "EEUR": "EDGAR-HYDE|Eastern Europe",
    # the USSR in all input data, including EDGAR-HYDE, see primap1_inputs_option
    "FSU": "SUN",
    "MEAST3": "EDGAR-HYDE|Middle East",
    "INDSSA": "EDGAR-HYDE|India Region",
    "CHNCP": "EDGAR-HYDE|China Region",
    "EAS": "EDGAR-HYDE|East Asia",
    "OCE": "EDGAR-HYDE|Oceania",
}


def countries(codes: str) -> list[list[str]]:
    members = codes.split()
    if len(members) != len(set(members)):
        raise ValueError(f"duplicate members in {codes!r}")
    return [sorted(members)]


def ar5_option(last_update: datetime.date) -> climate_categories.CategorizationOption:
    categories = {}
    for region, (title, codes) in AR5_RC10.items():
        in_rc5 = " and RC5" if region in ("EIT", "LAM") else ""
        categories[f"AR5|{region}"] = {
            "title": f"{title} (IPCC AR5 RC10{in_rc5})",
            "comment": f"Region {region} of the RC10{in_rc5} region set of the IPCC "
            "Fifth Assessment Report, Working Group III.",
            "children": countries(codes),
        }
    for region, (title, rc10) in AR5_RC5.items():
        categories[f"AR5|{region}"] = {
            "title": f"{title} (IPCC AR5 RC5)",
            "comment": f"Region {region} of the RC5 region set of the IPCC Fifth "
            "Assessment Report, Working Group III, made up of the RC10 regions "
            f"{', '.join(rc10)}.",
            "children": [[f"AR5|{r}" for r in rc10]],
        }

    return climate_categories.CategorizationOption(
        name="AR5",
        title="IPCC AR5 regions",
        comment="The regions of the RC5 and RC10 region sets of the IPCC Fifth "
        "Assessment Report, Working Group III, with codes like AR5|NAM. The RC5 regions "
        "EIT and LAM are identical to the RC10 regions of the same name, the other RC5 "
        "regions have the RC10 regions as children. The source does not assign "
        "Taiwan (TWN), Hong Kong (HKG), Macao (MAC), Saint Barthélemy (BLM), and Saint "
        f"Martin (MAF) to any region. {TERRITORIES_COMMENT}",
        references="IPCC (2014), Annex II: Metrics & Methodology, section A.II.2, in: "
        "Climate Change 2014: Mitigation of Climate Change, "
        "https://www.ipcc.ch/site/assets/uploads/2018/02/ipcc_wg3_ar5_annex-ii.pdf",
        last_update=last_update,
        add_categories=categories,
    )


def rcp_option(last_update: datetime.date) -> climate_categories.CategorizationOption:
    categories = {}
    for region, (title, codes) in RCP_R10.items():
        categories[f"RCP|{region}"] = {
            "title": f"{title} (RCP, 10 regions)",
            "comment": f"Region {region} of the 10-region aggregation of the RCP "
            "Database.",
            "children": countries(codes),
        }
    for region, (title, r10) in RCP_R5.items():
        categories[f"RCP|{region}"] = {
            "title": f"{title} (RCP, 5 regions)",
            "comment": f"Region {region} of the 5-region aggregation of the RCP "
            f"Database, made up of the regions {', '.join(r10)}.",
            "children": [[f"RCP|{r}" for r in r10]],
        }

    return climate_categories.CategorizationOption(
        name="RCP",
        title="RCP regions",
        comment="The regions of the Representative Concentration Pathways (RCPs) in "
        "the RCP Database, with codes like RCP|OECD90 for the 5 regions and "
        "RCP|R10NAM for the 10 regions. The 5 regions have the 10 regions as "
        "children. The source only assigns 188 countries to regions, many small "
        "countries and territories are not part of any region, for example Antigua "
        f"and Barbuda (ATG), Kiribati (KIR), and Andorra (AND). {TERRITORIES_COMMENT}",
        references="RCP Database (version 2.0), region definitions, "
        "https://tntcat.iiasa.ac.at/RcpDb/dsd?Action=htmlpage&page=about",
        last_update=last_update,
        add_categories=categories,
    )


def edgar_hyde_option(
    last_update: datetime.date,
) -> climate_categories.CategorizationOption:
    categories = {
        f"EDGAR-HYDE|{region}": {
            "title": f"{region} (EDGAR-HYDE)",
            "comment": f"Region {region!r} of EDGAR 2.0 and EDGAR-HYDE.",
            "children": countries(codes),
        }
        for region, codes in EDGAR_HYDE_REGIONS.items()
    }

    return climate_categories.CategorizationOption(
        name="EDGAR_HYDE",
        title="EDGAR-HYDE regions",
        comment="The 13 regions of the EDGAR-HYDE historical emissions data set, which "
        "are the regions of EDGAR 2.0, with codes like EDGAR-HYDE|Africa. The regions "
        "Canada, USA, and Japan only contain the country of the same name. The source "
        "does not assign Bermuda (BMU), the British Virgin Islands (VGB), Mayotte "
        "(MYT), Palestine (PSE), and some other territories to any region. "
        f"{TERRITORIES_COMMENT}",
        references="Van Aardenne et al. (2001), A 1°x1° resolution data set of "
        "historical anthropogenic trace gas emissions for the period 1890-1990, "
        "https://doi.org/10.1029/2000GB001265;\n"
        "Olivier et al. (1996), Description of EDGAR Version 2.0, RIVM report "
        "771060002, appendix 1, table R.1.1, "
        "https://www.rivm.nl/bibliotheek/rapporten/771060002.pdf",
        last_update=last_update,
        add_categories=categories,
    )


def primap1_inputs_option(
    last_update: datetime.date,
) -> climate_categories.CategorizationOption:
    return climate_categories.CategorizationOption(
        name="PRIMAP1_inputs",
        title="PRIMAP-hist up to v2.x, input data",
        comment="The codes which primap1, which produced PRIMAP-hist up to v2.x, used "
        "in its input data, as alternative codes. Currently the codes of the regions "
        "of the IPCC Fifth Assessment Report (RC10*), the RCP database (R5*), and "
        "EDGAR-HYDE. primap1 used FSU for the USSR (SUN) in all input data, so the "
        "CIS region of EDGAR-HYDE, which consists of the same 15 republics, is "
        "included in SUN.",
        references="PRIMAP-hist v2.8 input data, "
        "https://github.com/primap-community/PRIMAP-hist_data",
        last_update=last_update,
        requires=("AR5", "EDGAR_HYDE", "PRIMAP1", "RCP"),
        add_alternative_codes=PRIMAP1_INPUT_CODES,
        merge_into={"EDGAR-HYDE|CIS": "SUN"},
    )
