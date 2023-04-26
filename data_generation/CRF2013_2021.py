"""Run this via `make climate_categories/data/CRF2013_2021.yaml` in the main
directory."""

import pathlib

import climate_categories

OUTPATH = pathlib.Path("./climate_categories/data/CRF2013_2021.yaml")


def main():
    """Create the CRF2013_2021 categorization from the CRF2013 categorization.
    No categories are removed. Several country specific categories are added.
    Where different countries have added equivalent categories these have
    been grouped into one category.

    TODO: Currently country specific categories for some tables are not included.
    Affected tables are LULUCF detail tables, detail tables in the industrial
    sectors (tables with country specific items not read) and some agricultural
    subsectors (3.F-I)

    """
    spec = climate_categories.CRF2013.to_spec()

    # Metadata
    spec["name"] = "CRF2013_2021"
    spec["title"] = (
        "Common Reporting Format GHG emissions categories (2013). "
        "Extended for 2021 CRF submissions."
    )
    spec["comment"] = (
        "Classification of green-house gas emissions and removals into categories "
        "for use in annual inventories using the Common Reporting Format as "
        "specified in the UNFCCC guidelines on reporting and review as decided "
        "in the ninetenth session of the Conference of the Parties in 2013. "
        "This specification extend the CRF2013 specification by country specific "
        "categories from the 2021 submissions."
    )
    spec["references"] = (
        "United Nations 2013, Decision 24/CP.19 - Revision of the UNFCCC reporting "
        "guidelines on annual inventories for Parties included in Annex I to the "
        "Convention. Documented in the 'Report of the Conference of the Parties on "
        "its nineteenth session, held in Warsaw from 11 to 23 November 2013' "
        "available at https://unfccc.int/resource/docs/2013/cop19/eng/10a03.pdf. "
        "https://unfccc.int/ghg-inventories-annex-i-parties/2021"
    )
    spec["institution"] = "UN"
    spec["last_update"] = "2021-04-12"
    spec["version"] = "2013-2021"
    spec["total_sum"] = True
    spec["canonical_top_level_category"] = "0"

    # Changes in categories
    cats = spec["categories"]
    ncats = {}

    # --------
    # go through the specifications table by table
    # --------

    # Table 1s1
    # nothing to add

    # Table 1.A(a)s1
    cats["1.A.1.a.iv"]["children"] = [
        [
            "1.A.1.a.iv.1",
            "1.A.1.a.iv.2",
            "1.A.1.a.iv.3",
            "1.A.1.a.iv.4",
        ]
    ]
    ncats["1.A.1.a.iv.1"] = {"title": "Methane Cogeneration (Mining)"}  # for SVK
    ncats["1.A.1.a.iv.2"] = {
        "title": "Municipal Solid Waste Incineration (Energy use)"
    }  # for SVK
    # name for CHE is "Municipal and special waste incineration plants"
    ncats["1.A.1.a.iv.3"] = {"title": "Other"}  # for ESP
    ncats["1.A.1.a.iv.4"] = {
        "title": "Total Public Electricity and Heat Production"
    }  # for AUT
    # name for DEU is "1.A.1.a Public Electricity and Heat Production"
    cats["1.A.1.c.ii"]["children"] = [["1.A.1.c.ii.1", "1.A.1.c.ii.2", "1.A.1.c.ii.3"]]
    ncats["1.A.1.c.ii.1"] = {"title": "Charcoal Production"}  # for CYP
    ncats["1.A.1.c.ii.2"] = {
        "title": "1.A.1.c Manufacture of Solid Fuels and Other Energy Industries"
    }  # for DEU
    ncats["1.A.1.c.ii.3"] = {"title": "Other"}  # for ESP

    # Table 1.A(a)s2
    # it is not completely clear what countries report under the custom subcategories
    # we have thus grouped them by similar names but kept a few different
    # categories even if they might have the same content and are never reported
    # together
    cats["1.A.2.g.viii"]["children"] = [
        [
            "1.A.2.g.viii.1",
            "1.A.2.g.viii.2",
            "1.A.2.g.viii.3",
            "1.A.2.g.viii.4",
            "1.A.2.g.viii.5",
            "1.A.2.g.viii.6",
            "1.A.2.g.viii.7",
            "1.A.2.g.viii.8",
            "1.A.2.g.viii.9",
            "1.A.2.g.viii.10",
        ]
    ]
    ncats["1.A.2.g.viii.1"] = {"title": "Non-specified Industry"}  # for SVK, CYP
    # for DNK, DKE, USA, CZE name is "Other non-specified"
    # for PRT, LTU name is "Non-specified industry"
    # for BEL name is "Other non specified"
    # for MCO name is "Undefined Industry"
    # for TUR name is "Other unspecified"
    ncats["1.A.2.g.viii.2"] = {
        "title": "Manufacture and construction Aggregated"
    }  # for BLR
    # name for HRV: "1A2 Total for 1990 to 2000"
    # name for MAL: "All Industry"
    ncats["1.A.2.g.viii.3"] = {
        "title": "Other manufacturing industries"
    }  # for DNK, DKE, DNM, FIN
    # name for CAN: "Other Manufacturing"
    # name for AUS: "All Other Manufacturing"
    # name for NOR: "Other manufacturing"
    # name for AUT, LUX: "Other Manufacturing Industries"
    ncats["1.A.2.g.viii.4"] = {"title": "Other Industrial Sectors"}  # NLD
    # for RUS name is: "Other Industries"
    # for HRV name is: "Other Industry:
    # for GBR, GBK name is "Other industry (not specified above)"
    # for UKR name is "Oter Industries"
    ncats["1.A.2.g.viii.5"] = {"title": "Non-CO2 emissions from BFG combustion"}  # RUS
    ncats["1.A.2.g.viii.6"] = {"title": "Rubber"}  # PRT
    ncats["1.A.2.g.viii.7"] = {
        "title": "All stationary combustin within CRF 1.A.2.g"
    }  # SWE
    ncats["1.A.2.g.viii.8"] = {"title": "Other stationary combustion"}  # IRL
    # for HUN name is "Other Stationary Combustion"
    ncats["1.A.2.g.viii.9"] = {"title": "Other Boilers and Engines Industry"}  # CHE
    ncats["1.A.2.g.viii.10"] = {
        "title": "Other"
    }  # for BLR, DNK, ESP, LVA, NZL, POL, ROU, SVN,

    # Table 1.A(a)s3
    cats["1.A.3.b.v"]["children"] = [
        [
            "1.A.3.b.v.1",
            "1.A.3.b.v.2",
            "1.A.3.b.v.3",
            "1.A.3.b.v.4",
            "1.A.3.b.v.5",
            "1.A.3.b.v.6",
            "1.A.3.b.v.7",
            "1.A.3.b.v.8",
            "1.A.3.b.v.9",
            "1.A.3.b.v.10",
            "1.A.3.b.v.11",
            "1.A.3.b.v.12",
            "1.A.3.b.v.13",
        ]
    ]
    ncats["1.A.3.b.v.1"] = {
        "title": "Road total"
    }  # TUR reports all road transport aggregated
    ncats["1.A.3.b.v.2"] = {"title": "Buses"}  # CYP
    ncats["1.A.3.b.v.3"] = {"title": "All vehicles - biofuel use"}  # GBR, GBK
    ncats["1.A.3.b.v.4"] = {"title": "All vehicles - LPG use"}  # GBR, GBK
    ncats["1.A.3.b.v.5"] = {
        "title": "All vehicles - biofuel use (fossil component)"
    }  # GBR, GBK
    ncats["1.A.3.b.v.6"] = {"title": "Propane and Natural Gas Vehicles"}  # CAN
    ncats["1.A.3.b.v.7"] = {"title": "Lubricant Two-Stroke Engines"}  # BEL
    ncats["1.A.3.b.v.8"] = {"title": "Gaseous Fuels"}  # ROU
    ncats["1.A.3.b.v.9"] = {"title": "Other Liquid Fuels"}  # ROU
    ncats["1.A.3.b.v.10"] = {"title": "Biomass"}  # ROU
    ncats["1.A.3.b.v.11"] = {"title": "Evaporative Emissions"}  # USA
    ncats["1.A.3.b.v.12"] = {"title": "Urea-Based Catalysts"}  # SVK
    ncats["1.A.3.b.v.13"] = {"title": "Other non-specified"}  # ESP

    cats["1.A.3.e.ii"]["children"] = [
        ["1.A.3.e.ii.1", "1.A.3.e.ii.2", "1.A.3.e.ii.3", "1.A.3.e.ii.4"]
    ]
    ncats["1.A.3.e.ii.1"] = {"title": "Off-road vehicles and other machinery"}  # UKR
    # for CAN name is "Off Road"
    # for AUS name is "Off-Road Vehicles"
    ncats["1.A.3.e.ii.2"] = {"title": "Aircraft support vehicles"}  # GBR, GBK
    ncats["1.A.3.e.ii.3"] = {"title": "Other non-specified"}  # BEL
    ncats["1.A.3.e.ii.4"] = {"title": "Non-Transportation Mobile"}  # USA

    # Table 1.A(a)s4
    cats["1.A.4.b.iii"]["children"] = [["1.A.4.b.iii.1"]]
    ncats["1.A.4.b.iii.1"] = {"title": "Residential"}  # CYP

    cats["1.A.5.a"]["children"] = [
        [
            "1.A.5.a.i",
            "1.A.5.a.ii",
            "1.A.5.a.iii",
            "1.A.5.a.iv",
            "1.A.5.a.v",
        ]
    ]
    ncats["1.A.5.a.i"] = {"title": "Military Fuel Use"}  # GBK, GBR
    # name for NOR, HUN is "Military"
    ncats["1.A.5.a.ii"] = {"title": "Other non-specified"}  # ESP
    # name for ROU is "Other"
    # name for FRA, FRK is "Other not specified"
    # name for CYP is "Other (not specified elsewhere)
    # name for DNM, DNK, DKE is "Other stationary combustion"
    # name for LUX is "Stationary"
    ncats["1.A.5.a.iii"] = {"title": "Non-Fuel Use"}  # NOR
    # name for USA is Non Energy Use
    ncats["1.A.5.a.iv"] = {"title": "Incineration of Waste"}  # USA
    ncats["1.A.5.a.v"] = {"title": "US Territories"}  # USA
    cats["1.A.5.b"]["children"] = [
        [
            "1.A.5.b.i",
            "1.A.5.b.ii",
            "1.A.5.b.iii",
            "1.A.5.b.iv",
            "1.A.5.b.v",
            "1.A.5.b.vi",
            "1.A.5.b.vii",
            "1.A.5.b.viii",
            "1.A.5.b.ix",
            "1.A.5.b.x",
            "1.A.5.b.xi",
            "1.A.5.b.xii",
            "1.A.5.b.xiii",
        ]
    ]
    ncats["1.A.5.b.i"] = {"title": "Military Aviation and Shipping"}  # GBK, GBR
    ncats["1.A.5.b.ii"] = {"title": "Military Aviation Component"}  # HRV
    # name for CAN is "Domestic Military (Aviation)"
    ncats["1.A.5.b.iii"] = {"title": "Military water-borne component"}  # HRV
    # name for CAN is "Military Water-borne Navigation"
    ncats["1.A.5.b.iv"] = {"title": "Other non-specified"}  # ESP
    # name for ROU, MLT is "Other"
    # name for FRA, FRK is "Other not specified"
    # name for CZE is "Other mobile sources not included elsewhere"
    # name for LUX is "Unspecified Mobile"
    # name for LVA is "Mobile"
    ncats["1.A.5.b.v"] = {"title": "Military Use"}  # NLD, BEL, UKR
    # name for AUT, NOR, HUN, LTU is "Military"
    # name ofr SVN is "Military use of fuels"
    ncats["1.A.5.b.vi"] = {"title": "Mobile (aviation component)"}  # CYP
    ncats["1.A.5.b.vii"] = {"title": "Lubricants used in 2-stroke engines"}  # NOR
    ncats["1.A.5.b.viii"] = {"title": "Recreational crafts"}  # DNM, DKE, DNK
    ncats["1.A.5.b.ix"] = {"title": "Military use Jet Kerosene"}  # SVK
    ncats["1.A.5.b.x"] = {"title": "Military Gasoline"}  # SVK
    ncats["1.A.5.b.xi"] = {"title": "Military Diesel Oil"}  # SVK
    ncats["1.A.5.b.xii"] = {"title": "Military Transport"}  # AUS
    ncats["1.A.5.b.xiii"] = {"title": "Agriculture and Forestry and Fishing"}  # CZE

    # Table 1.B.1
    cats["1.B.1.c"]["children"] = [
        ["1.B.1.c.i", "1.B.1.c.ii", "1.B.1.c.iii", "1.B.1.c.iv"]
    ]
    ncats["1.B.1.c.i"] = {"title": "Flaring"}  # UKR, AUS
    # name for SWE is "Flaring of gas"
    ncats["1.B.1.c.ii"] = {"title": "Coal Dumps"}  # JPN
    ncats["1.B.1.c.iii"] = {"title": "SO2 scrubbing"}  # SVN"
    ncats["1.B.1.c.iv"] = {"title": "Emission from Coke Oven Gas Subsystem"}  # POL
    # name for KAZ is "Flaring of coke oven gas"

    # Table 1.B.2
    cats["1.B.2.d"]["children"] = [
        [
            "1.B.2.d.i",
            "1.B.2.d.ii",
            "1.B.2.d.iii",
            "1.B.2.d.iv",
            "1.B.2.d.v",
            "1.B.2.d.vi",
            "1.B.2.d.vii",
            "1.B.2.d.viii",
            "1.B.2.d.ix",
            "1.B.2.d.x",
        ]
    ]
    ncats["1.B.2.d.i"] = {"title": "Groundwater Extraction and CO2 Mining"}  # HUN
    ncats["1.B.2.d.ii"] = {"title": "Geothermal"}  # NOR, DEU, PRT, NZL
    ncats["1.B.2.d.iii"] = {"title": "City Gas Production"}  # PRT
    ncats["1.B.2.d.iv"] = {"title": "Other"}  # UKR, ROU
    # name for SWE is "Other non-specified"
    ncats["1.B.2.d.v"] = {"title": "Flaring in Refineries"}  # ITA
    ncats["1.B.2.d.vi"] = {"title": "LPG Transport"}  # GRC
    ncats["1.B.2.d.vii"] = {"title": "Distribution of Town Gas"}  # FIN
    ncats["1.B.2.d.viii"] = {"title": "Petrol Distribution"}  # IRL
    ncats["1.B.2.d.ix"] = {"title": "Natural Gas Transport"}  # BLR
    ncats["1.B.2.d.x"] = {
        "title": "Natural Gas Exploration - N2O Emissions"
    }  # GBR, GBK

    # Table 3s1
    # option c for Australia
    # 3.A
    cats["3.A.1"]["children"].append(
        ["3.A.1.C-AUS-a", "3.A.1.C-AUS-b", "3.A.1.C-AUS-c"]
    )
    ncats["3.A.1.C-AUS-a"] = {"title": "Dairy Cattle"}
    ncats["3.A.1.C-AUS-b"] = {"title": "Beef Cattle - Pasture"}
    ncats["3.A.1.C-AUS-c"] = {"title": "Beef Cattle - Feedlot"}
    # 3.B
    cats["3.B.1"]["children"].append(
        ["3.B.1.C-AUS-a", "3.B.1.C-AUS-b", "3.B.1.C-AUS-c"]
    )
    ncats["3.B.1.C-AUS-a"] = {"title": "Dairy Cattle"}
    ncats["3.B.1.C-AUS-b"] = {"title": "Beef Cattle - Pasture"}
    ncats["3.B.1.C-AUS-c"] = {"title": "Beef Cattle - Feedlot"}
    # option c for Malta
    # 3.A
    cats["3.A.1"]["children"].append(
        [
            "3.A.1.C-MLT-a",
            "3.A.1.C-MLT-b",
            "3.A.1.C-MLT-c",
            "3.A.1.C-MLT-d",
            "3.A.1.C-MLT-e",
        ]
    )
    ncats["3.A.1.C-MLT-a"] = {"title": "dairy cows"}
    ncats["3.A.1.C-MLT-b"] = {"title": "non-lactating cows"}
    ncats["3.A.1.C-MLT-c"] = {"title": "bulls"}
    ncats["3.A.1.C-MLT-d"] = {"title": "calves"}
    ncats["3.A.1.C-MLT-e"] = {"title": "growing cattle 1-2 years"}
    # 3.B
    cats["3.B.1"]["children"].append(
        [
            "3.B.1.C-MLT-a",
            "3.B.1.C-MLT-b",
            "3.B.1.C-MLT-c",
            "3.B.1.C-MLT-d",
            "3.B.1.C-MLT-e",
        ]
    )
    ncats["3.B.1.C-MLT-a"] = {"title": "dairy cows"}
    ncats["3.B.1.C-MLT-b"] = {"title": "non-lactating cows"}
    ncats["3.B.1.C-MLT-c"] = {"title": "bulls"}
    ncats["3.B.1.C-MLT-d"] = {"title": "calves"}
    ncats["3.B.1.C-MLT-e"] = {"title": "growing cattle 1-2 years"}
    # option c for Luxembourg
    # 3.A
    cats["3.A.1"]["children"].append(
        [
            "3.A.1.C-LUX-a",
            "3.A.1.C-LUX-b",
            "3.A.1.C-LUX-c",
            "3.A.1.C-LUX-d",
            "3.A.1.C-LUX-e",
            "3.A.1.C-LUX-f",
        ]
    )
    ncats["3.A.1.C-LUX-a"] = {"title": "Bulls"}
    ncats["3.A.1.C-LUX-b"] = {"title": "Calves"}
    ncats["3.A.1.C-LUX-c"] = {"title": "Young Cattle"}
    ncats["3.A.1.C-LUX-d"] = {"title": "Suckler Cows"}
    ncats["3.A.1.C-LUX-e"] = {"title": "Bulls under 2 years"}
    ncats["3.A.1.C-LUX-f"] = {"title": "Dairy Cows"}
    # 3.B (order is different in table but the same here)
    cats["3.B.1"]["children"].append(
        [
            "3.B.1.C-LUX-a",
            "3.B.1.C-LUX-b",
            "3.B.1.C-LUX-c",
            "3.B.1.C-LUX-d",
            "3.B.1.C-LUX-e",
            "3.B.1.C-LUX-f",
        ]
    )
    ncats["3.B.1.C-LUX-a"] = {"title": "Bulls"}
    ncats["3.B.1.C-LUX-b"] = {"title": "Calves"}
    ncats["3.B.1.C-LUX-c"] = {"title": "Young Cattle"}
    ncats["3.B.1.C-LUX-d"] = {"title": "Suckler Cows"}
    ncats["3.B.1.C-LUX-e"] = {"title": "Bulls under 2 years"}
    ncats["3.B.1.C-LUX-f"] = {"title": "Dairy Cows"}
    # option c for Poland
    # 3.A
    cats["3.A.1"]["children"].append(
        [
            "3.A.1.C-POL-a",
            "3.A.1.C-POL-b",
            "3.A.1.C-POL-c",
            "3.A.1.C-POL-d",
            "3.A.1.C-POL-e",
        ]
    )
    ncats["3.A.1.C-POL-a"] = {"title": "Bulls (older than 2 years)"}
    ncats["3.A.1.C-POL-b"] = {"title": "Non-dairy Heifers (older than 2 years)"}
    ncats["3.A.1.C-POL-c"] = {"title": "Non-dairy Young Cattle (younger than 1 year)"}
    ncats["3.A.1.C-POL-d"] = {"title": "Dairy Cattle"}
    ncats["3.A.1.C-POL-e"] = {"title": "Non-dairy Young Cattle (1-2 years)"}
    # 3.B
    cats["3.B.1"]["children"].append(["3.B.1.C-POL-a", "3.B.1.C-POL-b"])
    ncats["3.B.1.C-POL-a"] = {"title": "non-dairy Cattle"}
    ncats["3.B.1.C-POL-b"] = {"title": "Dairy Cattle"}
    # option c for Slovenia
    # 3.A
    cats["3.A.1"]["children"].append(
        ["3.A.1.C-SVN-a", "3.A.1.C-SVN-b", "3.A.1.C-SVN-c"]
    )
    ncats["3.A.1.C-SVN-a"] = {"title": "Dairy cows"}
    ncats["3.A.1.C-SVN-b"] = {"title": "Non-dairy cattle"}
    ncats["3.A.1.C-SVN-c"] = {"title": "Other cows"}
    # 3.B
    cats["3.B.1"]["children"].append(
        ["3.B.1.C-SVN-a", "3.B.1.C-SVN-b", "3.B.1.C-SVN-c"]
    )
    ncats["3.B.1.C-SVN-a"] = {"title": "Dairy cows"}
    ncats["3.B.1.C-SVN-b"] = {"title": "Non-dairy cattle"}
    ncats["3.B.1.C-SVN-c"] = {"title": "Other cows"}
    # option c for USA
    # 3.A
    cats["3.A.1"]["children"].append(
        [
            "3.A.1.C-USA-a",
            "3.A.1.C-USA-b",
            "3.A.1.C-USA-c",
            "3.A.1.C-USA-d",
            "3.A.1.C-USA-e",
            "3.A.1.C-USA-f",
            "3.A.1.C-USA-g",
            "3.A.1.C-USA-h",
            "3.A.1.C-USA-i",
            "3.A.1.C-USA-j",
            "3.A.1.C-USA-k",
        ]
    )
    ncats["3.A.1.C-USA-a"] = {"title": "Steer Stocker"}
    ncats["3.A.1.C-USA-b"] = {"title": "Heifer Stocker"}
    ncats["3.A.1.C-USA-c"] = {"title": "Beef Cows"}
    ncats["3.A.1.C-USA-d"] = {"title": "Dairy Replacements"}
    ncats["3.A.1.C-USA-e"] = {"title": "Beef Replacements"}
    ncats["3.A.1.C-USA-f"] = {"title": "Steer Feedlot"}
    ncats["3.A.1.C-USA-g"] = {"title": "Heifer Feedlot"}
    ncats["3.A.1.C-USA-h"] = {"title": "Bulls"}
    ncats["3.A.1.C-USA-i"] = {"title": "Dairy Cows"}
    ncats["3.A.1.C-USA-j"] = {"title": "Beef Calves"}
    ncats["3.A.1.C-USA-k"] = {"title": "Dairy Calves"}
    # 3.B (two extra but unused categories)
    cats["3.B.1"]["children"].append(
        [
            "3.B.1.C-USA-a",
            "3.B.1.C-USA-b",
            "3.B.1.C-USA-c",
            "3.B.1.C-USA-d",
            "3.B.1.C-USA-e",
            "3.B.1.C-USA-f",
            "3.B.1.C-USA-g",
            "3.B.1.C-USA-h",
            "3.B.1.C-USA-i",
            "3.B.1.C-USA-j",
            "3.B.1.C-USA-k",
            "3.B.1.C-USA-l",
            "3.B.1.C-USA-m",
        ]
    )
    ncats["3.B.1.C-USA-a"] = {"title": "Steer Stocker"}
    ncats["3.B.1.C-USA-b"] = {"title": "Heifer Stocker"}
    ncats["3.B.1.C-USA-c"] = {"title": "Beef Cows"}
    ncats["3.B.1.C-USA-d"] = {"title": "Dairy Replacements"}
    ncats["3.B.1.C-USA-e"] = {"title": "Beef Replacements"}
    ncats["3.B.1.C-USA-f"] = {"title": "Steer Feedlot"}
    ncats["3.B.1.C-USA-g"] = {"title": "Heifer Feedlot"}
    ncats["3.B.1.C-USA-h"] = {"title": "Bulls"}
    ncats["3.B.1.C-USA-i"] = {"title": "Dairy Cows"}
    ncats["3.B.1.C-USA-j"] = {"title": "Beef Calves"}
    ncats["3.B.1.C-USA-k"] = {"title": "Dairy Calves"}
    ncats["3.B.1.C-USA-l"] = {"title": "Dairy Cattle"}
    ncats["3.B.1.C-USA-m"] = {"title": "Non-Dairy Cattle"}

    # Table 3s2
    # Denmark, Austria, Sweden, Ireland - NOX from Manure management
    # name for Austria is "NOX emissions from manure management"
    # name for Denmark is "NOx from 3B"
    # name for Sweden is "NOx from manure management"
    # name for Ireland is "NOx from Manure Management"
    # name for germany is "3.B NOx Emissions"
    cats["3.J"]["children"] = [["3.J.1"]]
    ncats["3.J.1"] = {"title": "NOx from Manure Management"}
    # CZE, LVA, EST - other in other
    # name for CZE, LVA is "Other"
    # name for EST is "Other non-specified"
    # name for UK is "Other UK emissions"
    cats["3.J"]["children"][0].append("3.J.2")
    ncats["3.J.2"] = {"title": "Other"}
    # UK other categories
    cats["3.J"]["children"][0].append("3.J.3")
    ncats["3.J.3"] = {"title": "OTs and CDs - Livestock"}
    cats["3.J"]["children"][0].append("3.J.4")
    ncats["3.J.4"] = {"title": "OTs and CDs - soils"}
    cats["3.J"]["children"][0].append("3.J.5")
    ncats["3.J.5"] = {"title": "OTs and CDs - other"}
    # Germany other categories
    cats["3.J"]["children"][0].append("3.J.6")
    ncats["3.J.6"] = {"title": "Digestate renewable raw material (storage of N)"}
    cats["3.J"]["children"][0].append("3.J.7")
    ncats["3.J.7"] = {
        "title": "Digestate renewable raw material (atmospheric deposition)"
    }
    cats["3.J"]["children"][0].append("3.J.8")
    ncats["3.J.8"] = {
        "title": "Digestate renewable raw material (storage of dry matter)"
    }
    # Norway - NOx from Livestock
    cats["3.J"]["children"][0].append("3.J.9")
    ncats["3.J.9"] = {"title": "NOx from Livestock"}

    # Table 3.C
    cats["3.C.1.b"]["children"] = [["3.C.1.b.i", "3.C.1.b.ii"]]
    ncats["3.C.1.b.i"] = {"title": "Intermittently flooded Single aeration"}
    ncats["3.C.1.b.ii"] = {"title": "Intermittently flooded Multiple aeration"}
    cats["3.C.4"]["children"] = [["3.C.4.a"]]
    ncats["3.C.4.a"] = {"title": "Other Non-Specified"}
    # name for EST is "Non-specified"
    # name for DEU is "Other"
    # name for LVA is "other"
    # name for CZE is "Other cultivation"

    # Table 3.E
    cats["3.E.1"]["children"] = [["3.E.1.a", "3.E.1.b", "3.E.1.c", "3.E.1.d"]]
    ncats["3.E.1.a"] = {"title": "Savanna Woodland"}  # AUS
    # name for SWE, CHE, CZE, HRV is "Forest land"
    # name for MLT is "forest land"
    ncats["3.E.1.b"] = {"title": "Savanna Grassland"}  # AUS
    ncats["3.E.1.c"] = {"title": "Luxembourg"}  # LUX
    ncats["3.E.1.d"] = {"title": "Other non-specified"}  # EST
    # name for DNK, DKE, DNM is "All"
    # name for DEU is "Unspecified"
    # name for LVA is "Zone"
    cats["3.E.2"]["children"] = [
        ["3.E.2.a", "3.E.2.b", "3.E.2.c", "3.E.2.d", "3.E.2.e", "3.E.2.f", "3.E.2.g"]
    ]
    ncats["3.E.2.a"] = {"title": "Savanna Woodland"}  # AUS
    ncats["3.E.2.b"] = {"title": "Savanna Grassland"}  # AUS
    ncats["3.E.2.c"] = {"title": "Temperate Grassland"}  # AUS
    ncats["3.E.2.d"] = {"title": "Grassland"}  # SWE, CHE, CZE, HRV
    # name for MLT is "grassland"
    ncats["3.E.2.e"] = {"title": "Luxembourg"}  # LUX
    ncats["3.E.2.f"] = {"title": "Other non-specified"}  # EST
    # name for DNK, DKE, DNM is "All
    # name for DEU is "Unspecified"
    # name for LVA is "Zone_"
    ncats["3.E.2.g"] = {"title": "Tussock"}  # NZL

    # Table 4

    # entries under H. Other
    cats["4.H"]["children"] = [[f"4.H.{i}" for i in range(1, 10)]]
    # some of the subcategories refer to categories already included above
    # but are used to report non-CO2 emissions
    ncats["4.H.1"] = {"title": "Land converted to Settlement"}  # JPN
    ncats["4.H.2"] = {"title": "Settlements Remaining Settlement"}  # USA, DEU, GBR
    # name for DEU is "Settlements"
    # name for GBR is "4.E Settlements"
    ncats["4.H.3"] = {"title": "4.C Grassland"}  # GBR
    ncats["4.H.4"] = {"title": "Biogenic NMVOCs from managed forest"}  # FRA
    ncats["4.H.5"] = {"title": "Reservoir of Petit-Saut in French Guiana"}  # FRA
    ncats["4.H.6"] = {"title": "N2O Emissions from Aquaculture Use"}  # AUS
    ncats["4.H.7"] = {"title": "CH4 from artificial water bodies"}  # AUS
    ncats["4.H.8"] = {"title": "Luxembourg"}  # LUX
    ncats["4.H.9"] = {"title": "Other"}  # SWE, DEU
    # name for SWE is "All Other"

    # Table 5
    cats["5.E"]["children"] = [
        [
            "5.E.1",
            "5.E.2",
            "5.E.3",
            "5.E.4",
            "5.E.5",
            "5.E.6",
            "5.E.7",
        ]
    ]
    ncats["5.E.1"] = {"title": "Recycling activities"}  # NLD
    ncats["5.E.2"] = {"title": "Mechanical-Biological Treatment MBT"}  # DEU
    ncats["5.E.3"] = {"title": "Accidental fires"}  # DEU, DKE, DNK, DNM
    # name for ESP is "Accidential combustion"
    ncats["5.E.4"] = {"title": "Decomposition of Petroleum-Derived Surfactants"}  # JPN
    ncats["5.E.5"] = {"title": "Other non-specified"}  # USA
    # name for CZE is "Other waste"
    # name for EST, NOR is "Other"
    ncats["5.E.6"] = {"title": "Biogas burning without energy recovery"}  # PRT
    ncats["5.E.7"] = {"title": "Sludge spreading"}  # ESP

    # Table 5.B
    cats["5.B.1.b"]["children"] = [
        [
            "5.B.1.b.i",
            "5.B.1.b.ii",
            "5.B.1.b.iii",
            "5.B.1.b.iv",
            "5.B.1.b.v",
            "5.B.1.b.vi",
            "5.B.1.b.vii",
            "5.B.1.b.viii",
            "5.B.1.b.ix",
            "5.B.1.b.x",
            "5.B.1.b.xi",
            "5.B.1.b.xii",
            "5.B.1.b.xiii",
            "5.B.1.b.xiv",
            "5.B.1.b.xv",
            "5.B.1.b.xvi",
            "5.B.1.b.xvii",
            "5.B.1.b.xviii",
            "5.B.1.b.xix",
        ]
    ]
    ncats["5.B.1.b.i"] = {"title": "Organic wastes households"}  # NLD
    ncats["5.B.1.b.ii"] = {
        "title": "Organic wastes from gardens and horticulture"
    }  # NLD
    ncats["5.B.1.b.iii"] = {"title": "Industrial Solid Waste"}  # POL
    ncats["5.B.1.b.iv"] = {"title": "Home composting"}  # NOR
    ncats["5.B.1.b.v"] = {"title": "Other waste"}  # SWE
    # name for LTU is mixed waste
    # name for CZE is "Other_SW"
    ncats["5.B.1.b.vi"] = {"title": "Sludge"}  # HUN, EST
    ncats["5.B.1.b.vii"] = {"title": "Textile"}  # EST
    ncats["5.B.1.b.viii"] = {"title": "Wood"}  # EST
    ncats["5.B.1.b.ix"] = {"title": "Organic"}  # EST
    ncats["5.B.1.b.x"] = {"title": "Paper"}  # EST
    ncats["5.B.1.b.xi"] = {"title": "MBA treated MSW"}  # LUX
    ncats["5.B.1.b.xii"] = {
        "title": "Specific Agricultural and Industrial Waste"
    }  # UKR
    ncats["5.B.1.b.xiii"] = {"title": "Industrial solid waste and constr. waste"}  # FIN
    ncats["5.B.1.b.xiv"] = {"title": "Municipal sludge"}  # FIN
    ncats["5.B.1.b.xv"] = {"title": "Industrial sludge"}  # FIN
    ncats["5.B.1.b.xvi"] = {"title": "Open air composting"}  # LIE
    ncats["5.B.1.b.xvii"] = {"title": "Industrial Waste"}  # JPN
    ncats["5.B.1.b.xviii"] = {"title": "Human Waste and Johkasou sludge"}  # JPN
    ncats["5.B.1.b.xix"] = {"title": "Food and garden waste"}  # DNM, DNK, DKE

    cats["5.B.2.b"]["children"] = [
        [
            "5.B.2.b.i",
            "5.B.2.b.ii",
            "5.B.2.b.iii",
            "5.B.2.b.iv",
            "5.B.2.b.v",
            "5.B.2.b.vi",
            "5.B.2.b.vii",
            "5.B.2.b.viii",
            "5.B.2.b.ix",
            "5.B.2.b.x",
            "5.B.2.b.xi",
            "5.B.2.b.xii",
        ]
    ]
    ncats["5.B.2.b.i"] = {"title": "Organic wastes households"}  # NLD
    ncats["5.B.2.b.ii"] = {
        "title": "Organic wastes from gardens and horticulture"
    }  # NLD
    ncats["5.B.2.b.iii"] = {
        "title": "Animal manure and other organic waste"
    }  # DNM, DNK, DKE
    ncats["5.B.2.b.iv"] = {"title": "sewage sludge"}  # LTU
    # name for EST is "Sludge"
    ncats["5.B.2.b.v"] = {"title": "Other waste"}  # SWE
    # name for CZE is "Other_AD"
    ncats["5.B.2.b.vi"] = {"title": "Agricultural biogas facilities"}  # CHE
    ncats["5.B.2.b.vii"] = {
        "title": "Other biogases from anaerobic fermentation"
    }  # HUN
    ncats["5.B.2.b.viii"] = {
        "title": "Anaerobic Digestion On-Farm and at Wastewater Treatment Facilities"
    }  # USA
    ncats["5.B.2.b.ix"] = {
        "title": "Biogenic waste incl. wastes from Agriculture (manure)"
    }  # LUX
    ncats["5.B.2.b.x"] = {"title": "Industrial solid waste and constr. waste"}  # FIN
    ncats["5.B.2.b.xi"] = {"title": "Municipal sludge"}  # FIN
    ncats["5.B.2.b.xii"] = {"title": "Industrial sludge"}  # FIN

    # Table 5.C
    cats["5.C.1.a.ii.5"]["children"] = [
        [
            "5.C.1.a.ii.5.a",
            "5.C.1.a.ii.5.b",
            "5.C.1.a.ii.5.c",
            "5.C.1.a.ii.5.d",
            "5.C.1.a.ii.5.e",
            "5.C.1.a.ii.5.f",
            "5.C.1.a.ii.5.g",
        ]
    ]
    ncats["5.C.1.a.ii.5.a"] = {"title": "Animal cremations"}  # DKE, DNK, DNM
    ncats["5.C.1.a.ii.5.b"] = {"title": "Human cremations"}  # DKE, DNK, DNM
    ncats["5.C.1.a.ii.5.c"] = {"title": "Cremation"}  # CHE, NOR, FRA, FRK
    # name for DEU is "cremation"
    ncats["5.C.1.a.ii.5.d"] = {"title": "Industrial waste"}  # NOR
    ncats["5.C.1.a.ii.5.e"] = {"title": "Biogenic other waste"}  # EST
    # name for ROU is : "Biogenic waste other than Municipal Solid Waste"
    ncats["5.C.1.a.ii.5.f"] = {"title": "Sludge"}  # JPN
    ncats["5.C.1.a.ii.5.g"] = {"title": "Non-fossile liquid waste"}  # JPN

    cats["5.C.1.b.ii.5"]["children"] = [
        [
            "5.C.1.b.ii.5.a",
            "5.C.1.b.ii.5.b",
            "5.C.1.b.ii.5.c",
            "5.C.1.b.ii.5.d",
            "5.C.1.b.ii.5.e",
            "5.C.1.b.ii.5.f",
        ]
    ]
    ncats["5.C.1.b.ii.5.a"] = {"title": "Quarantine and other waste"}  # NZL
    ncats["5.C.1.b.ii.5.b"] = {"title": "Industrial waste"}  # CHE
    ncats["5.C.1.b.ii.5.c"] = {"title": "Chemical waste"}  # GBR, GBK
    ncats["5.C.1.b.ii.5.d"] = {"title": "Flaring in the chemical industry"}  # BEL
    ncats["5.C.1.b.ii.5.e"] = {"title": "Sludge"}  # JPN
    ncats["5.C.1.b.ii.5.f"] = {"title": "Solvents"}  # GRC, AUS

    cats["5.C.2.a.ii"]["children"] = [
        [
            "5.C.2.a.ii.1",
            "5.C.2.a.ii.2",
            "5.C.2.a.ii.3",
            "5.C.2.a.ii.4",
            "5.C.2.a.ii.5",
            "5.C.2.a.ii.6",
        ]
    ]
    ncats["5.C.2.a.ii.1"] = {"title": "agricultural waste"}  # ITA
    # name for ESP is "Agricultural residues"
    ncats["5.C.2.a.ii.2"] = {"title": "Natural residues"}  # CHE
    ncats["5.C.2.a.ii.3"] = {"title": "Wood waste"}  # GBR, GBK
    ncats["5.C.2.a.ii.4"] = {"title": "Bonfires etc."}  # DEU
    # name for NLD, ISL is "Bonfires"
    ncats["5.C.2.a.ii.5"] = {"title": "Other"}  # EST
    # name for CZE is  "Other waste"
    ncats["5.C.2.a.ii.6"] = {"title": "Industrial Solid Waste"}  # JPN

    cats["5.C.2.b.ii"]["children"] = [
        [
            "5.C.2.b.ii.1",
            "5.C.2.b.ii.2",
            "5.C.2.b.ii.3",
            "5.C.2.b.ii.4",
            "5.C.2.b.ii.5",
            "5.C.2.b.ii.6",
        ]
    ]
    ncats["5.C.2.b.ii.1"] = {"title": "Rural waste"}  # NZL
    ncats["5.C.2.b.ii.2"] = {"title": "Accidental fires (vehicles)"}  # GBR, GBK
    ncats["5.C.2.b.ii.3"] = {"title": "Accidental fires (buildings)"}  # GBR, GBK
    ncats["5.C.2.b.ii.4"] = {"title": "Bonfires"}  # ISL
    ncats["5.C.2.b.ii.5"] = {"title": "Other"}  # EST
    # name for CZE is  "Other waste"
    ncats["5.C.2.b.ii.6"] = {"title": "Industrial Solid Waste"}  # JPN

    # Table5.D
    cats["5.D.3"]["children"] = [
        [
            "5.D.3.a",
            "5.D.3.b",
            "5.D.3.c",
            "5.D.3.d",
        ]
    ]
    ncats["5.D.3.a"] = {"title": "Other"}  # EST
    # Name for CZE is "Uncategorized wastewater"
    ncats["5.D.3.b"] = {"title": "Septic tanks"}  # NLD
    ncats["5.D.3.c"] = {"title": "Wastewater Effluent"}  # NLD
    ncats["5.D.3.d"] = {"title": "Fish farming"}  # FIN

    for ncode in ncats:
        if "." in ncode:
            ncats[ncode]["alternative_codes"] = [
                ncode.replace(".", " "),
                ncode.replace(".", ""),
            ]

    cats.update(ncats)

    CRF2013_2021 = climate_categories.HierarchicalCategorization.from_spec(spec)

    CRF2013_2021.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
