"""Run this via `make climate_categories/data/CRF2013.yaml` in the main
directory."""

import pathlib

import climate_categories

OUTPATH = pathlib.Path("./climate_categories/data/CRF2013.yaml")


def main():
    """Create the CRF2013 categorization from the IPCC2006 categorization, which was
    also used by the UNFCCC to develop CRF2013. The sectors 3 (Agriculture),
    4 (LULUCF) and 5 (Waste) are rebuilt from scratch because agriculture
    and LUULCF are combined in one category in IPCC2006 but split in two categories
    here. The sector codes follow the codes used in the tables where possible
    and in consequence do not follow a consistent pattern.
    This categorization follows the template tables (adding subcategories for
    consistency in a few places). To read all submitted data including country specific
    subsectors in "Other" categories, an extended terminology is needed. With each
    submission round (e.g. 2021) these subsectors change, thus a submission-year
    specific extended terminology might be needed to avoid cluttered sector
    specifications.

    """
    spec = climate_categories.IPCC2006.to_spec()

    # Metadata
    spec["name"] = "CRF2013"
    spec["title"] = "Common Reporting Format GHG emissions categories (2013)"
    spec["comment"] = (
        "Classification of green-house gas emissions and removals into categories "
        "for use in annual inventories using the Common Reporting Format as "
        "specified in the UNFCCC guidelines on reporting and review as decided "
        "in the ninetenth session of the Conference of the Parties in 2013"
    )
    spec["references"] = (
        "United Nations 2013, Decision 24/CP.19 - Revision of the UNFCCC reporting "
        "guidelines on annual inventories for Parties included in Annex I to the "
        "Convention. Documented in the 'Report of the Conference of the Parties on "
        "its nineteenth session, held in Warsaw from 11 to 23 November 2013' "
        "available at https://unfccc.int/resource/docs/2013/cop19/eng/10a03.pdf"
    )
    spec["institution"] = "UN"
    spec["last_update"] = "2013-11-16"
    spec["version"] = "2013"
    spec["total_sum"] = True
    spec["canonical_top_level_category"] = "0"

    # Changes in categories
    cats = spec["categories"]
    ncats = {}

    # --------
    # go through the template files table by table
    # --------

    # Table1s1 - overview table, no additional information

    # Table1s2 - overview table, no additional information

    # Table1.A(a)s1 - energy Industries.
    # one category renamed, "other" subcategory added
    cats["1.A.1.a"]["title"] = "Public electricity and heat production"
    cats["1.A.1.a"]["children"][0].append("1.A.1.a.iv")
    ncats["1.A.1.a.iv"] = {
        "title": "Other (Please Specify)",
    }

    # Table1.A(a)s2 - Manufacturing Industries and Construction
    # additional grouping of some industries
    for cat in (
        "1.A.2.g",
        "1.A.2.h",
        "1.A.2.i",
        "1.A.2.j",
        "1.A.2.k",
        "1.A.2.l",
        "1.A.2.m",
    ):
        del cats[cat]
    cats["1.A.2"]["children"] = [
        ["1.A.2.a", "1.A.2.b", "1.A.2.c", "1.A.2.d", "1.A.2.e", "1.A.2.f", "1.A.2.g"]
    ]
    ncats["1.A.2.g"] = {
        "title": "Other (Please Specify)",
        "children": [
            [
                "1.A.2.g.i",
                "1.A.2.g.ii",
                "1.A.2.g.iii",
                "1.A.2.g.iv",
                "1.A.2.g.v",
                "1.A.2.g.vi",
                "1.A.2.g.vii",
                "1.A.2.g.viii",
            ]
        ],
    }
    ncats["1.A.2.g.i"] = {"title": "Manufacturing of Machinery"}
    ncats["1.A.2.g.ii"] = {"title": "Manufacturing of Transport Equipment"}
    ncats["1.A.2.g.iii"] = {"title": "Mining (Excluding Fuels) and Quarrying"}
    ncats["1.A.2.g.iv"] = {"title": "Wood and Wood Products"}
    ncats["1.A.2.g.v"] = {"title": "Construction"}
    ncats["1.A.2.g.vi"] = {"title": "Textile and Leather"}
    ncats["1.A.2.g.vii"] = {"title": "Off-Road Vehicles and Other Machinery"}
    ncats["1.A.2.g.viii"] = {"title": "Other (Please Specify)"}

    # Table1.A(a)s3 - Transport
    # some restructuring regarding bunker fuels and removal of some subcategories
    cats_to_remove = [
        "1.A.3.a",
        "1.A.3.a.i",
        "1.A.3.a.ii",
        "1.A.3.b.i.1",
        "1.A.3.b.i.2",
        "1.A.3.b.ii.1",
        "1.A.3.b.ii.2",
        "1.A.3.b.v",
        "1.A.3.b.vi",
        "1.A.3.d",
        "1.A.3.d.i",
        "1.A.3.d.ii",
    ]
    del cats["1.A.3.b.i"]["children"]
    del cats["1.A.3.b.ii"]["children"]
    for cat in cats_to_remove:
        del cats[cat]
    cats["1.A.3.b"]["children"] = [
        ["1.A.3.b.i", "1.A.3.b.ii", "1.A.3.b.iii", "1.A.3.b.iv", "1.A.3.b.v"]
    ]
    ncats["1.A.3.b.v"] = {"title": "Other (Please Specify)"}
    ncats["1.A.3.a"] = {"title": "Domestic Aviation"}
    ncats["1.A.3.d"] = {"title": "Domestic Navigation"}

    # Table1.A(a)s4 - Other Sectors
    # subsectors added
    # commercial / Institutional
    cats["1.A.4.a"]["children"] = [["1.A.4.a.i", "1.A.4.a.ii", "1.A.4.a.iii"]]
    ncats["1.A.4.a.i"] = {"title": "Stationary Combustion"}
    ncats["1.A.4.a.ii"] = {"title": "Off-Road Vehicles and Other Machinery"}
    ncats["1.A.4.a.iii"] = {"title": "Other (please specify)"}
    # residential
    cats["1.A.4.b"]["children"] = [["1.A.4.b.i", "1.A.4.b.ii", "1.A.4.b.iii"]]
    ncats["1.A.4.b.i"] = {"title": "Stationary Combustion"}
    ncats["1.A.4.b.ii"] = {"title": "Off-Road Vehicles and Other Machinery"}
    ncats["1.A.4.b.iii"] = {"title": "Other (please specify)"}
    # Agriculture/forestry/fishing
    cats["1.A.4.c.iii"]["title"] = "Fishing"
    # Other
    cats["1.A.5"] = {
        "title": "Other (not specified elsewhere)",
        "children": [["1.A.5.a", "1.A.5.b"]],
    }
    cats["1.A.5.b"][
        "children"
    ] = []  # for template tables, might be back in for actual data
    del cats["1.A.5.b.i"]
    del cats["1.A.5.b.ii"]
    del cats["1.A.5.b.iii"]
    del cats["1.A.5.c"]  # multilateral operations
    # Add information items outside the hierarchy
    ncats["M.Info"] = {
        "title": "Information Items",
        "children": [["M.Info.WI"]],
    }
    ncats["M.Info.WI"] = {
        "title": "Waste Incineration with energy recovery included as",
        "children": [["M.Info.WI.Bio", "M.Info.WI.FF"]],
    }
    ncats["M.Info.WI.Bio"] = {"title": "Biomass"}
    ncats["M.Info.WI.FF"] = {"title": "Fossil Fuels"}

    # Table1.A(b) - reference approach is an alternative to sectoral approach
    ncats["1.A-ref"] = {
        "title": "Reference Approach",
        "children": [["1.A-ref.1", "1.A-ref.2"]],
    }
    cats["1.A"]["children"].append(["1.A-ref"])

    ncats["1.A-ref.1"] = {
        "title": "Fossil Fuel",
        "children": [["1.A-ref.1.a", "1.A-ref.1.b", "1.A-ref.1.c", "1.A-ref.1.d"]],
    }
    ncats["1.A-ref.1.a"] = {
        "title": "Liquid Fossil",
        "children": [["1.A-ref.1.a.i", "1.A-ref.1.a.ii"]],
    }

    ncats["1.A-ref.1.a.i"] = {
        "title": "Primary Fuels",
        "children": [["1.A-ref.1.a.i.1", "1.A-ref.1.a.i.2", "1.A-ref.1.a.i.3"]],
    }
    ncats["1.A-ref.1.a.i.1"] = {"title": "Crude Oil"}
    ncats["1.A-ref.1.a.i.2"] = {"title": "Orimulsion"}
    ncats["1.A-ref.1.a.i.3"] = {"title": "Natural Gas Liquids"}

    ncats["1.A-ref.1.a.ii"] = {
        "title": "Secondary Fuels",
        "children": [[f"1.A-ref.1.a.ii.{x}" for x in range(1, 15)]],
    }
    ncats["1.A-ref.1.a.ii.1"] = {"title": "Gasoline"}
    ncats["1.A-ref.1.a.ii.2"] = {"title": "Jet Kerosene"}
    ncats["1.A-ref.1.a.ii.3"] = {"title": "Other Kerosene"}
    ncats["1.A-ref.1.a.ii.4"] = {"title": "Shale Oil"}
    ncats["1.A-ref.1.a.ii.5"] = {"title": "Gas / Diesel Oil"}
    ncats["1.A-ref.1.a.ii.6"] = {"title": "Residual Fuel Oil"}
    ncats["1.A-ref.1.a.ii.7"] = {"title": "Liquefied Petroleum Gases (LPG)"}
    ncats["1.A-ref.1.a.ii.8"] = {"title": "Ethane"}
    ncats["1.A-ref.1.a.ii.9"] = {"title": "Naphtha"}
    ncats["1.A-ref.1.a.ii.10"] = {"title": "Bitumen"}
    ncats["1.A-ref.1.a.ii.11"] = {"title": "Lubricants"}
    ncats["1.A-ref.1.a.ii.12"] = {"title": "Petroleum Coke"}
    ncats["1.A-ref.1.a.ii.13"] = {"title": "Refinery Feedstocks"}
    ncats["1.A-ref.1.a.ii.14"] = {"title": "Other Oil"}

    ncats["1.A-ref.1.b"] = {
        "title": "Solid Fossil",
        "children": [["1.A-ref.1.b.i", "1.A-ref.1.b.ii"]],
    }

    ncats["1.A-ref.1.b.i"] = {
        "title": "Primary Fuels",
        "children": [[f"1.A-ref.1.b.i.{x}" for x in range(1, 7)]],
    }
    ncats["1.A-ref.1.b.i.1"] = {"title": "Anthracite"}
    ncats["1.A-ref.1.b.i.2"] = {"title": "Coking Coal"}
    ncats["1.A-ref.1.b.i.3"] = {"title": "Other Bituminous Coal"}
    ncats["1.A-ref.1.b.i.4"] = {"title": "Sub-Bituminous Coal"}
    ncats["1.A-ref.1.b.i.5"] = {"title": "Lignite"}
    ncats["1.A-ref.1.b.i.6"] = {"title": "Oil Shale and Tar Sand"}
    # ncats["1.A-ref.1.b.i.7"] = {"title": "Peat"} # not in CRF2013 template

    ncats["1.A-ref.1.b.ii"] = {
        "title": "Secondary Fuels",
        "children": [["1.A-ref.1.b.ii.1", "1.A-ref.1.b.ii.2", "1.A-ref.1.b.ii.3"]],
    }
    ncats["1.A-ref.1.b.ii.1"] = {"title": "BKB & Patent Fuel"}
    ncats["1.A-ref.1.b.ii.2"] = {"title": "Coke Oven / Gas Coke"}
    ncats["1.A-ref.1.b.ii.3"] = {"title": "Coal Tar"}

    ncats["1.A-ref.1.c"] = {"title": "Gaseous Fossil", "children": [["1.A-ref.1.c.i"]]}
    ncats["1.A-ref.1.c.i"] = {"title": "Natural Gas (Dry)"}

    ncats["1.A-ref.1.d"] = {
        "title": "Other Fossil Fuels",
        "children": [["1.A-ref.1.d.i"]],
    }
    ncats["1.A-ref.1.d.i"] = {"title": "Peat"}

    ncats["1.A-ref.2"] = {
        "title": "Biomass",
        "children": [["1.A-ref.2.a", "1.A-ref.2.b", "1.A-ref.2.c", "1.A-ref.2.d"]],
    }
    ncats["1.A-ref.2.a"] = {"title": "Solid Biomass"}
    ncats["1.A-ref.2.b"] = {"title": "Liquid Biomass"}
    ncats["1.A-ref.2.c"] = {"title": "Gas Biomass"}
    ncats["1.A-ref.2.d"] = {"title": "Other non-Fossil Fuels (Biogenic Waste)"}

    # Table1.A(c) - comparison, no new sectors defined

    # Table1.A(d) - activity data, no new sectors defined

    # Table1.B.1 - Fugitive emissions from solid fuels
    # remove / restructure some subcategories
    del cats["1.B.1.a.i.4"]
    cats["1.B.1.a.i"]["children"] = [[f"1.B.1.a.i.{i}" for i in range(1, 4)]]
    del cats["1.B.1.b"]
    del cats["1.B.1.c"]
    ncats["1.B.1.b"] = {"title": "Solid Fuel Transformation"}
    ncats["1.B.1.c"] = {"title": "Other (please specify)"}

    # Table1.B.2 - Oil, natural gas, other
    # structure is completely different
    cats_to_remove = [
        "1.B.2.a.i",
        "1.B.2.a.ii",
        "1.B.2.a.iii",
        "1.B.2.a.iii.1",
        "1.B.2.a.iii.2",
        "1.B.2.a.iii.3",
        "1.B.2.a.iii.4",
        "1.B.2.a.iii.5",
        "1.B.2.a.iii.6",
        "1.B.2.b.i",
        "1.B.2.b.ii",
        "1.B.2.b.iii",
        "1.B.2.b.iii.1",
        "1.B.2.b.iii.2",
        "1.B.2.b.iii.3",
        "1.B.2.b.iii.4",
        "1.B.2.b.iii.5",
        "1.B.2.b.iii.6",
        "1.B.3",
    ]
    for cat in cats_to_remove:
        del cats[cat]

    cats["1.B"]["children"] = [["1.B.1", "1.B.2"]]
    cats["1.B.2"]["children"] = [["1.B.2.a", "1.B.2.b", "1.B.2.c", "1.B.2.d"]]
    # oil. the use of arabic numbers is against the usual structure but
    # we keep it to stay as close to the tables as possible
    cats["1.B.2.a"]["children"] = [
        ["1.B.2.a.1", "1.B.2.a.2", "1.B.2.a.3", "1.B.2.a.4", "1.B.2.a.5", "1.B.2.a.6"]
    ]
    ncats["1.B.2.a.1"] = {"title": "Exploration"}
    ncats["1.B.2.a.2"] = {"title": "Production"}
    ncats["1.B.2.a.3"] = {"title": "Transport"}
    ncats["1.B.2.a.4"] = {"title": "Refining / Storage"}
    ncats["1.B.2.a.5"] = {"title": "Distribution of Oil Products"}
    ncats["1.B.2.a.6"] = {"title": "Other"}
    # natural gas. the use of arabic numbers is against the usual structure but
    # we keep it to stay as close to the tables as possible
    cats["1.B.2.b"]["children"] = [[f"1.B.2.b.{i}" for i in range(1, 7)]]
    ncats["1.B.2.b.1"] = {"title": "Exploration"}
    ncats["1.B.2.b.2"] = {"title": "Production"}
    ncats["1.B.2.b.3"] = {"title": "Processing"}
    ncats["1.B.2.b.4"] = {"title": "Transmission and Storage"}
    ncats["1.B.2.b.5"] = {"title": "Distribution"}
    ncats["1.B.2.b.6"] = {"title": "Other"}
    # venting and flaring
    ncats["1.B.2.c"] = {
        "title": "Venting and Flaring",
        "children": [["1.B.2.c-ven", "1.B.2.c-fla"]],
    }
    ncats["1.B.2.c-ven"] = {
        "title": "Venting",
        "children": [["1.B.2.c-ven.i", "1.B.2.c-ven.ii", "1.B.2.c-ven.iii"]],
    }
    ncats["1.B.2.c-ven.i"] = {"title": "Oil"}
    ncats["1.B.2.c-ven.ii"] = {"title": "Gas"}
    ncats["1.B.2.c-ven.iii"] = {"title": "Combined"}
    ncats["1.B.2.c-fla"] = {
        "title": "Flaring",
        "children": [["1.B.2.c-fla.i", "1.B.2.c-fla.ii", "1.B.2.c-fla.iii"]],
    }
    ncats["1.B.2.c-fla.i"] = {"title": "Oil"}
    ncats["1.B.2.c-fla.ii"] = {"title": "Gas"}
    ncats["1.B.2.c-fla.iii"] = {"title": "Combined"}
    # other
    ncats["1.B.2.d"] = {"title": "Other (Please Specify)"}

    # Table1.C - CO2 transport and storage
    # add information items
    ncats["M.Info"]["children"][0].append("M.Info.CCS")
    ncats["M.Info.CCS"] = {
        "title": "CO2 Transport and Storage - information Items",
        "children": [
            [
                "M.Info.CCS.A",
                "M.Info.CCS.B",
            ]
        ],
    }
    ncats["M.Info.CCS.A"] = {
        "title": "CO2 Transport and Storage - information Items - Total A",
        "children": [["M.Info.CCS.A.TACS", "M.Info.CCS.A.TAIS"]],
    }
    ncats["M.Info.CCS.B"] = {
        "title": "CO2 Transport and Storage - information Items - Total B",
        "children": [
            [
                "M.Info.CCS.B.TAES",
                "M.Info.CCS.B.TAI",
                "M.Info.CCS.B.TLTIS",
            ]
        ],
    }
    ncats["M.Info.CCS.A.TACS"] = {"title": "Total Amount Captured for Storage"}
    ncats["M.Info.CCS.A.TAIS"] = {"title": "Total Amount of Imports for Storage"}
    ncats["M.Info.CCS.B.TAES"] = {"title": "Total Amount of Exports for Storage"}
    ncats["M.Info.CCS.B.TAI"] = {
        "title": "Tota Amount of CO2 Injected at Storage Sites"
    }
    ncats["M.Info.CCS.B.TLTIS"] = {
        "title": "Total Leakage from Transport, Injection and Storage"
    }

    # Table1.D - International shipping and aviation
    # we add some additional structure to the memo items here
    ncats["M.Memo"] = {
        "title": "Memo Items",
        "children": [["M.Memo.Int", "M.Memo.Mult", "M.Memo.CO2Cap", "M.Memo.Bio"]],
    }
    ncats["M.Memo.Int"] = {
        "title": "International Bunkers",
        "children": [["M.Memo.Int.Avi", "M.Memo.Int.Mar"]],
    }
    ncats["M.Memo.Int.Avi"] = {"title": "International Aviation (Aviation Bunkers)"}
    ncats["M.Memo.Int.Mar"] = {"title": "International Navigation (Marine Bunkers)"}
    ncats["M.Memo.Mult"] = {"title": "Multilateral Operations"}
    ncats["M.Memo.Bio"] = {"title": "CO2 Emissions from Biomass"}
    ncats["M.Memo.CO2Cap"] = {
        "title": "CO2 captured",
        "children": [["M.Memo.CO2Cap.Dom", "M.Memo.CO2Cap.Exp"]],
    }
    ncats["M.Memo.CO2Cap.Dom"] = {"title": "For Domestic Storage"}
    ncats["M.Memo.CO2Cap.Exp"] = {"title": "For Storage in Other Countries"}

    # Table2(I)s1/2 - just summary tables. use detailed tables instead

    # Table2(I).A-Hs1 - Mineral Industry and Chemical Industry
    # Mineral Industry
    del cats["2.A.5"]  # for the templates, probably still reported
    cats["2.A"]["children"] = [[f"2.A.{i}" for i in range(1, 5)]]
    # Chemical Industry
    cats["2.B.4"]["children"] = [["2.B.4.a", "2.B.4.b", "2.B.4.c"]]
    ncats["2.B.4.a"] = {"title": "Caprolactam"}
    ncats["2.B.4.b"] = {"title": "Glyoxal"}
    ncats["2.B.4.c"] = {"title": "Glyoxylic Acid"}
    cats["2.B.5"]["children"] = [["2.B.5.a", "2.B.5.b"]]
    ncats["2.B.5.a"] = {"title": "Silicon Carbide"}
    ncats["2.B.5.b"] = {"title": "Calcium Carbide"}
    cats["2.B.8"]["children"][0].append("2.B.8.g")
    ncats["2.B.8.g"] = {
        "title": "Other",
        "children": [["2.B.8.g.i", "2.B.8.g.ii"]],
    }
    ncats["2.B.8.g.i"] = {"title": "Styrene"}
    ncats["2.B.8.g.ii"] = {"title": "Other (please specify)"}
    # 2.B.9 is missing in this table as it's f-gases only

    # Table2(I).A-Hs1 - More industrial sectors
    # Metal Industry
    cats["2.C.1"]["children"] = [[f"2.C.1.{x}" for x in "abcdef"]]
    ncats["2.C.1.a"] = {"title": "Steel"}
    ncats["2.C.1.b"] = {"title": "Pig Iron"}
    ncats["2.C.1.c"] = {"title": "Direct Reduced Iron"}
    ncats["2.C.1.d"] = {"title": "Sinter"}
    ncats["2.C.1.e"] = {"title": "Pellet"}
    ncats["2.C.1.f"] = {"title": "Other (Please Specify)"}
    # non-energy products from fuels and solvent use
    cats["2.D"]["children"] = [["2.D.1", "2.D.2", "2.D.3"]]
    del cats["2.D.3"]
    del cats["2.D.4"]
    ncats["2.D.3"] = {
        "title": "Other (please specify)",
        "children": [[f"2.D.3.{x}" for x in "abcd"]],
    }
    ncats["2.D.3.a"] = {"title": "Solvent use"}
    ncats["2.D.3.b"] = {"title": "Road Paving with Asphlat"}
    ncats["2.D.3.c"] = {"title": "Asphalt Toofing"}
    ncats["2.D.3.d"] = {"title": "Other (Please Specify)"}
    # Other product manufacture and use
    cats["2.G.3"]["children"] = [["2.G.3.a", "2.G.3.b"]]
    del cats["2.G.3.b"]
    del cats["2.G.3.c"]
    ncats["2.G.3.b"] = {
        "title": "Other",
        "children": [["2.G.3.b.i", "2.G.3.b.ii"]],
    }
    ncats["2.G.3.b.i"] = {"title": "Propellant for Pressure and Aerosol Products"}
    ncats["2.G.3.b.ii"] = {"title": "Other (Please Specify)"}
    # Other: no changes needed

    # Table2(II), Tables2(II)B-Hs1/2 - Industrial Processes: f-gases
    # Chemical industry: additional subcategories
    cats["2.B.9.a"]["children"] = [["2.B.9.a.i", "2.B.9.a.ii"]]
    ncats["2.B.9.a.i"] = {"title": "Production of HCFC-22"}
    ncats["2.B.9.a.ii"] = {"title": "Other (Please Specify)"}
    cats["2.B.9.b"]["children"] = [["2.B.9.b.i", "2.B.9.b.ii", "2.B.9.b.iii"]]
    ncats["2.B.9.b.i"] = {"title": "Production of HFC-134a"}
    ncats["2.B.9.b.ii"] = {"title": "Production of SF6"}
    ncats["2.B.9.b.iii"] = {"title": "Other (Please Specify)"}
    # Metal industry
    cats["2.C.3"]["children"] = [[f"2.C.3.{x}" for x in "ab"]]
    ncats["2.C.3.a"] = {"title": "By-Product Emissions"}
    ncats["2.C.3.b"] = {"title": "F-Gases Used in Foundries"}
    # Product uses as substitutes for ODS
    cats["2.F.1"]["children"] = [[f"2.F.1.{x}" for x in "abcdef"]]
    del cats["2.F.1.a"]
    del cats["2.F.1.b"]
    ncats["2.F.1.a"] = {"title": "Commercial Refrigeration"}
    ncats["2.F.1.b"] = {"title": "Domestic Refrigeration"}
    ncats["2.F.1.c"] = {"title": "Industrial Refrigeration"}
    ncats["2.F.1.d"] = {"title": "Transport Refrigeration"}
    ncats["2.F.1.e"] = {"title": "Mobile Air-Conditioning"}
    ncats["2.F.1.f"] = {"title": "Stationary Air-Conditioning"}
    cats["2.F.4"]["children"] = [["2.F.4.a", "2.F.4.b"]]
    ncats["2.F.4.a"] = {"title": "Metered dose Inhalers"}
    ncats["2.F.4.b"] = {"title": "Others (Please Specify)"}
    cats["2.F.6"]["children"] = [["2.F.6.a", "2.F.6.b"]]
    ncats["2.F.6.a"] = {"title": "Emissive"}
    ncats["2.F.6.b"] = {"title": "Contained"}
    # Other product manufacture and use
    del cats["2.G.1"]["children"]
    for x in "abc":
        del cats[f"2.G.1.{x}"]
    cats["2.G.2"]["children"] = [[f"2.G.2.{x}" for x in "abcde"]]
    del cats["2.G.2.c"]
    ncats["2.G.2.c"] = {"title": "Soundproof Windows"}
    ncats["2.G.2.d"] = {"title": "Adiabatic Properties: Shoes and Tyres"}
    ncats["2.G.2.e"] = {"title": "Other (Please Specify)"}

    # Agriculture and LULUCF are separated in CRF but one category in IPCC2006
    # Thus we have to build the complete tree and delete the IPCC categories
    # first remove IPCC2006 category 3 (AFOLU)
    cats_to_remove = [cat for cat in cats.keys() if cat[0] == "3"]
    for cat in cats_to_remove:
        del cats[cat]

    # Table3s1/2 - Summary tables, only used for top level category
    ncats["3"] = {
        "title": "Total Agriculture",
        "children": [
            [f"3.{x}" for x in "ABCDEFGHIJ"],
            ["M.3.LV"] + [f"3.{x}" for x in "CDEFGHIJ"],
        ],
    }
    ncats["M.3.LV"] = {
        "title": "Livestock",
        "children": [["3.A", "3.B"]],
    }

    # Table3.A - Enteric fermentation
    ncats["3.A"] = {
        "title": "Enteric Fermentation",
        "children": [["3.A.1", "3.A.2", "3.A.3", "3.A.4"]],
    }
    ncats["3.A.1"] = {
        "title": "Cattle",
        "children": [
            ["3.A.1.Aa", "3.A.1.Ab"],
            ["3.A.1.Ba", "3.A.1.Bb", "3.A.1.Bc"],
            ["3.A.1.C"],
        ],
    }
    ncats["3.A.1.Aa"] = {"title": "Dairy Cattle"}
    ncats["3.A.1.Ab"] = {"title": "Non-Dairy Cattle"}
    ncats["3.A.1.Ba"] = {"title": "Mature Dairy Cattle"}
    ncats["3.A.1.Bb"] = {"title": "Other Mature Cattle"}
    ncats["3.A.1.Bc"] = {"title": "Growing Cattle"}
    ncats["3.A.1.C"] = {"title": "Other (as specified in table 3(I).A)"}
    # option C needs to be filled with what countries actually report
    # will be one grouping per country that reports in option c
    # these will be added in the submission year specific
    # terminologies
    ncats["3.A.2"] = {"title": "Sheep"}
    ncats["3.A.3"] = {"title": "Swine"}
    ncats["3.A.4"] = {
        "title": "Other Livestock",
        "children": [[f"3.A.4.{x}" for x in "abcdefgh"]],
    }
    ncats["3.A.4.a"] = {"title": "Buffalo"}
    ncats["3.A.4.b"] = {"title": "Camels"}
    ncats["3.A.4.c"] = {"title": "Deer"}
    ncats["3.A.4.d"] = {"title": "Goats"}
    ncats["3.A.4.e"] = {"title": "Horses"}
    ncats["3.A.4.f"] = {"title": "Mules and Asses"}
    ncats["3.A.4.g"] = {"title": "Poultry"}
    ncats["3.A.4.h"] = {
        "title": "Other (Please Specify)",
        "children": [
            ["3.A.4.h.i", "3.A.4.h.ii", "3.A.4.h.iii", "3.A.4.h.iv", "3.A.4.h.v"]
        ],
    }
    ncats["3.A.4.h.i"] = {"title": "Rabbit"}
    ncats["3.A.4.h.ii"] = {"title": "Reindeer"}
    ncats["3.A.4.h.iii"] = {"title": "Ostrich"}
    ncats["3.A.4.h.iv"] = {"title": "Fur-bearing Animals"}
    ncats["3.A.4.h.v"] = {"title": "Other"}

    # Table3.B(a/b) - Manure Management
    ncats["3.B"] = {
        "title": "Manure Management",
        "children": [["3.B.1", "3.B.2", "3.B.3", "3.B.4", "3.B.5"]],
    }
    ncats["3.B.1"] = {
        "title": "Cattle",
        "children": [
            ["3.B.1.Aa", "3.B.1.Ab"],
            ["3.B.1.Ba", "3.B.1.Bb", "3.B.1.Bc"],
            ["3.B.1.C"],
        ],
    }
    ncats["3.B.1.Aa"] = {"title": "Dairy Cattle"}
    ncats["3.B.1.Ab"] = {"title": "Non-Dairy Cattle"}
    ncats["3.B.1.Ba"] = {"title": "Mature Dairy Cattle"}
    ncats["3.B.1.Bb"] = {"title": "Other Mature Cattle"}
    ncats["3.B.1.Bc"] = {"title": "Growing Cattle"}
    ncats["3.B.1.C"] = {"title": "Other (as specified in table 3(I).B)"}
    # option C needs to be filled with what countries actually report
    # will be one grouping per country that reports in option c
    # these will be added in the submission year specific
    # terminologies
    ncats["3.B.2"] = {"title": "Sheep"}  # possibly subsectors in reported data
    ncats["3.B.3"] = {"title": "Swine"}  # possibly subsectors in reported data
    ncats["3.B.4"] = {
        "title": "Other Livestock",
        "children": [[f"3.B.4.{x}" for x in "abcdefgh"]],
    }
    ncats["3.B.4.a"] = {"title": "Buffalo"}
    ncats["3.B.4.b"] = {"title": "Camels"}
    ncats["3.B.4.c"] = {"title": "Deer"}
    ncats["3.B.4.d"] = {"title": "Goats"}
    ncats["3.B.4.e"] = {"title": "Horses"}
    ncats["3.B.4.f"] = {"title": "Mules and Asses"}
    ncats["3.B.4.g"] = {"title": "Poultry"}
    ncats["3.B.4.h"] = {
        "title": "Other (Please Specify)",
        "children": [
            ["3.B.4.h.i", "3.B.4.h.ii", "3.B.4.h.iii", "3.B.4.h.iv", "3.B.4.h.v"]
        ],
    }
    ncats["3.B.4.h.i"] = {"title": "Rabbit"}
    ncats["3.B.4.h.ii"] = {"title": "Reindeer"}
    ncats["3.B.4.h.iii"] = {"title": "Ostrich"}
    ncats["3.B.4.h.iv"] = {"title": "Fur-bearing Animals"}
    ncats["3.B.4.h.v"] = {"title": "Other"}

    ncats["3.B.5"] = {"title": "Indirect N2O emissions"}

    # Table3.C - Rice Cultivation
    ncats["3.C"] = {
        "title": "Rice Cultivation",
        "children": [[f"3.C.{i}" for i in range(1, 5)]],
    }
    ncats["3.C.1"] = {
        "title": "Irrigated",
        "children": [["3.C.1.a", "3.C.1.b"]],
    }
    ncats["3.C.1.a"] = {"title": "Continuously Flooded"}
    ncats["3.C.1.b"] = {
        "title": "Intermittently Flooded"
    }  # possible subsectors in reported data
    ncats["3.C.2"] = {
        "title": "Rain-Fed",
        "children": [["3.C.2.a", "3.C.2.b"]],
    }
    ncats["3.C.2.a"] = {"title": "Flood-Prone"}
    ncats["3.C.2.b"] = {"title": "Drought-Prone"}
    ncats["3.C.3"] = {
        "title": "Deep Water",
        "children": [["3.C.3.a", "3.C.3.b"]],
    }
    ncats["3.C.3.a"] = {"title": "Water Depth 50-100 cm"}
    ncats["3.C.3.b"] = {"title": "Water Depth > 100 cm"}
    ncats["3.C.4"] = {"title": "Other (Please Specify)"}
    # ignore the rows "Upland Rice" and "Total" as they don't contain emissions data

    # Table3.D - Direct and indirect N2O emissions from agricultural soils
    # we follow the numbering of subsectors in the table despite it not
    # fitting the general structure  of the hierarchy
    ncats["3.D"] = {
        "title": "Agricultural Soils",
        "children": [["3.D.a", "3.D.b"]],
    }
    ncats["3.D.a"] = {
        "title": "Direct N2O emissions from managed soils",
        "children": [[f"3.D.a.{i}" for i in range(1, 8)]],
    }
    ncats["3.D.a.1"] = {"title": "Inorganic N Fertilizers"}
    ncats["3.D.a.2"] = {
        "title": "Organic N Fertilizer",
        "children": [["3.D.a.2.a", "3.D.a.2.b", "3.D.a.2.c"]],
    }
    ncats["3.D.a.2.a"] = {"title": "Animal Manure Applied to Soils"}
    ncats["3.D.a.2.b"] = {"title": "Sewage Sludge Applied to Soils"}
    ncats["3.D.a.2.c"] = {"title": "Other Organic Fertilizer Applied to Soils"}
    ncats["3.D.a.3"] = {"title": "Urine and Dung Deposited by Grazing Animals"}
    ncats["3.D.a.4"] = {"title": "Crop Residues"}
    ncats["3.D.a.5"] = {
        "title": "Mineralization/immobilization associated with loss/gain of soil "
        "organic matter"
    }
    ncats["3.D.a.6"] = {"title": "Cultivation of Organic Soils (i.e. Histosols)"}
    ncats["3.D.a.7"] = {"title": "Other"}
    ncats["3.D.b"] = {
        "title": "Indirect N2O Emissions from Managed Soils",
        "children": [[f"3.D.b.{i}" for i in range(1, 3)]],
    }
    ncats["3.D.b.1"] = {"title": "Atmospheric Deposition"}
    ncats["3.D.b.2"] = {"title": "Nitrogen Leaching and Run-Off"}

    # Table3.E - Prescribed burning of Savannahs
    ncats["3.E"] = {
        "title": "Prescribed Burning of Savannahs",
        "children": [["3.E.1", "3.E.2"]],
    }
    ncats["3.E.1"] = {"title": "Forest Land"}  # possibly subsectors in reporting
    ncats["3.E.2"] = {"title": "Grassland"}  # possibly subsectors in reporting

    # Table3F - Field burning of Argricultural Residue
    ncats["3.F"] = {
        "title": "Field burning of Agricultural Residues",
        "children": [[f"3.F.{i}" for i in range(1, 6)]],
    }
    ncats["3.F.1"] = {
        "title": "Cereals",
        "children": [[f"3.F.1.{x}" for x in "abcd"]],
    }
    ncats["3.F.1.a"] = {"title": "Wheat"}
    ncats["3.F.1.b"] = {"title": "Barley"}
    ncats["3.F.1.c"] = {"title": "Maize"}
    ncats["3.F.1.d"] = {"title": "Other (Please Specify)"}
    ncats["3.F.2"] = {"title": "Pulses"}  # possible subsectors in reporting
    ncats["3.F.3"] = {"title": "Tubers and Roots"}  # possible subsectors in reporting
    ncats["3.F.4"] = {"title": "Sugar Cane"}
    ncats["3.F.5"] = {"title": "Other (Please Specify)"}

    # Table3.G-I
    ncats["3.G"] = {
        "title": "Liming",
        "children": [["3.G.1", "3.G.2"]],
    }
    ncats["3.G.1"] = {"title": "Limestone CaCO3"}
    ncats["3.G.2"] = {"title": "Dolomite CaMg(CO3)2"}
    ncats["3.H"] = {"title": "Urea Application"}
    ncats["3.I"] = {"title": "Other Carbon-Containing Fertilizers"}
    ncats["3.J"] = {"title": "Other (Please Specify)"}

    # Table4 - LULUCF overview
    # as the detailed tables use different hierarchies we only have the sectors
    # of this table in the main LULUCF hierarchy
    # we have to add a subsector for indirect N2O though as it is not included in
    # any of the subsectors
    # total LULUCF
    ncats["4"] = {
        "title": "Total LULUCF",
        "children": [
            [f"4.{x}" for x in "ABCDEFGH"],
            ["4A-F", "4(I)", "4(II)", "4(III)", "4(V)"],
        ],
    }
    # Forest Land
    ncats["4.A"] = {
        "title": "Forest Land",
        "children": [
            ["4.A.1", "4.A.2", "4(II).A"],
            ["4A-F.A", "4(I).A", "4(II).A", "4(III).A", "4(V).A"],
        ],
    }
    ncats["4.A.1"] = {
        "title": "Forest Land Remaining Forest Land",
        "children": [["4A-F.A.1", "4(I).A.1", "4(III).A.1", "4(V).A.1"]],
    }
    ncats["4.A.2"] = {
        "title": "Land Converted to Forest Land",
        "children": [["4A-F.A.2", "4(I).A.2", "4(III).A.2", "4(V).A.2"]],
    }
    # Cropland
    ncats["4.B"] = {
        "title": "Cropland",
        "children": [
            ["4.B.1", "4.B.2", "4(II).B"],
            ["4A-F.B", "4(II).B", "4(III).B", "4(V).B"],
        ],
    }
    ncats["4.B.1"] = {
        "title": "Cropland Remaining Cropland",
        "children": [["4A-F.B.1", "4(III).B.1", "4(V).B.1"]],
    }
    ncats["4.B.2"] = {
        "title": "Land Converted to Cropland",
        "children": [["4A-F.B.2", "4(III).B.2", "4(V).B.2"]],
    }
    # Grassland
    ncats["4.C"] = {
        "title": "Grassland",
        "children": [
            ["4.C.1", "4.C.2", "4(II).C"],
            ["4A-F.C", "4(II).C", "4(III).C", "4(V).C"],
        ],
    }
    ncats["4.C.1"] = {
        "title": "Grassland Remaining Grassland",
        "children": [["4A-F.C.1", "4(III).C.1", "4(V).C.1"]],
    }
    ncats["4.C.2"] = {
        "title": "Land Converted to Grassland",
        "children": [["4A-F.C.2", "4(III).C.2", "4(V).C.2"]],
    }
    # Wetlands
    ncats["4.D"] = {
        "title": "Wetlands",
        "children": [
            ["4.D.1", "4.D.2", "4(II).D"],
            ["4A-F.D", "4(I).D", "4(II).D", "4(III).D", "4(V).D"],
        ],
    }
    ncats["4.D.1"] = {
        "title": "Wetlands Remaining Wetlands",
        "children": [["4A-F.D.1", "4(I).D.1", "4(III).D.1", "4(V).D.1"]],
    }
    ncats["4.D.2"] = {
        "title": "Land Converted to Wetlands",
        "children": [["4A-F.D.2", "4(I).D.2", "4(III).D.2", "4(V).D.2"]],
    }
    # Settlements
    ncats["4.E"] = {
        "title": "Settlements",
        "children": [["4.E.1", "4.E.2"], ["4A-F.E", "4(I).E", "4(III).E", "4(V).E"]],
    }
    ncats["4.E.1"] = {
        "title": "Settlements Remaining Settlements",
        "children": [["4A-F.E.1", "4(I).E.1", "4(III).E.1", "4(V).E.1"]],
    }
    ncats["4.E.2"] = {
        "title": "Land Converted to Settlements",
        "children": [["4A-F.E.2", "4(I).E.2", "4(III).E.2", "4(V).E.2"]],
    }
    # Other Land
    ncats["4.F"] = {
        "title": "Other Land",
        "children": [["4.F.1", "4.F.2"], ["4A-F.F", "4(III).F", "4(V).F"]],
    }
    ncats["4.F.1"] = {
        "title": "Other Land Remaining Other Land",
        "children": [["4A-F.F.1", "4(III).F.1", "4(V).F.1"]],
    }
    ncats["4.F.2"] = {
        "title": "Land Converted to Other Land",
        "children": [["4A-F.F.2", "4(III).F.2", "4(V).F.2"]],
    }
    # Harvested Wood Products
    ncats["4.G"] = {"title": "Harvested Wood Products"}
    # Other
    ncats["4.H"] = {
        "title": "Other ( Please Specify)",
        "children": [["4(I).H", "4(II).H", "4(V).H"]],
    }
    # indirect N2O
    # will be added with Table 4(IV)

    # Table4.1 - Land conversion matrix, no sector information taken

    # the LULUCF reporting does not follow a single hierarchy,
    # but the same sector hierarchy is repeated several times.
    # Thus we have to add an additional layer to distinguish
    # between the sources and accommodate all data
    # for Tables 4.A to 4.F we use the head category 4A-F
    ncats["4A-F"] = {
        "title": "LULUCF data by land type. CRF Tables 4.a - 4.G",
        "children": [["4A-F.A", "4A-F.B", "4A-F.C", "4A-F.D", "4A-F.E", "4A-F.F"]],
    }

    # Table4.A - Forest Land
    ncats["4A-F.A"] = {
        "title": "Total Forest Land",
        "children": [["4A-F.A.1", "4A-F.A.2"]],
    }
    ncats["4A-F.A.1"] = {"title": "Forest Land Remaining Forest Land"}
    ncats["4A-F.A.2"] = {
        "title": "Land Converted to Forest Land",
        "children": [[f"4A-F.A.2.{i}" for i in range(1, 6)]],
    }
    ncats["4A-F.A.2.1"] = {"title": "Gropland Converted to Forest Land"}
    ncats["4A-F.A.2.2"] = {"title": "Grassland Converted to Forest Land"}
    ncats["4A-F.A.2.3"] = {"title": "Wetlands Converted to Forest Land"}
    ncats["4A-F.A.2.4"] = {"title": "Settlements Converted to Forest Land"}
    ncats["4A-F.A.2.5"] = {"title": "Other Land Converted to Forest Land"}

    # Table4.B - Cropland
    ncats["4A-F.B"] = {
        "title": "Total Cropland",
        "children": [["4A-F.B.1", "4A-F.B.2"]],
    }
    ncats["4A-F.B.1"] = {"title": "Cropland Remaining Cropland"}
    ncats["4A-F.B.2"] = {
        "title": "Land Converted to Cropland",
        "children": [[f"4A-F.B.2.{i}" for i in range(1, 6)]],
    }
    ncats["4A-F.B.2.1"] = {"title": "Forest Land Converted to Cropland"}
    ncats["4A-F.B.2.2"] = {"title": "Grassland Converted to Cropland"}
    ncats["4A-F.B.2.3"] = {"title": "Wetlands Converted to Cropland"}
    ncats["4A-F.B.2.4"] = {"title": "Settlements Converted to Cropland"}
    ncats["4A-F.B.2.5"] = {"title": "Other Land Converted to Cropland"}

    # Table4.C - Grassland
    ncats["4A-F.C"] = {
        "title": "Total Grassland",
        "children": [["4A-F.C.1", "4A-F.C.2"]],
    }
    ncats["4A-F.C.1"] = {"title": "Grassland Remaining Grassland"}
    ncats["4A-F.C.2"] = {
        "title": "Land Converted to Grassland",
        "children": [[f"4A-F.C.2.{i}" for i in range(1, 6)]],
    }
    ncats["4A-F.C.2.1"] = {"title": "Forest Land Converted to Grassland"}
    ncats["4A-F.C.2.2"] = {"title": "Cropland Converted to Grassland"}
    ncats["4A-F.C.2.3"] = {"title": "Wetlands Converted to Grassland"}
    ncats["4A-F.C.2.4"] = {"title": "Settlements Converted to Grassland"}
    ncats["4A-F.C.2.5"] = {"title": "Other Land Converted to Grassland"}

    # Table4.D - Wetlands
    ncats["4A-F.D"] = {
        "title": "Total Wetlands",
        "children": [["4A-F.D.1", "4A-F.D.2"]],
    }
    ncats["4A-F.D.1"] = {
        "title": "Wetlands Remaining Wetlands",
        "children": [["4A-F.D.1.1", "4A-F.D.1.2", "4A-F.D.1.3"]],
    }
    ncats["4A-F.D.1.1"] = {"title": "Peat Extraction Remaining Peat Extraction"}
    ncats["4A-F.D.1.2"] = {"title": "Flooded Land Remaining Flooded Land"}
    ncats["4A-F.D.1.3"] = {"title": "Other Wetlands Remaining Other Wetlands"}
    ncats["4A-F.D.2"] = {
        "title": "Land Converted to Wetlands",
        "children": [[f"4A-F.D.2.{i}" for i in range(1, 4)]],
    }
    ncats["4A-F.D.2.1"] = {"title": "Land Converted to Peat Extraction"}
    ncats["4A-F.D.2.2"] = {
        "title": "Land Converted to Flooded Land",
        "children": [[f"4A-F.D.2.2.{i}" for i in range(1, 6)]],
    }
    ncats["4A-F.D.2.2.1"] = {"title": "Forest Land Converted to Flooded Land"}
    ncats["4A-F.D.2.2.2"] = {"title": "Cropland Converted to Flooded Land"}
    ncats["4A-F.D.2.2.3"] = {"title": "Grassland Converted to Flooded Land"}
    ncats["4A-F.D.2.2.4"] = {"title": "Settlements Converted to Flooded Land"}
    ncats["4A-F.D.2.2.5"] = {"title": "Other Land Converted to Flooded Land"}
    ncats["4A-F.D.2.3"] = {
        "title": "Land Converted to Other Wetlands",
        "children": [[f"4A-F.D.2.3.{i}" for i in range(1, 6)]],
    }
    ncats["4A-F.D.2.3.1"] = {"title": "Forest Land Converted to Other Wetlands"}
    ncats["4A-F.D.2.3.2"] = {"title": "Cropland Converted to Other Wetlands"}
    ncats["4A-F.D.2.3.3"] = {"title": "Grassland Converted to Other Wetlands"}
    ncats["4A-F.D.2.3.4"] = {"title": "Settlements Converted to Other Wetlands"}
    ncats["4A-F.D.2.3.5"] = {"title": "Other Land Converted to Other Wetlands"}

    # Table4.E - Settlements
    ncats["4A-F.E"] = {
        "title": "Total Settlements",
        "children": [["4A-F.E.1", "4A-F.E.2"]],
    }
    ncats["4A-F.E.1"] = {"title": "Settlements Remaining Settlements"}
    ncats["4A-F.E.2"] = {
        "title": "Land Converted to Settlements",
        "children": [[f"4A-F.E.2.{i}" for i in range(1, 6)]],
    }
    ncats["4A-F.E.2.1"] = {"title": "Forest Land Converted to Settlements"}
    ncats["4A-F.E.2.2"] = {"title": "Cropland Converted to Settlements"}
    ncats["4A-F.E.2.3"] = {"title": "Grassland Converted to Settlements"}
    ncats["4A-F.E.2.4"] = {"title": "Wetlands Converted to Settlements"}
    ncats["4A-F.E.2.5"] = {"title": "Other Land Converted to Settlements"}

    # Table4.F - Other Land
    ncats["4A-F.F"] = {
        "title": "Total Other Land",
        "children": [["4A-F.F.1", "4A-F.F.2"]],
    }
    ncats["4A-F.F.1"] = {"title": "Other Land Remaining Other Land"}
    ncats["4A-F.F.2"] = {
        "title": "Land Converted to Other Land",
        "children": [[f"4A-F.F.2.{i}" for i in range(1, 6)]],
    }
    ncats["4A-F.F.2.1"] = {"title": "Forest Land Converted to Other Land"}
    ncats["4A-F.F.2.2"] = {"title": "Cropland Converted to Other Land"}
    ncats["4A-F.F.2.3"] = {"title": "Grassland Converted to Other Land"}
    ncats["4A-F.F.2.4"] = {"title": "Wetlands Converted to Other Land"}
    ncats["4A-F.F.2.5"] = {"title": "Settlements Converted to Other Land"}

    # Table4(I) - Direct N2O emissions from nitrogen inputs to managed soils
    # here we use 4(I) as head category
    ncats["4(I)"] = {
        "title": "LULUCF - Direct N2O from nitrogen inputs to managed soils "
        "(Table 4(I)",
        "children": [["4(I).A", "4(I).D", "4(I).E", "4(I).H"]],
    }
    # Forest Land
    ncats["4(I).A"] = {
        "title": "Forest Land",
        "children": [["4(I).A.1", "4(I).A.2"]],
    }
    ncats["4(I).A.1"] = {
        "title": "Forest Land Remaining Forest Land",
        "children": [["4(I).A.1.1", "4(I).A.1.2"]],
    }
    ncats["4(I).A.1.1"] = {"title": "Inorganic N Fertilizer"}
    ncats["4(I).A.1.2"] = {"title": "Organic N Fertilizer"}
    ncats["4(I).A.2"] = {
        "title": "Land Converted to Forest Land",
        "children": [["4(I).A.2.1", "4(I).A.2.2"]],
    }
    ncats["4(I).A.2.1"] = {"title": "Inorganic N Fertilizer"}
    ncats["4(I).A.2.2"] = {"title": "Organic N Fertilizer"}
    # Wetlands
    ncats["4(I).D"] = {
        "title": "Wetlands",
        "children": [["4(I).D.1", "4(I).D.2"]],
    }
    ncats["4(I).D.1"] = {
        "title": "Wetlands Remaining Wetlands",
        "children": [["4(I).D.1.1", "4(I).D.1.2"]],
    }
    ncats["4(I).D.1.1"] = {"title": "Inorganic N Fertilizer"}
    ncats["4(I).D.1.2"] = {"title": "Organic N Fertilizer"}
    ncats["4(I).D.2"] = {
        "title": "Land Converted to Wetlands",
        "children": [["4(I).D.2.1", "4(I).D.2.2"]],
    }
    ncats["4(I).D.2.1"] = {"title": "Inorganic N Fertilizer"}
    ncats["4(I).D.2.2"] = {"title": "Organic N Fertilizer"}
    # Settlements
    ncats["4(I).E"] = {
        "title": "Settlements",
        "children": [["4(I).E.1", "4(I).E.2"]],
    }
    ncats["4(I).E.1"] = {
        "title": "Settlements Remaining Settlements",
        "children": [["4(I).E.1.1", "4(I).E.1.2"]],
    }
    ncats["4(I).E.1.1"] = {"title": "Inorganic N Fertilizer"}
    ncats["4(I).E.1.2"] = {"title": "Organic N Fertilizer"}
    ncats["4(I).E.2"] = {
        "title": "Land Converted to Settlements",
        "children": [["4(I).E.2.1", "4(I).E.2.2"]],
    }
    ncats["4(I).E.2.1"] = {"title": "Inorganic N Fertilizer"}
    ncats["4(I).E.2.2"] = {"title": "Organic N Fertilizer"}
    # Other
    ncats["4(I).H"] = {
        "title": "Other (Please specify)",
        "children": [["4(I).H.1", "4(I).H.2"]],
    }
    ncats["4(I).H.1"] = {"title": "Inorganic N Fertilizer"}
    ncats["4(I).H.2"] = {"title": "Organic N Fertilizer"}

    # Table4(II) - Emissions and removal from drainage and rewetting
    ncats["4(II)"] = {
        "title": "LULUCF - Emissions and removals from drainage and rewetting "
        "and other management of organic and mineral soils  (Table 4(II))",
        "children": [["4(II).A", "4(II).B", "4(II).C", "4(II).D", "4(II).H"]],
    }
    # Forest Land
    ncats["4(II).A"] = {
        "title": "Forest Land",
        "children": [["4(II).A.1", "4(II).A.2"]],
    }
    ncats["4(II).A.1"] = {
        "title": "Total Organic Soils",
        "children": [["4(II).A.1.a", "4(II).A.1.b", "4(II).A.1.c"]],
    }
    ncats["4(II).A.1.a"] = {"title": "Drained Organic Soils"}
    ncats["4(II).A.1.b"] = {"title": "Rewetted Organic Soils"}
    ncats["4(II).A.1.c"] = {"title": "Other (Please Specify)"}
    ncats["4(II).A.2"] = {
        "title": "Total Mineral Soils",
        "children": [["4(II).A.2.a", "4(II).A.2.b"]],
    }
    ncats["4(II).A.2.a"] = {"title": "Rewetted Mineral Soils"}
    ncats["4(II).A.2.b"] = {"title": "Other (Please Specify)"}
    # Cropland
    ncats["4(II).B"] = {
        "title": "Cropland",
        "children": [["4(II).B.1", "4(II).B.2"]],
    }
    ncats["4(II).B.1"] = {
        "title": "Total Organic Soils",
        "children": [["4(II).B.1.a", "4(II).B.1.b", "4(II).B.1.c"]],
    }
    ncats["4(II).B.1.a"] = {"title": "Drained Organic Soils"}
    ncats["4(II).B.1.b"] = {"title": "Rewetted Organic Soils"}
    ncats["4(II).B.1.c"] = {"title": "Other (Please Specify)"}
    ncats["4(II).B.2"] = {
        "title": "Total Mineral Soils",
        "children": [["4(II).B.2.a", "4(II).B.2.b"]],
    }
    ncats["4(II).B.2.a"] = {"title": "Rewetted Mineral Soils"}
    ncats["4(II).B.2.b"] = {"title": "Other (Please Specify)"}
    # Grassland
    ncats["4(II).C"] = {
        "title": "Grassland",
        "children": [["4(II).C.1", "4(II).C.2"]],
    }
    ncats["4(II).C.1"] = {
        "title": "Total Organic Soils",
        "children": [["4(II).C.1.a", "4(II).C.1.b", "4(II).C.1.c"]],
    }
    ncats["4(II).C.1.a"] = {"title": "Drained Organic Soils"}
    ncats["4(II).C.1.b"] = {"title": "Rewetted Organic Soils"}
    ncats["4(II).C.1.c"] = {"title": "Other (Please Specify)"}
    ncats["4(II).C.2"] = {
        "title": "Total Mineral Soils",
        "children": [["4(II).C.2.a", "4(II).C.2.b"]],
    }
    ncats["4(II).C.2.a"] = {"title": "Rewetted Mineral Soils"}
    ncats["4(II).C.2.b"] = {"title": "Other (Please Specify)"}
    # Wetlands
    ncats["4(II).D"] = {
        "title": "Wetlands",
        "children": [["4(II).D.1", "4(II).D.2", "4(II).D.3"]],
    }
    ncats["4(II).D.1"] = {
        "title": "Peat Extraction Lands",
        "children": [["4(II).D.1.a", "4(II).D.1.b"]],
    }
    ncats["4(II).D.1.a"] = {
        "title": "Total Organic Soils",
        "children": [["4(II).D.1.a.i", "4(II).D.1.a.ii", "4(II).D.1.a.iii"]],
    }
    ncats["4(II).D.1.a.i"] = {"title": "Drained Organic Soils"}
    ncats["4(II).D.1.a.ii"] = {"title": "Rewetted Organic Soils"}
    ncats["4(II).D.1.a.iii"] = {"title": "Other (Please Specify)"}
    ncats["4(II).D.1.b"] = {
        "title": "Total Mineral Soils",
        "children": [["4(II).D.1.b.i", "4(II).D.1.b.ii"]],
    }
    ncats["4(II).D.1.b.i"] = {"title": "Rewetted Mineral Soils"}
    ncats["4(II).D.1.b.ii"] = {"title": "Other (Please Specify)"}
    ncats["4(II).D.2"] = {
        "title": "Flooded Lands",
        "children": [["4(II).D.2.a", "4(II).D.2.b"]],
    }
    ncats["4(II).D.2.a"] = {
        "title": "Total Organic Soils",
        "children": [["4(II).D.2.a.i", "4(II).D.2.a.ii", "4(II).D.2.a.iii"]],
    }
    ncats["4(II).D.2.a.i"] = {"title": "Drained Organic Soils"}
    ncats["4(II).D.2.a.ii"] = {"title": "Rewetted Organic Soils"}
    ncats["4(II).D.2.a.iii"] = {"title": "Other (Please Specify)"}
    ncats["4(II).D.2.b"] = {
        "title": "Total Mineral Soils",
        "children": [["4(II).D.2.b.i", "4(II).D.2.b.ii"]],
    }
    ncats["4(II).D.2.b.i"] = {"title": "Rewetted Mineral Soils"}
    ncats["4(II).D.2.b.ii"] = {"title": "Other (Please Specify)"}
    ncats["4(II).D.3"] = {
        "title": "Other Wetlands",
        "children": [["4(II).D.3.a", "4(II).D.3.b"]],
    }
    ncats["4(II).D.3.a"] = {
        "title": "Total Organic Soils",
        "children": [["4(II).D.3.a.i", "4(II).D.3.a.ii", "4(II).D.3.a.iii"]],
    }
    ncats["4(II).D.3.a.i"] = {"title": "Drained Organic Soils"}
    ncats["4(II).D.3.a.ii"] = {"title": "Rewetted Organic Soils"}
    ncats["4(II).D.3.a.iii"] = {"title": "Other (Please Specify)"}
    ncats["4(II).D.3.b"] = {
        "title": "Total Mineral Soils",
        "children": [["4(II).D.3.b.i", "4(II).D.3.b.ii"]],
    }
    ncats["4(II).D.3.b.i"] = {"title": "Rewetted Mineral Soils"}
    ncats["4(II).D.3.b.ii"] = {"title": "Other (Please Specify)"}
    # Other
    ncats["4(II).H"] = {
        "title": "Other (Please Specify)",
        "children": [["4(II).H.1", "4(II).H.2"]],
    }
    ncats["4(II).H.1"] = {
        "title": "Total Organic Soils",
        "children": [["4(II).H.1.a", "4(II).H.1.b", "4(II).H.1.c"]],
    }
    ncats["4(II).H.1.a"] = {"title": "Drained Organic Soils"}
    ncats["4(II).H.1.b"] = {"title": "Rewetted Organic Soils"}
    ncats["4(II).H.1.c"] = {"title": "Other (Please Specify)"}
    ncats["4(II).H.2"] = {
        "title": "Total Mineral Soils",
        "children": [["4(II).H.2.a", "4(II).H.2.b"]],
    }
    ncats["4(II).H.2.a"] = {"title": "Rewetted Mineral Soils"}
    ncats["4(II).H.2.b"] = {"title": "Other (Please Specify)"}

    # Table4(III) - Direct nitrous oxide (N2O) emissions from nitrogen (N)
    # mineralization/immobilization associated with loss/gain of soil
    # organic matter resulting from change of land use or management of mineral
    # soils
    # same sectors as in 4.A-F
    ncats["4(III)"] = {
        "title": "LULUCF - Direct N2O Eemissions from Nitrogen (N) "
        "Mineralization/Immobilization Associated with "
        "Loss/Gain of Soil Organic Matter Resulting from "
        "Change of Land Use or Management of Mineral Soils "
        "(Table 4(III))",
        "children": [[f"4(III).{x}" for x in "ABCDEF"]],
    }
    ncats["4(III).A"] = {
        "title": "Forest Land",
        "children": [["4(III).A.1", "4(III).A.2"]],
    }
    ncats["4(III).A.1"] = {"title": "Forest Land Remaining Forest Land"}
    ncats["4(III).A.2"] = {
        "title": "Land Converted to Forest Land",
        "children": [[f"4(III).A.2.{i}" for i in range(1, 6)]],
    }
    ncats["4(III).A.2.1"] = {"title": "Gropland Converted to Forest Land"}
    ncats["4(III).A.2.2"] = {"title": "Grassland Converted to Forest Land"}
    ncats["4(III).A.2.3"] = {"title": "Wetlands Converted to Forest Land"}
    ncats["4(III).A.2.4"] = {"title": "Settlements Converted to Forest Land"}
    ncats["4(III).A.2.5"] = {"title": "Other Land Converted to Forest Land"}
    # Cropland
    ncats["4(III).B"] = {
        "title": "Cropland",
        "children": [["4(III).B.1", "4(III).B.2"]],
    }
    ncats["4(III).B.1"] = {"title": "Cropland Remaining Cropland"}
    ncats["4(III).B.2"] = {
        "title": "Land Converted to Cropland",
        "children": [[f"4(III).B.2.{i}" for i in range(1, 6)]],
    }
    ncats["4(III).B.2.1"] = {"title": "Forest Land Converted to Cropland"}
    ncats["4(III).B.2.2"] = {"title": "Grassland Converted to Cropland"}
    ncats["4(III).B.2.3"] = {"title": "Wetlands Converted to Cropland"}
    ncats["4(III).B.2.4"] = {"title": "Settlements Converted to Cropland"}
    ncats["4(III).B.2.5"] = {"title": "Other Land Converted to Cropland"}
    # Grassland
    ncats["4(III).C"] = {
        "title": "Grassland",
        "children": [["4(III).C.1", "4(III).C.2"]],
    }
    ncats["4(III).C.1"] = {"title": "Grassland Remaining Grassland"}
    ncats["4(III).C.2"] = {
        "title": "Land Converted to Grassland",
        "children": [[f"4(III).C.2.{i}" for i in range(1, 6)]],
    }
    ncats["4(III).C.2.1"] = {"title": "Forest Land Converted to Grassland"}
    ncats["4(III).C.2.2"] = {"title": "Cropland Converted to Grassland"}
    ncats["4(III).C.2.3"] = {"title": "Wetlands Converted to Grassland"}
    ncats["4(III).C.2.4"] = {"title": "Settlements Converted to Grassland"}
    ncats["4(III).C.2.5"] = {"title": "Other Land Converted to Grassland"}
    # Wetlands
    ncats["4(III).D"] = {
        "title": "Wetlands",
        "children": [["4(III).D.1", "4(III).D.2"]],
    }
    ncats["4(III).D.1"] = {
        "title": "Wetlands Remaining Wetlands",
        "children": [["4(III).D.1.1", "4(III).D.1.2", "4(III).D.1.3"]],
    }
    ncats["4(III).D.1.1"] = {"title": "Peat Extraction Remaining Peat Extraction"}
    ncats["4(III).D.1.2"] = {"title": "Flooded Land Remaining Flooded Land"}
    ncats["4(III).D.1.3"] = {"title": "Other Wetlands Remaining Other Wetlands"}
    ncats["4(III).D.2"] = {
        "title": "Land Converted to Wetlands",
        "children": [[f"4(III).D.2.{i}" for i in range(1, 4)]],
    }
    ncats["4(III).D.2.1"] = {"title": "Land Converted to Peat Extraction"}
    ncats["4(III).D.2.2"] = {
        "title": "Land Converted to Flooded Land",
        "children": [[f"4(III).D.2.2.{i}" for i in range(1, 6)]],
    }
    ncats["4(III).D.2.2.1"] = {"title": "Forest Land Converted to Flooded Land"}
    ncats["4(III).D.2.2.2"] = {"title": "Cropland Converted to Flooded Land"}
    ncats["4(III).D.2.2.3"] = {"title": "Grassland Converted to Flooded Land"}
    ncats["4(III).D.2.2.4"] = {"title": "Settlements Converted to Flooded Land"}
    ncats["4(III).D.2.2.5"] = {"title": "Other Land Converted to Flooded Land"}
    ncats["4(III).D.2.3"] = {
        "title": "Land Converted to Other Wetlands",
        "children": [[f"4(III).D.2.3.{i}" for i in range(1, 6)]],
    }
    ncats["4(III).D.2.3.1"] = {"title": "Forest Land Converted to Other Wetlands"}
    ncats["4(III).D.2.3.2"] = {"title": "Cropland Converted to Other Wetlands"}
    ncats["4(III).D.2.3.3"] = {"title": "Grassland Converted to Other Wetlands"}
    ncats["4(III).D.2.3.4"] = {"title": "Settlements Converted to Other Wetlands"}
    ncats["4(III).D.2.3.5"] = {"title": "Other Land Converted to Other Wetlands"}
    # Settlements
    ncats["4(III).E"] = {
        "title": "Settlements",
        "children": [["4(III).E.1", "4(III).E.2"]],
    }
    ncats["4(III).E.1"] = {"title": "Settlements Remaining Settlements"}
    ncats["4(III).E.2"] = {
        "title": "Land Converted to Settlements",
        "children": [[f"4(III).E.2.{i}" for i in range(1, 6)]],
    }
    ncats["4(III).E.2.1"] = {"title": "Forest Land Converted to Settlements"}
    ncats["4(III).E.2.2"] = {"title": "Cropland Converted to Settlements"}
    ncats["4(III).E.2.3"] = {"title": "Grassland Converted to Settlements"}
    ncats["4(III).E.2.4"] = {"title": "Wetlands Converted to Settlements"}
    ncats["4(III).E.2.5"] = {"title": "Other Land Converted to Settlements"}
    # Other Land. Subsectors are not present in the template tables but we add them here
    # in case they are reported by a country
    ncats["4(III).F"] = {
        "title": "Other Land",
        "children": [["4(III).F.1", "4(III).F.2"]],
    }
    ncats["4(III).F.1"] = {"title": "Other Land Remaining Other Land"}
    ncats["4(III).F.2"] = {
        "title": "Land Converted to Other Land",
        "children": [[f"4(III).F.2.{i}" for i in range(1, 6)]],
    }
    ncats["4(III).F.2.1"] = {"title": "Forest Land Converted to Other Land"}
    ncats["4(III).F.2.2"] = {"title": "Cropland Converted to Other Land"}
    ncats["4(III).F.2.3"] = {"title": "Grassland Converted to Other Land"}
    ncats["4(III).F.2.4"] = {"title": "Wetlands Converted to Other Land"}
    ncats["4(III).F.2.5"] = {"title": "Other Land Converted to Other Land"}

    # Table4(iv) - Indirect N2O emissions from managed soils
    # Emissions are included in total LULUCF sums but in none of the
    # subsectors. Thus we add a subsector to the hierarchy
    ncats["4"]["children"][0].append("M.4.I")
    ncats["M.4.I"] = {
        "title": "Indirect N2O Emissions From Managed Soils",
        "children": [["M.4.1.a", "M.4.1.b"]],
    }
    ncats["M.4.1.a"] = {"title": "Atmospheric Deposition"}
    ncats["M.4.1.b"] = {"title": "Nitrogen Leaching and Run-Off"}

    # Table4(v)
    ncats["4(V)"] = {
        "title": "LULUCF: Biomass Burning (Table 4(V))",
        "children": [
            ["4(V).A", "4(V).B", "4(V).C", "4(V).D", "4(V).E", "4(V).F", "4(V).H"]
        ],
    }
    # Forest Land
    ncats["4(V).A"] = {
        "title": "Forest Land",
        "children": [["4(V).A.1", "4(V).A.2"]],
    }
    ncats["4(V).A.1"] = {
        "title": "Forest Land Remaining Forest Land",
        "children": [["4(V).A.1.a", "4(V).A.1.b"]],
    }
    ncats["4(V).A.1.a"] = {"title": "Controlled Burning"}
    ncats["4(V).A.1.b"] = {"title": "Wildfires"}
    ncats["4(V).A.2"] = {
        "title": "Land Converted to Forest Land",
        "children": [["4(V).A.2.a", "4(V).A.2.b"]],
    }
    ncats["4(V).A.2.a"] = {"title": "Controlled Burning"}
    ncats["4(V).A.2.b"] = {"title": "Wildfires"}
    # Cropland
    ncats["4(V).B"] = {
        "title": "Cropland",
        "children": [["4(V).B.1", "4(V).B.2"]],
    }
    ncats["4(V).B.1"] = {
        "title": "Cropland Remaining Cropland",
        "children": [["4(V).B.1.a", "4(V).B.1.b"]],
    }
    ncats["4(V).B.1.a"] = {"title": "Controlled Burning"}
    ncats["4(V).B.1.b"] = {"title": "Wildfires"}
    ncats["4(V).B.2"] = {
        "title": "Land Converted to Cropland",
        "children": [["4(V).B.2.a", "4(V).B.2.b"]],
    }
    ncats["4(V).B.2.a"] = {"title": "Controlled Burning"}
    ncats["4(V).B.2.b"] = {"title": "Wildfires"}
    # Grassland
    ncats["4(V).C"] = {
        "title": "Grassland",
        "children": [["4(V).C.1", "4(V).C.2"]],
    }
    ncats["4(V).C.1"] = {
        "title": "Grassland Remaining Grassland",
        "children": [["4(V).C.1.a", "4(V).C.1.b"]],
    }
    ncats["4(V).C.1.a"] = {"title": "Controlled Burning"}
    ncats["4(V).C.1.b"] = {"title": "Wildfires"}
    ncats["4(V).C.2"] = {
        "title": "Land Converted to Grassland",
        "children": [["4(V).C.2.a", "4(V).C.2.b"]],
    }
    ncats["4(V).C.2.a"] = {"title": "Controlled Burning"}
    ncats["4(V).C.2.b"] = {"title": "Wildfires"}
    # Wetlands
    ncats["4(V).D"] = {
        "title": "Wetlands",
        "children": [["4(V).D.1", "4(V).D.2"]],
    }
    ncats["4(V).D.1"] = {
        "title": "Wetlands Remaining Wetlands",
        "children": [["4(V).D.1.a", "4(V).D.1.b"]],
    }
    ncats["4(V).D.1.a"] = {"title": "Controlled Burning"}
    ncats["4(V).D.1.b"] = {"title": "Wildfires"}
    ncats["4(V).D.2"] = {
        "title": "Land Converted to Wetlands",
        "children": [["4(V).D.2.a", "4(V).D.2.b"]],
    }
    ncats["4(V).D.2.a"] = {"title": "Controlled Burning"}
    ncats["4(V).D.2.b"] = {"title": "Wildfires"}
    # Settlements (no subsectors in CRF table templates)
    ncats["4(V).E"] = {
        "title": "Settlements",
        "children": [["4(V).E.1", "4(V).E.2"]],
    }
    ncats["4(V).E.1"] = {
        "title": "Settlements Remaining Settlements",
        "children": [["4(V).E.1.a", "4(V).E.1.b"]],
    }
    ncats["4(V).E.1.a"] = {"title": "Controlled Burning"}
    ncats["4(V).E.1.b"] = {"title": "Wildfires"}
    ncats["4(V).E.2"] = {
        "title": "Land Converted to Settlements",
        "children": [["4(V).E.2.a", "4(V).E.2.b"]],
    }
    ncats["4(V).E.2.a"] = {"title": "Controlled Burning"}
    ncats["4(V).E.2.b"] = {"title": "Wildfires"}
    # Other Land (no subsectors in CRF table templates)
    ncats["4(V).F"] = {
        "title": "Other Land",
        "children": [["4(V).F.1", "4(V).F.2"]],
    }
    ncats["4(V).F.1"] = {
        "title": "Other Land Remaining Other Land",
        "children": [["4(V).F.1.a", "4(V).F.1.b"]],
    }
    ncats["4(V).F.1.a"] = {"title": "Controlled Burning"}
    ncats["4(V).F.1.b"] = {"title": "Wildfires"}
    ncats["4(V).F.2"] = {
        "title": "Land Converted to Other Land",
        "children": [["4(V).F.2.a", "4(V).F.2.b"]],
    }
    ncats["4(V).F.2.a"] = {"title": "Controlled Burning"}
    ncats["4(V).F.2.b"] = {"title": "Wildfires"}
    # Other
    ncats["4(V).H"] = {"title": "Other (Please Specify)"}

    # Table 4.Gs1 - Harvested Wood Products
    ncats["4.G"]["children"] = [["4.GA"], ["4.GB"], ["4.GC"]]
    # Approach A
    ncats["4.GA"] = {
        "title": "Harvested Wood Products - Approach A",
        "children": [["4.GA.1"]],
    }
    ncats["4.GA.1"] = {
        "title": "Total HWP consumed domestically",
        "children": [[f"4.GA.1.{i}" for i in range(1, 4)]],
    }
    ncats["4.GA.1.1"] = {
        "title": "Solid Wood",
        "children": [[f"4.GA.1.1.{x}" for x in "abc"]],
    }
    ncats["4.GA.1.1.a"] = {"title": "Sawnwood"}
    ncats["4.GA.1.1.b"] = {"title": "Wood Panels"}
    ncats["4.GA.1.1.c"] = {"title": "Other Wood Products"}
    ncats["4.GA.1.2"] = {"title": "Paper and Paperboard"}
    ncats["4.GA.1.3"] = {"title": "Other (Please Specify)"}
    # Approach B
    ncats["4.GB"] = {
        "title": "Harvested Wood Products - Approach B",
        "children": [[f"4.GB.{i}" for i in range(1, 4)]],
    }
    ncats["4.GB.1"] = {
        "title": "Total HWP from domestic harvest",
        "children": [[f"4.GB.1.{i}" for i in range(1, 4)]],
    }
    ncats["4.GB.1.1"] = {
        "title": "Solid Wood",
        "children": [[f"4.GB.1.1.{x}" for x in "abc"]],
    }
    ncats["4.GB.1.1.a"] = {"title": "Sawnwood"}
    ncats["4.GB.1.1.b"] = {"title": "Wood Panels"}
    ncats["4.GB.1.1.c"] = {"title": "Other Wood Products"}
    ncats["4.GB.1.2"] = {"title": "Paper and Paperboard"}
    ncats["4.GB.1.3"] = {"title": "Other (Please Specify)"}
    ncats["4.GB.2"] = {
        "title": "HWP produced and consumed domestically",
        "children": [[f"4.GB.2.{i}" for i in range(1, 4)]],
    }
    ncats["4.GB.2.1"] = {
        "title": "Solid Wood",
        "children": [[f"4.GB.2.1.{x}" for x in "abc"]],
    }
    ncats["4.GB.2.1.a"] = {"title": "Sawnwood"}
    ncats["4.GB.2.1.b"] = {"title": "Wood Panels"}
    ncats["4.GB.2.1.c"] = {"title": "Other Wood Products"}
    ncats["4.GB.2.2"] = {"title": "Paper and Paperboard"}
    ncats["4.GB.2.3"] = {"title": "Other (Please Specify)"}
    ncats["4.GB.3"] = {
        "title": "HWP produced and exported",
        "children": [[f"4.GB.3.{i}" for i in range(1, 4)]],
    }
    ncats["4.GB.3.1"] = {
        "title": "Solid Wood",
        "children": [[f"4.GB.3.1.{x}" for x in "abc"]],
    }
    ncats["4.GB.3.1.a"] = {"title": "Sawnwood"}
    ncats["4.GB.3.1.b"] = {"title": "Wood Panels"}
    ncats["4.GB.3.1.c"] = {"title": "Other Wood Products"}
    ncats["4.GB.3.2"] = {"title": "Paper and Paperboard"}
    ncats["4.GB.3.3"] = {"title": "Other (Please Specify)"}
    # Approach C (no emissions in subsectors)
    ncats["4.GC"] = {
        "title": "Harvested Wood Products - Approach C",
        "children": [["4.GC.1"]],
    }
    ncats["4.GC.1"] = {
        "title": "Total",
        "children": [[f"4.GC.1.{i}" for i in range(1, 4)]],
    }
    ncats["4.GC.1.1"] = {
        "title": "Solid Wood",
        "children": [[f"4.GC.1.1.{x}" for x in "abc"]],
    }
    ncats["4.GC.1.1.a"] = {"title": "Sawnwood"}
    ncats["4.GC.1.1.b"] = {"title": "Wood Panels"}
    ncats["4.GC.1.1.c"] = {"title": "Other Wood Products"}
    ncats["4.GC.1.2"] = {"title": "Paper and Paperboard"}
    ncats["4.GC.1.3"] = {"title": "Other (Please Specify)"}
    # information items are ignored for now

    # Table 4.Gs2 - Do not read

    # Table5 - Waste
    # remove Waste as category 4 as it's category 5 in the CRF tables
    cats_to_remove = [cat for cat in cats.keys() if cat[0] in ["4", "5"]]
    for cat in cats_to_remove:
        del cats[cat]

    ncats["5"] = {
        "title": "Waste",
        "children": [[f"5.{x}" for x in "ABCDE"]],
    }
    ncats["5.A"] = {
        "title": "Solid Waste Disposal",
        "children": [[f"5.A.{i}" for i in range(1, 4)]],
    }
    ncats["5.A.1"] = {"title": "Managed Waste Disposal Sites"}
    ncats["5.A.2"] = {"title": "Unmanaged Waste Disposal Sites"}
    ncats["5.A.3"] = {"title": "Uncategorized Waste Disposal Sites"}
    ncats["5.B"] = {
        "title": "Biological Treatment of Solid Waste",
        "children": [["5.B.1", "5.B.2"]],
    }
    ncats["5.B.1"] = {"title": "Composting"}
    ncats["5.B.2"] = {"title": "Anaerobic Digestion at Biogas Facilities"}
    ncats["5.C"] = {
        "title": "Incineration and Open Burning of Waste",
        "children": [["5.C.1", "5.C.2"]],
    }
    ncats["5.C.1"] = {"title": "Waste Incineration"}
    ncats["5.C.2"] = {"title": "Open Burning of Waste"}
    ncats["5.D"] = {
        "title": "Wastewater Treatment and Discharge",
        "children": [[f"5.D.{i}" for i in range(1, 4)]],
    }
    ncats["5.D.1"] = {"title": "Domestic Wastewater"}
    ncats["5.D.2"] = {"title": "Industrial Wastewater"}
    ncats["5.D.3"] = {"title": "Other"}
    ncats["5.E"] = {"title": "Other (please specify)"}
    ncats["M.Memo"]["children"][0].append("M.Memo.LTSW")
    ncats["M.Memo.LTSW"] = {"title": "Long Term Storage of C in Waste Disposal Sites"}
    ncats["M.Memo"]["children"][0].append("M.Memo.ACLT")
    ncats["M.Memo.ACLT"] = {"title": "Annual Change in Long-Term Storage"}
    ncats["M.Memo"]["children"][0].append("M.Memo.ACLTHWP")
    ncats["M.Memo.ACLTHWP"] = {
        "title": "Annual Change in Total Long-Term C Storage in HWP Waste"
    }

    # Table 5.A - Solid Waste Disposal
    ncats["5.A.1"]["children"] = [["5.A.1.a", "5.A.1.b"]]
    ncats["5.A.1.a"] = {"title": "Anaerobic"}
    ncats["5.A.1.b"] = {"title": "Semi-Aerobic"}

    # Table 5.B - Biological Treatment of Solid Waste
    ncats["5.B.1"]["children"] = [["5.B.1.a", "5.B.1.b"]]
    ncats["5.B.1.a"] = {"title": "Municipal Solid Waste"}
    ncats["5.B.1.b"] = {"title": "Other (please specify)"}
    ncats["5.B.2"]["children"] = [["5.B.2.a", "5.B.2.b"]]
    ncats["5.B.2.a"] = {"title": "Municipal Solid Waste"}
    ncats["5.B.2.b"] = {"title": "Other (Please Specify)"}

    # Table 5.C - Waste Incineration
    ncats["5.C.1"]["children"] = [["5.C.1.a", "5.C.1.b"]]
    ncats["5.C.1.a"] = {
        "title": "Biogenic",
        "children": [["5.C.1.a.i", "5.C.1.a.ii"]],
    }
    ncats["5.C.1.a.i"] = {"title": "Municipal Solid Waste"}
    ncats["5.C.1.a.ii"] = {
        "title": "Other (please specify)",
        "children": [
            [
                "5.C.1.a.ii.1",
                "5.C.1.a.ii.2",
                "5.C.1.a.ii.3",
                "5.C.1.a.ii.4",
                "5.C.1.a.ii.5",
            ]
        ],
    }
    ncats["5.C.1.a.ii.1"] = {"title": "Industrial Solid Waste"}
    ncats["5.C.1.a.ii.2"] = {"title": "Hazardous Waste"}
    ncats["5.C.1.a.ii.3"] = {"title": "Clinical Waste"}
    ncats["5.C.1.a.ii.4"] = {"title": "Sewage Sludge"}
    ncats["5.C.1.a.ii.5"] = {"title": "Other (Please Specify)"}
    ncats["5.C.1.b"] = {
        "title": "Non-Biogenic",
        "children": [["5.C.1.b.i", "5.C.1.b.ii"]],
    }
    ncats["5.C.1.b.i"] = {"title": "Municipal Solid Waste"}
    ncats["5.C.1.b.ii"] = {
        "title": "Other (please specify)",
        "children": [
            [
                "5.C.1.b.ii.1",
                "5.C.1.b.ii.2",
                "5.C.1.b.ii.3",
                "5.C.1.b.ii.4",
                "5.C.1.b.ii.5",
            ]
        ],
    }
    ncats["5.C.1.b.ii.1"] = {"title": "Industrial Solid Waste"}
    ncats["5.C.1.b.ii.2"] = {"title": "Hazardous Waste"}
    ncats["5.C.1.b.ii.3"] = {"title": "Clinical Waste"}
    ncats["5.C.1.b.ii.4"] = {"title": "Sewage Sludge"}
    ncats["5.C.1.b.ii.5"] = {"title": "Other (Please Specify)"}
    # open burning
    ncats["5.C.2"]["children"] = [["5.C.2.a", "5.C.2.b"]]
    ncats["5.C.2.a"] = {
        "title": "Biogenic",
        "children": [["5.C.2.a.i", "5.C.2.a.ii"]],
    }
    ncats["5.C.2.a.i"] = {"title": "Municipal Solid Waste"}
    ncats["5.C.2.a.ii"] = {"title": "Other (please specify)"}
    ncats["5.C.2.b"] = {
        "title": "Non-Biogenic",
        "children": [["5.C.2.b.i", "5.C.2.b.ii"]],
    }
    ncats["5.C.2.b.i"] = {"title": "Municipal Solid Waste"}
    ncats["5.C.2.b.ii"] = {"title": "Other (please specify)"}

    # Table 5.D - Wastewater Treatment and Discharge
    # no new sectors

    # Tables Summary1.As1-3
    del cats["0"]
    ncats["0"] = {
        "title": "Total National Emissions and Removals",
        "children": [["1", "2", "3", "4", "5"]],
    }

    ncats["M.Memo"]["children"][0].append("M.Memo.IndN2O")
    ncats["M.Memo.IndN2O"] = {"title": "Indirect N2O"}
    ncats["M.Memo"]["children"][0].append("M.Memo.IndCO2")
    ncats["M.Memo.IndCO2"] = {"title": "Indirect CO2"}

    for ncode in ncats:
        if "." in ncode:
            ncats[ncode]["alternative_codes"] = [
                ncode.replace(".", " "),
                ncode.replace(".", ""),
            ]

    cats.update(ncats)

    CRF2013 = climate_categories.HierarchicalCategorization.from_spec(spec)

    CRF2013.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
