"""Run this via `make climate_categories/data/CRF1999.yaml` in the main
directory."""

import pathlib

import climate_categories

OUTPATH = pathlib.Path("./climate_categories/data/CRF1999.yaml")


def main():
    """Create the CRF1999 categorization from the IPCC1996 categorization, which was
    also used by the UNFCCC to develop CRF1999. However, we can't use extend() and
    CRF1999 is not considered an extension of IPCC1996, because some codes were
    re-used for other categories.

    The CRF1999 categorization contains categories without codes. For new sets of
    categories, I formed codes as usual. However, some categories are inserted at parts
    of the hierarchy where this is not possible. For those, I
    generate codes from the parent codes plus a dash followed by the first three letters
    of the category title. Better than nothing.
    """
    spec = climate_categories.IPCC1996.to_spec()

    # Metadata
    spec["name"] = "CRF1999"
    spec["title"] = "Common Reporting Format GHG emissions categories (1999)"
    spec["comment"] = (
        "Classification of green-house gas emissions and removals into"
        " categories for use in annual inventories using the Common"
        " Reporting Format as specified in the UNFCCC guidelines on"
        " reporting"
        " and review as decided in the fifth session of the Conference of"
        " the Parties in 1999"
    )
    spec["references"] = (
        "United Nations 2000, Review of the Implementation of"
        " Commitments and of Other Provisions of the Convention,"
        " Annex Common Reporting Format, UNDOC FCCC/CP/1999/7, pages"
        " 15ff, https://undocs.org/en/FCCC/CP/1999/7"
    )
    spec["institution"] = "UN"
    spec["last_update"] = "1999-11-05"
    spec["version"] = "1999"
    spec["total_sum"] = True
    spec["canonical_top_level_category"] = "0"

    # Changes in categories
    cats = spec["categories"]
    ncats = {}

    # page 32 - reference approach is an alternative to sectoral approach
    ncats["1.A-ref"] = {
        "title": "Reference Approach",
        "children": [["1.A-ref.1", "1.A-ref.2"]],
    }
    cats["1.A"]["children"].append(["1.A-ref"])

    ncats["1.A-ref.1"] = {
        "title": "Fossil Fuel",
        "children": [["1.A-ref.1.a", "1.A-ref.1.b", "1.A-ref.1.c"]],
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
    ncats["1.A-ref.1.a.ii.7"] = {"title": "LPG"}
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
        "children": [[f"1.A-ref.1.b.i.{x}" for x in range(1, 8)]],
    }
    ncats["1.A-ref.1.b.i.1"] = {"title": "Anthracite"}
    ncats["1.A-ref.1.b.i.2"] = {"title": "Coking Coal"}
    ncats["1.A-ref.1.b.i.3"] = {"title": "Other Bituminous Coal"}
    ncats["1.A-ref.1.b.i.4"] = {"title": "Sub-bituminous coal"}
    ncats["1.A-ref.1.b.i.5"] = {"title": "Lignite"}
    ncats["1.A-ref.1.b.i.6"] = {"title": "Oil Shale"}
    ncats["1.A-ref.1.b.i.7"] = {"title": "Peat"}

    ncats["1.A-ref.1.b.ii"] = {
        "title": "Secondary Fuels",
        "children": [["1.A-ref.1.b.ii.1", "1.A-ref.1.b.ii.2"]],
    }
    ncats["1.A-ref.1.b.ii.1"] = {"title": "BKB & Patent Fuel"}
    ncats["1.A-ref.1.b.ii.2"] = {"title": "Coke Oven / Gas Coke"}

    ncats["1.A-ref.1.c"] = {"title": "Gaseous Fossil", "children": [["1.A-ref.1.c.i"]]}
    ncats["1.A-ref.1.c.i"] = {"title": "Natural Gas (Dry)"}

    ncats["1.A-ref.2"] = {
        "title": "Biomass",
        "children": [["1.A-ref.2.a", "1.A-ref.2.b", "1.A-ref.2.c"]],
    }
    ncats["1.A-ref.2.a"] = {"title": "Solid Biomass"}
    ncats["1.A-ref.2.b"] = {"title": "Liquid Biomass"}
    ncats["1.A-ref.2.c"] = {"title": "Gas Biomass"}

    # page 36
    ncats["1.B.2.b-exp"] = {"title": "Exploration"}
    ncats["1.B.2.b-dis"] = {"title": "Distribution"}
    cats["1.B.2.b"]["children"] = [
        ["1.B.2.b-exp", "1.B.2.b.i", "1.B.2.b.ii", "1.B.2.b-dis", "1.B.2.b.iii"]
    ]

    ncats["1.B.2.b.iii.1"] = {"title": "at industrial plants and power stations"}
    ncats["1.B.2.b.iii.2"] = {"title": "in residential and commercial sectors"}
    cats["1.B.2.b.iii"]["children"] = [["1.B.2.b.iii.1", "1.B.2.b.iii.2"]]

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
    cats["1.B.2.c"]["children"] = [["1.B.2.c-ven", "1.B.2.c-fla"]]
    for cat in ("1.B.2.c.i", "1.B.2.c.ii", "1.B.2.c.iii"):
        del cats[cat]

    ncats["1.B.2.d"] = {"title": "Other"}
    cats["1.B.2"]["children"][0].append("1.B.2.d")

    # page 39
    ncats["2.E.1.a"] = {"title": "Production of HCFC-22"}
    ncats["2.E.1.b"] = {"title": "Other"}
    cats["2.E.1"]["children"] = [["2.E.1.a", "2.E.1.b"]]

    # re-numbered
    cats["2.F.8"] = cats["2.F.6"]
    del cats["2.F.6"]
    cats["2.F.8"]["alternative_codes"] = ["2F8", "2 F 8"]

    cats["2.F.4"]["title"] = "Aerosols / Metered Dose Inhalers"
    ncats["2.F.6"] = {"title": "Semiconductor Manufacture"}
    ncats["2.F.7"] = {"title": "Electrical Equipment"}
    cats["2.F"]["children"] = [[f"2.F.{x}" for x in range(1, 9)]]

    # page 40
    ncats["2.A.7.a"] = {"title": "Glass Production"}
    ncats["2.A.7.b"] = {"title": "Other"}
    cats["2.A.7"]["children"] = [["2.A.7.a", "2.A.7.b"]]

    ncats["2.B.4.a"] = {"title": "Silicon Carbide"}
    ncats["2.B.4.b"] = {"title": "Calcium Carbide"}
    cats["2.B.4"]["children"] = [["2.B.4.a", "2.B.4.b"]]

    ncats["2.B.5.a"] = {"title": "Carbon Black"}
    ncats["2.B.5.b"] = {"title": "Ethylene"}
    ncats["2.B.5.c"] = {"title": "Dichloroethylene"}
    ncats["2.B.5.d"] = {"title": "Styrene"}
    ncats["2.B.5.e"] = {"title": "Methanol"}
    ncats["2.B.5.f"] = {"title": "Other"}
    cats["2.B.5"]["children"] = [[f"2.B.5.{x}" for x in "abcdef"]]

    # page 41
    ncats["2.C.1.a"] = {"title": "Steel"}
    ncats["2.C.1.b"] = {"title": "Pig Iron"}
    ncats["2.C.1.c"] = {"title": "Sinter"}
    ncats["2.C.1.d"] = {"title": "Coke"}
    ncats["2.C.1.e"] = {"title": "Other"}
    cats["2.C.1"]["children"] = [[f"2.C.1.{x}" for x in "abcde"]]

    # page 42
    ncats["2.C.4.a"] = {"title": "SF6 used in Aluminium Foundries"}
    ncats["2.C.4.b"] = {"title": "SF6 used in Magnesium Foundries"}
    cats["2.C.4"]["children"] = [["2.C.4.a", "2.C.4.b"]]

    # Page 45
    ncats["2.F.1.a"] = {"title": "Domestic Refrigeration"}
    ncats["2.F.1.b"] = {"title": "Commercial Refrigeration"}
    ncats["2.F.1.c"] = {"title": "Transport Refrigeration"}
    ncats["2.F.1.d"] = {"title": "Industrial Refrigeration"}
    ncats["2.F.1.e"] = {"title": "Stationary Air-Conditioning"}
    ncats["2.F.1.f"] = {"title": "Mobile Air-Conditioning"}
    cats["2.F.1"]["children"] = [[f"2.F.1.{x}" for x in "abcdef"]]

    ncats["2.F.2.a"] = {"title": "Hard Foam"}
    ncats["2.F.2.b"] = {"title": "Soft Foam"}
    cats["2.F.2"]["children"] = [["2.F.2.a", "2.F.2.b"]]

    # Page 46
    ncats["2.F.4.a"] = {"title": "Metered Dose Inhalers"}
    ncats["2.F.4.b"] = {"title": "Other"}
    cats["2.F.4"]["children"] = [["2.F.4.a", "2.F.4.b"]]

    # Page 47
    ncats["3.D.1"] = {"title": "Use of N2O for Anaesthesia"}
    ncats["3.D.2"] = {"title": "N2O from Fire Extinguishers"}
    ncats["3.D.3"] = {"title": "N2O from Aerosol Cans"}
    ncats["3.D.4"] = {"title": "Other Use of N2O"}
    ncats["3.D.5"] = {"title": "Other"}
    cats["3.D"]["children"] = [[f"3.D.{x}" for x in range(1, 6)]]

    # Page 55
    ncats["4.D.1"] = {
        "title": "Direct Soil Emissions",
        "children": [[f"4.D.1.{x}" for x in "abcde"]],
    }
    ncats["4.D.1.a"] = {"title": "Synthetic Fertilizers"}
    ncats["4.D.1.b"] = {"title": "Animal Wastes Applied to Soils"}
    ncats["4.D.1.c"] = {"title": "N-fixing Crops"}
    ncats["4.D.1.d"] = {"title": "Crop Residue"}
    ncats["4.D.1.e"] = {"title": "Cultivation of Histosols"}

    ncats["4.D.2"] = {"title": "Animal Production"}

    ncats["4.D.3"] = {
        "title": "Indirect Emissions",
        "children": [["4.D.3.a", "4.D.3.b"]],
    }
    ncats["4.D.3.a"] = {"title": "Atmospheric Deposition"}
    ncats["4.D.3.b"] = {"title": "Nitrogen Leaching and Run-off"}
    ncats["4.D.4"] = {"title": "Other"}

    cats["4.D"]["children"] = [["4.D.1", "4.D.2", "4.D.3", "4.D.4"]]

    # Page 57
    ncats["4.F.1.a"] = {"title": "Wheat"}
    ncats["4.F.1.b"] = {"title": "Barley"}
    ncats["4.F.1.c"] = {"title": "Maize"}
    ncats["4.F.1.d"] = {"title": "Oats"}
    ncats["4.F.1.e"] = {"title": "Rye"}
    ncats["4.F.1.f"] = {"title": "Rice"}
    ncats["4.F.1.g"] = {"title": "Other"}
    cats["4.F.1"]["children"] = [[f"4.F.1.{x}" for x in "abcdefg"]]

    ncats["4.F.2.a"] = {"title": "Dry bean"}
    ncats["4.F.2.b"] = {"title": "Peas"}
    ncats["4.F.2.c"] = {"title": "Soybeans"}
    ncats["4.F.2.d"] = {"title": "Other"}
    cats["4.F.2"]["children"] = [[f"4.F.2.{x}" for x in "abcd"]]

    ncats["4.F.3.a"] = {"title": "Potatoes"}
    ncats["4.F.3.b"] = {"title": "Other"}
    cats["4.F.3"]["children"] = [["4.F.3.a", "4.F.3.b"]]

    # Page 58ff
    # changed a lot, re-do completely
    for cat in (
        "5.A",
        "5.A.1",
        "5.A.1.a",
        "5.A.1.b",
        "5.A.1.c",
        "5.A.1.d",
        "5.A.1.e",
        "5.A.1.f",
        "5.A.1.g",
        "5.A.1.h",
        "5.A.2",
        "5.A.2.a",
        "5.A.2.b",
        "5.A.2.c",
        "5.A.2.d",
        "5.A.3",
        "5.A.3.a",
        "5.A.3.b",
        "5.A.3.c",
        "5.A.4",
        "5.A.5",
    ):
        del cats[cat]

    ncats["5.A"] = {
        "title": "Changes in Forest and Other Woody Biomass Stocks",
        "children": [["5.A.1", "5.A.2", "5.A.3", "5.A.4", "5.A.5"]],
    }
    ncats["5.A.1"] = {
        "title": "Tropical",
        "children": [["5.A.1.a", "5.A.1.b", "5.A.1.c"]],
    }

    ncats["5.A.1.a"] = {
        "title": "Plantations",
        "children": [
            [
                f"5.A.1.a.{x}"
                for x in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix")
            ]
        ],
    }
    ncats["5.A.1.a.i"] = {"title": "Acacia spp."}
    ncats["5.A.1.a.ii"] = {"title": "Eucalyptus spp."}
    ncats["5.A.1.a.iii"] = {"title": "Tectona grandis"}
    ncats["5.A.1.a.iv"] = {"title": "Pinus spp"}
    ncats["5.A.1.a.v"] = {"title": "Pinus caribaea"}
    ncats["5.A.1.a.vi"] = {"title": "Mixed Hardwoods"}
    ncats["5.A.1.a.vii"] = {"title": "Mixed Fast-Growing Hardwoods"}
    ncats["5.A.1.a.viii"] = {"title": "Mixed Softwoods"}
    ncats["5.A.1.a.ix"] = {"title": "Other"}

    ncats["5.A.1.b"] = {
        "title": "Other Forests",
        "children": [["5.A.1.b.i", "5.A.1.b.ii", "5.A.1.b.iii"]],
    }
    ncats["5.A.1.b.i"] = {"title": "Moist"}
    ncats["5.A.1.b.ii"] = {"title": "Seasonal"}
    ncats["5.A.1.b.iii"] = {"title": "Dry"}

    ncats["5.A.1.c"] = {"title": "Other"}

    ncats["5.A.2"] = {
        "title": "Temperate",
        "children": [["5.A.2.a", "5.A.2.b", "5.A.2.c"]],
    }
    ncats["5.A.2.a"] = {"title": "Plantations"}

    ncats["5.A.2.b"] = {
        "title": "Commercial",
        "children": [["5.A.2.b.i", "5.A.2.b.ii"]],
    }
    ncats["5.A.2.b.i"] = {"title": "Evergreen"}
    ncats["5.A.2.b.ii"] = {"title": "Deciduous"}

    ncats["5.A.2.c"] = {"title": "Other"}

    ncats["5.A.3"] = {"title": "Boreal"}
    ncats["5.A.4"] = {"title": "Grasslands / Tundra"}

    ncats["5.A.5"] = {"title": "Other", "children": [["5.A.5.a", "5.A.5.b"]]}
    ncats["5.A.5.a"] = {"title": "Harvested Wood"}
    ncats["5.A.5.b"] = {"title": "Other"}

    # Page 58
    ncats["5.D.1"] = {"title": "Cultivation of Mineral Soils"}
    ncats["5.D.2"] = {"title": "Cultivation of Organic Soils"}
    ncats["5.D.3"] = {"title": "Liming of Agricultural Soils"}
    ncats["5.D.4"] = {"title": "Forest Soils"}
    ncats["5.D.5"] = {"title": "Other"}
    cats["5.D"]["children"] = [[f"5.D.{x}" for x in range(1, 6)]]

    # Page 60
    ncats["5.B-tro"] = {"title": "Tropical Savanna / Grasslands"}
    ncats["5.B-gra"] = {"title": "Grasslands"}
    cats["5.B"]["children"][0].append("5.B-tro")
    cats["5.B"]["children"][0].append("5.B-gra")

    ncats["5.B.2-mix"] = {"title": "Mixed Broadleaf / Coniferous"}
    cats["5.B.2"]["children"][0].append("5.B.2-mix")

    # Page 61
    ncats["5.C-tro"] = {"title": "Tropical Savanna / Grasslands"}
    ncats["5.C-gra"] = {"title": "Grasslands"}
    cats["5.C"]["children"][0].append("5.C-tro")
    cats["5.C"]["children"][0].append("5.C-gra")

    ncats["5.C.1.a"] = {"title": "Wet / Very Moist"}
    ncats["5.C.1.b"] = {"title": "Moist, short dry season"}
    ncats["5.C.1.c"] = {"title": "Moist, long dry season"}
    ncats["5.C.1.d"] = {"title": "Dry"}
    ncats["5.C.1.e"] = {"title": "Montane Moist"}
    ncats["5.C.1.f"] = {"title": "Montane Dry"}
    cats["5.C.1"]["children"] = [[f"5.C.1.{x}" for x in "abcdef"]]

    for parent in ("5.C.2", "5.C.3"):
        ncats[f"{parent}.a"] = {"title": "Mixed Broadleaf / Coniferous"}
        ncats[f"{parent}.b"] = {"title": "Coniferous"}
        ncats[f"{parent}.c"] = {"title": "Broadleaf"}
        cats[parent]["children"] = [[f"{parent}.{x}" for x in "abc"]]

    # Page 62
    ncats["5.D.1"]["children"] = [[f"5.D.1.{x}" for x in "abcdef"]]
    ncats["5.D.1.a"] = {"title": "High Activity Soils"}
    ncats["5.D.1.b"] = {"title": "Low Activity Soils"}
    ncats["5.D.1.c"] = {"title": "Sandy"}
    ncats["5.D.1.d"] = {"title": "Volcanic"}
    ncats["5.D.1.e"] = {"title": "Wetland (Aquic)"}
    ncats["5.D.1.f"] = {"title": "Other"}

    ncats["5.D.2"]["children"] = [["5.D.2.a", "5.D.2.b", "5.D.2.c"]]
    ncats["5.D.2.a"] = {
        "title": "Cool Temperate",
        "children": [["5.D.2.a.i", "5.D.2.a.ii"]],
    }
    ncats["5.D.2.a.i"] = {"title": "Upland Crops"}
    ncats["5.D.2.a.ii"] = {"title": "Pasture/Forest"}
    ncats["5.D.2.b"] = {
        "title": "Warm Temperate",
        "children": [["5.D.2.b.i", "5.D.2.b.ii"]],
    }
    ncats["5.D.2.b.i"] = {"title": "Upland Crops"}
    ncats["5.D.2.b.ii"] = {"title": "Pasture/Forest"}
    ncats["5.D.2.c"] = {"title": "Tropical", "children": [["5.D.2.c.i", "5.D.2.c.ii"]]}
    ncats["5.D.2.c.i"] = {"title": "Upland Crops"}
    ncats["5.D.2.c.ii"] = {"title": "Pasture/Forest"}

    ncats["5.D.3"]["children"] = [["5.D.3.a", "5.D.3.b"]]
    ncats["5.D.3.a"] = {"title": "Limestone"}
    ncats["5.D.3.b"] = {"title": "Dolomite"}

    # Page 64
    ncats["6.A.2.a"] = {"title": "deep (>5 m)"}
    ncats["6.A.2.b"] = {"title": "shallow (<5 m)"}
    cats["6.A.2"]["children"] = [["6.A.2.a", "6.A.2.b"]]

    ncats["6.C.1"] = {"title": "biogenic"}
    ncats["6.C.2"] = {"title": "plastics"}
    ncats["6.C.3"] = {"title": "other"}
    cats["6.C"]["children"] = [["6.C.1", "6.C.2", "6.C.3"]]

    # Pages 66ff
    ncats["0"] = {
        "title": "Total National Emissions and Removals",
        "children": [["1", "2", "3", "4", "5", "6", "7"]],
    }
    ncats["M.Memo"] = {
        "title": "Memo Items",
        "children": [["M.Memo.Int", "M.Memo.Mult", "M.Memo.Bio"]],
    }
    ncats["M.Memo.Int"] = {
        "title": "International Bunkers",
        "children": [["M.Memo.Int.Avi", "M.Memo.Int.Mar"]],
    }
    ncats["M.Memo.Int.Avi"] = {"title": "Aviation"}
    ncats["M.Memo.Int.Mar"] = {"title": "Marine"}
    ncats["M.Memo.Mult"] = {"title": "Multilateral Operations"}
    ncats["M.Memo.Bio"] = {"title": "CO2 Emissions from Biomass"}

    for ncode in ncats:
        if "." in ncode:
            ncats[ncode]["alternative_codes"] = [
                ncode.replace(".", " "),
                ncode.replace(".", ""),
            ]

    cats.update(ncats)

    CRF1999 = climate_categories.HierarchicalCategorization.from_spec(spec)

    CRF1999.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
