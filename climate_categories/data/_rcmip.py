spec = {
    "name": "RCMIP",
    "title": "Emissions categories from the Reduced Complexity Model Intercomparison Project (RCMIP)",
    "comment": "AFOLU in the SSPDb is AFOLU minus any agriculture\nrelated fossil fuel based emissions hence is not the same as the\nWG3 AFOLU definition. Rather AFOLU in the SSPDb is AFOLU as expected by\nMAGICC (i.e. exluding agriculture related fossil fuel use), hence\nwe call it MAGICC AFOLU.",
    "references": "Nicholls, Z. R. J., Meinshausen, M., Lewis, J., Gieseke, R., Dommenget, D., Dorheim, K., Fan, C.-S., Fuglestvedt, J. S., Gasser, T., Golüke, U., Goodwin, P., Hartin, C., Hope, A. P., Kriegler, E., Leach, N. J., Marchegiani, D., McBride, L. A., Quilcaille, Y., Rogelj, J., Salawitch, R. J., Samset, B. H., Sandstad, M., Shiklomanov, A. N., Skeie, R. B., Smith, C. J., Smith, S., Tanaka, K., Tsutsui, J., and Xie, Z.: Reduced Complexity Model Intercomparison Project Phase 1: introduction and evaluation of global-mean temperature response, Geosci. Model Dev., 13, 5175–5190, https://doi.org/10.5194/gmd-13-5175-2020, 2020.",
    "institution": "RCMIP",
    "last_update": "2020-09-21",
    "hierarchical": True,
    "version": "v5.1.0",
    "total_sum": True,
    "categories": {
        "Emissions": {
            "title": "RCMIP Emissions",
            "children": [
                [
                    "Emissions|BC",
                    "Emissions|CH4",
                    "Emissions|CO",
                    "Emissions|CO2",
                    "Emissions|F-Gases",
                    "Emissions|Montreal Gases",
                    "Emissions|N2O",
                    "Emissions|NH3",
                    "Emissions|NOx",
                    "Emissions|OC",
                    "Emissions|Sulfur",
                    "Emissions|VOC",
                ]
            ],
        },
        "Emissions|BC": {
            "title": "Black carbon emissions",
            "comment": "total black carbon emissions",
            "children": [
                [
                    "Emissions|BC|MAGICC AFOLU",
                    "Emissions|BC|MAGICC Fossil and Industrial",
                    "Emissions|BC|Other",
                ]
            ],
        },
        "Emissions|BC|MAGICC AFOLU": {
            "title": "Black carbon AFOLU emissions",
            "comment": "black carbon emissions from agriculture, forestry and other land use (IPCC category 3), excluding any fossil-fuel based emissions in the Agricultural sector (hence not identical to WG3 AFOLU)",
            "children": [[]],
        },
        "Emissions|BC|MAGICC Fossil and Industrial": {
            "title": "Black carbon fossil and industrial emissions",
            "comment": "black carbon emissions from energy use on supply and demand side (IPCC category 1A, 1B), industrial processes (IPCC category 2), waste (IPCC category 4) and other (IPCC category 5)",
            "children": [[]],
        },
        "Emissions|BC|Other": {
            "title": "Black carbon emissions from other sources",
            "comment": "black carbon emissions from other sources (please provide a definition)",
            "children": [[]],
        },
        "Emissions|CH4": {
            "title": "Methane emissions",
            "comment": "total methane emissions",
            "children": [
                [
                    "Emissions|CH4|MAGICC AFOLU",
                    "Emissions|CH4|MAGICC Fossil and Industrial",
                    "Emissions|CH4|Other",
                ]
            ],
        },
        "Emissions|CH4|MAGICC AFOLU": {
            "title": "Methane AFOLU emissions",
            "comment": "methane emissions from agriculture, forestry and other land use (IPCC category 3), excluding any fossil-fuel based emissions in the Agricultural sector (hence not identical to WG3 AFOLU)",
            "children": [[]],
        },
        "Emissions|CH4|MAGICC Fossil and Industrial": {
            "title": "Methane fossil and industrial emissions",
            "comment": "methane emissions from energy use on supply and demand side (IPCC category 1A, 1B), industrial processes (IPCC category 2), waste (IPCC category 4) and other (IPCC category 5)",
            "children": [[]],
        },
        "Emissions|CH4|Other": {
            "title": "Methane emissions from other sources",
            "comment": "methane emissions from other sources (please provide a definition)",
            "children": [[]],
        },
        "Emissions|CO": {
            "title": "Carbon monoxide emissions",
            "comment": "total carbon monoxide emissions",
            "children": [
                [
                    "Emissions|CO|MAGICC AFOLU",
                    "Emissions|CO|MAGICC Fossil and Industrial",
                    "Emissions|CO|Other",
                ]
            ],
        },
        "Emissions|CO|MAGICC AFOLU": {
            "title": "Carbon monoxide AFOLU emissions",
            "comment": "carbon monoxide emissions from agriculture, forestry and other land use (IPCC category 3), excluding any fossil-fuel based emissions in the Agricultural sector (hence not identical to WG3 AFOLU)",
            "children": [[]],
        },
        "Emissions|CO|MAGICC Fossil and Industrial": {
            "title": "Carbon monoxide fossil and industrial emissions",
            "comment": "carbon monoxide emissions from energy use on supply and demand side (IPCC category 1A, 1B), industrial processes (IPCC category 2), waste (IPCC category 4) and other (IPCC category 5)",
            "children": [[]],
        },
        "Emissions|CO|Other": {
            "title": "Carbon monoxide emissions from other sources",
            "comment": "carbon monoxide emissions from other sources (please provide a definition)",
            "children": [[]],
        },
        "Emissions|CO2": {
            "title": "Carbon dioxide emissions",
            "comment": "total carbon dioxide emissions",
            "children": [
                [
                    "Emissions|CO2|MAGICC AFOLU",
                    "Emissions|CO2|MAGICC Fossil and Industrial",
                    "Emissions|CO2|Other",
                ]
            ],
        },
        "Emissions|CO2|MAGICC AFOLU": {
            "title": "Carbon dioxide AFOLU emissions",
            "comment": "carbon dioxide emissions from agriculture, forestry and other land use (IPCC category 3), excluding any fossil-fuel based emissions in the Agricultural sector (hence not identical to WG3 AFOLU)",
            "children": [[]],
        },
        "Emissions|CO2|MAGICC Fossil and Industrial": {
            "title": "Carbon dioxide fossil and industrial emissions",
            "comment": "carbon dioxide emissions from energy use on supply and demand side (IPCC category 1A, 1B), industrial processes (IPCC category 2), waste (IPCC category 4) and other (IPCC category 5)",
            "children": [[]],
        },
        "Emissions|CO2|Other": {
            "title": "Carbon dioxide emissions from other sources",
            "comment": "carbon dioxide emissions from other sources (please provide a definition)",
            "children": [[]],
        },
        "Emissions|F-Gases": {
            "title": "F-gas emissions",
            "comment": "total F-gas emissions, including sulfur hexafluoride (SF6), nitrogen trifluoride (NF3), sulfuryl fluoride (SO2F2), hydrofluorocarbons (HFCs), perfluorocarbons (PFCs) ",
            "children": [
                [
                    "Emissions|F-Gases|HFC",
                    "Emissions|F-Gases|NF3",
                    "Emissions|F-Gases|PFC",
                    "Emissions|F-Gases|SF6",
                    "Emissions|F-Gases|SO2F2",
                ]
            ],
        },
        "Emissions|F-Gases|HFC": {
            "title": "Hydrofluorocarbons (HFCs and HCFCs) emissions",
            "comment": "equivalent species total emissions of hydrofluorocarbons (HFCs and HCFCs), provided as aggregate CO2-equivalents",
            "children": [
                [
                    "Emissions|F-Gases|HFC|HFC125",
                    "Emissions|F-Gases|HFC|HFC134a",
                    "Emissions|F-Gases|HFC|HFC143a",
                    "Emissions|F-Gases|HFC|HFC152a",
                    "Emissions|F-Gases|HFC|HFC227ea",
                    "Emissions|F-Gases|HFC|HFC23",
                    "Emissions|F-Gases|HFC|HFC236fa",
                    "Emissions|F-Gases|HFC|HFC245fa",
                    "Emissions|F-Gases|HFC|HFC32",
                    "Emissions|F-Gases|HFC|HFC365mfc",
                    "Emissions|F-Gases|HFC|HFC4310mee",
                ]
            ],
        },
        "Emissions|F-Gases|HFC|HFC125": {
            "title": "HFC125 emissions",
            "comment": "total emissions of HFC125",
            "children": [[]],
        },
        "Emissions|F-Gases|HFC|HFC134a": {
            "title": "HFC134a emissions",
            "comment": "total emissions of HFC134a",
            "children": [[]],
        },
        "Emissions|F-Gases|HFC|HFC143a": {
            "title": "HFC143a emissions",
            "comment": "total emissions of HFC143a",
            "children": [[]],
        },
        "Emissions|F-Gases|HFC|HFC152a": {
            "title": "HFC152a emissions",
            "comment": "total emissions of HFC152a",
            "children": [[]],
        },
        "Emissions|F-Gases|HFC|HFC227ea": {
            "title": "HFC227ea emissions",
            "comment": "total emissions of HFC227ea",
            "children": [[]],
        },
        "Emissions|F-Gases|HFC|HFC23": {
            "title": "HFC23 emissions",
            "comment": "total emissions of HFC23",
            "children": [[]],
        },
        "Emissions|F-Gases|HFC|HFC236fa": {
            "title": "HFC236fa emissions",
            "comment": "total emissions of HFC236fa",
            "children": [[]],
        },
        "Emissions|F-Gases|HFC|HFC245fa": {
            "title": "HFC245fa emissions",
            "comment": "total emissions of HFC245fa",
            "children": [[]],
        },
        "Emissions|F-Gases|HFC|HFC32": {
            "title": "HFC32 emissions",
            "comment": "total emissions of HFC32",
            "children": [[]],
        },
        "Emissions|F-Gases|HFC|HFC365mfc": {
            "title": "HFC365mfc emissions",
            "comment": "total emissions of HFC365mfc",
            "children": [[]],
        },
        "Emissions|F-Gases|HFC|HFC4310mee": {
            "title": "HFC43-10mee emissions",
            "comment": "total emissions of HFC43-10mee",
            "children": [[]],
        },
        "Emissions|F-Gases|NF3": {
            "title": "Nitrogen trifluoride emissions",
            "comment": "total emissions of nitrogen trifluoride (NF3)",
            "children": [[]],
        },
        "Emissions|F-Gases|PFC": {
            "title": "Perfluorocarbons  emissions",
            "comment": "equivalent species total emissions of perfluorocarbons (PFCs, as defined by Table 8.A.1 of AR5), provided as aggregate CF4-equivalents",
            "children": [
                [
                    "Emissions|F-Gases|PFC|C2F6",
                    "Emissions|F-Gases|PFC|C3F8",
                    "Emissions|F-Gases|PFC|C4F10",
                    "Emissions|F-Gases|PFC|C5F12",
                    "Emissions|F-Gases|PFC|C6F14",
                    "Emissions|F-Gases|PFC|C7F16",
                    "Emissions|F-Gases|PFC|C8F18",
                    "Emissions|F-Gases|PFC|cC4F8",
                    "Emissions|F-Gases|PFC|CF4",
                ]
            ],
        },
        "Emissions|F-Gases|PFC|C2F6": {
            "title": "C2F6 emissions",
            "comment": "total emissions of C2F6",
            "children": [[]],
        },
        "Emissions|F-Gases|PFC|C3F8": {
            "title": "C3F8 emissions",
            "comment": "total emissions of C3F8",
            "children": [[]],
        },
        "Emissions|F-Gases|PFC|C4F10": {
            "title": "C4F10 emissions",
            "comment": "total emissions of C4F10",
            "children": [[]],
        },
        "Emissions|F-Gases|PFC|C5F12": {
            "title": "C5F12 emissions",
            "comment": "total emissions of C5F12",
            "children": [[]],
        },
        "Emissions|F-Gases|PFC|C6F14": {
            "title": "C6F14 emissions",
            "comment": "total emissions of C6F14",
            "children": [[]],
        },
        "Emissions|F-Gases|PFC|C7F16": {
            "title": "C7F16 emissions",
            "comment": "total emissions of C7F16",
            "children": [[]],
        },
        "Emissions|F-Gases|PFC|C8F18": {
            "title": "C8F18 emissions",
            "comment": "total emissions of C8F18",
            "children": [[]],
        },
        "Emissions|F-Gases|PFC|cC4F8": {
            "title": "c-C4F8 emissions",
            "comment": "total emissions of c-C4F8",
            "children": [[]],
        },
        "Emissions|F-Gases|PFC|CF4": {
            "title": "CF4 emissions",
            "comment": "total emissions of CF4",
            "children": [[]],
        },
        "Emissions|F-Gases|SF6": {
            "title": "Sulfur hexafluoride emissions",
            "comment": "total emissions of sulfur hexafluoride (SF6)",
            "children": [[]],
        },
        "Emissions|F-Gases|SO2F2": {
            "title": "Sulfuryl fluoride emissions",
            "comment": "total emissions of sulfuryl fluoride (SO2F2)",
            "children": [[]],
        },
        "Emissions|Montreal Gases": {
            "title": "Montreal gas emissions",
            "comment": "equivalent species total Montreal gas emissions, provided as CFC-11 equivalents",
            "children": [
                [
                    "Emissions|Montreal Gases|CCl4",
                    "Emissions|Montreal Gases|CFC",
                    "Emissions|Montreal Gases|CH2Cl2",
                    "Emissions|Montreal Gases|CH3Br",
                    "Emissions|Montreal Gases|CH3CCl3",
                    "Emissions|Montreal Gases|CH3Cl",
                    "Emissions|Montreal Gases|CHCl3",
                    "Emissions|Montreal Gases|Halon1202",
                    "Emissions|Montreal Gases|Halon1211",
                    "Emissions|Montreal Gases|Halon1301",
                    "Emissions|Montreal Gases|Halon2402",
                    "Emissions|Montreal Gases|HCFC141b",
                    "Emissions|Montreal Gases|HCFC142b",
                    "Emissions|Montreal Gases|HCFC22",
                ]
            ],
        },
        "Emissions|Montreal Gases|CCl4": {
            "title": "CCl4 emissions",
            "comment": "total emissions of CCl4",
            "children": [[]],
        },
        "Emissions|Montreal Gases|CFC": {
            "title": "CFC emissions",
            "comment": "equivalent species total CFC emissions, provided as CFC-11 equivalents",
            "children": [
                [
                    "Emissions|Montreal Gases|CFC|CFC11",
                    "Emissions|Montreal Gases|CFC|CFC113",
                    "Emissions|Montreal Gases|CFC|CFC114",
                    "Emissions|Montreal Gases|CFC|CFC115",
                    "Emissions|Montreal Gases|CFC|CFC12",
                ]
            ],
        },
        "Emissions|Montreal Gases|CFC|CFC11": {
            "title": "CFC11 emissions",
            "comment": "total emissions of CFC11",
            "children": [[]],
        },
        "Emissions|Montreal Gases|CFC|CFC113": {
            "title": "CFC113 emissions",
            "comment": "total emissions of CFC113",
            "children": [[]],
        },
        "Emissions|Montreal Gases|CFC|CFC114": {
            "title": "CFC114 emissions",
            "comment": "total emissions of CFC114",
            "children": [[]],
        },
        "Emissions|Montreal Gases|CFC|CFC115": {
            "title": "CFC115 emissions",
            "comment": "total emissions of CFC115",
            "children": [[]],
        },
        "Emissions|Montreal Gases|CFC|CFC12": {
            "title": "CFC12 emissions",
            "comment": "total emissions of CFC12",
            "children": [[]],
        },
        "Emissions|Montreal Gases|CH2Cl2": {
            "title": "CH2Cl2 emissions",
            "comment": "total emissions of CH2Cl2",
            "children": [[]],
        },
        "Emissions|Montreal Gases|CH3Br": {
            "title": "CH3Br emissions",
            "comment": "total emissions of CH3Br",
            "children": [[]],
        },
        "Emissions|Montreal Gases|CH3CCl3": {
            "title": "CH3CCl3 emissions",
            "comment": "total emissions of CH3CCl3",
            "children": [[]],
        },
        "Emissions|Montreal Gases|CH3Cl": {
            "title": "CH3Cl emissions",
            "comment": "total emissions of CH3Cl",
            "children": [[]],
        },
        "Emissions|Montreal Gases|CHCl3": {
            "title": "CHCl3 emissions",
            "comment": "total emissions of CHCl3",
            "children": [[]],
        },
        "Emissions|Montreal Gases|Halon1202": {
            "title": "Halon-1202 emissions",
            "comment": "total emissions of Halon-1202",
            "children": [[]],
        },
        "Emissions|Montreal Gases|Halon1211": {
            "title": "Halon-1211 emissions",
            "comment": "total emissions of Halon-1211",
            "children": [[]],
        },
        "Emissions|Montreal Gases|Halon1301": {
            "title": "Halon-1301 emissions",
            "comment": "total emissions of Halon-1301",
            "children": [[]],
        },
        "Emissions|Montreal Gases|Halon2402": {
            "title": "Halon-2402 emissions",
            "comment": "total emissions of Halon-2402",
            "children": [[]],
        },
        "Emissions|Montreal Gases|HCFC141b": {
            "title": "HCFC141b emissions",
            "comment": "total emissions of HCFC141b",
            "children": [[]],
        },
        "Emissions|Montreal Gases|HCFC142b": {
            "title": "HCFC22 emissions",
            "comment": "total emissions of HCFC22",
            "children": [[]],
        },
        "Emissions|Montreal Gases|HCFC22": {
            "title": "HCFC22 emissions",
            "comment": "total emissions of HCFC22",
            "children": [[]],
        },
        "Emissions|N2O": {
            "title": "Nitrogen emissions",
            "comment": "total nitrogen emissions",
            "children": [
                [
                    "Emissions|N2O|MAGICC AFOLU",
                    "Emissions|N2O|MAGICC Fossil and Industrial",
                    "Emissions|N2O|Other",
                ]
            ],
        },
        "Emissions|N2O|MAGICC AFOLU": {
            "title": "Nitrogen AFOLU emissions",
            "comment": "nitrogen emissions from agriculture, forestry and other land use (IPCC category 3), excluding any fossil-fuel based emissions in the Agricultural sector (hence not identical to WG3 AFOLU)",
            "children": [[]],
        },
        "Emissions|N2O|MAGICC Fossil and Industrial": {
            "title": "Nitrogen fossil and industrial emissions",
            "comment": "nitrogen emissions from energy use on supply and demand side (IPCC category 1A, 1B), industrial processes (IPCC category 2), waste (IPCC category 4) and other (IPCC category 5)",
            "children": [[]],
        },
        "Emissions|N2O|Other": {
            "title": "Nitrogen emissions from other sources",
            "comment": "nitrogen emissions from other sources (please provide a definition)",
            "children": [[]],
        },
        "Emissions|NH3": {
            "title": "Ammonia emissions",
            "comment": "total ammonia emissions",
            "children": [
                [
                    "Emissions|NH3|MAGICC AFOLU",
                    "Emissions|NH3|MAGICC Fossil and Industrial",
                    "Emissions|NH3|Other",
                ]
            ],
        },
        "Emissions|NH3|MAGICC AFOLU": {
            "title": "Ammonia AFOLU emissions",
            "comment": "ammonia emissions from agriculture, forestry and other land use (IPCC category 3), excluding any fossil-fuel based emissions in the Agricultural sector (hence not identical to WG3 AFOLU)",
            "children": [[]],
        },
        "Emissions|NH3|MAGICC Fossil and Industrial": {
            "title": "Ammonia fossil and industrial emissions",
            "comment": "ammonia emissions from energy use on supply and demand side (IPCC category 1A, 1B), industrial processes (IPCC category 2), waste (IPCC category 4) and other (IPCC category 5)",
            "children": [[]],
        },
        "Emissions|NH3|Other": {
            "title": "Ammonia emissions from other sources",
            "comment": "ammonia emissions from other sources (please provide a definition)",
            "children": [[]],
        },
        "Emissions|NOx": {
            "title": "Nitrous oxide emissions",
            "comment": "total nitrous oxide emissions",
            "children": [
                [
                    "Emissions|NOx|MAGICC AFOLU",
                    "Emissions|NOx|MAGICC Fossil and Industrial",
                    "Emissions|NOx|Other",
                ]
            ],
        },
        "Emissions|NOx|MAGICC AFOLU": {
            "title": "Nitrous oxide AFOLU emissions",
            "comment": "nitrous oxide emissions from agriculture, forestry and other land use (IPCC category 3), excluding any fossil-fuel based emissions in the Agricultural sector (hence not identical to WG3 AFOLU)",
            "children": [[]],
        },
        "Emissions|NOx|MAGICC Fossil and Industrial": {
            "title": "Nitrous oxide fossil and industrial emissions",
            "comment": "nitrous oxide emissions from energy use on supply and demand side (IPCC category 1A, 1B), industrial processes (IPCC category 2), waste (IPCC category 4) and other (IPCC category 5)",
            "children": [[]],
        },
        "Emissions|NOx|Other": {
            "title": "Nitrous oxide emissions from other sources",
            "comment": "nitrous oxide emissions from other sources (please provide a definition)",
            "children": [[]],
        },
        "Emissions|OC": {
            "title": "Organic carbon emissions",
            "comment": "total organic carbon emissions",
            "children": [
                [
                    "Emissions|OC|MAGICC AFOLU",
                    "Emissions|OC|MAGICC Fossil and Industrial",
                    "Emissions|OC|Other",
                ]
            ],
        },
        "Emissions|OC|MAGICC AFOLU": {
            "title": "Organic carbon AFOLU emissions",
            "comment": "organic carbon emissions from agriculture, forestry and other land use (IPCC category 3), excluding any fossil-fuel based emissions in the Agricultural sector (hence not identical to WG3 AFOLU)",
            "children": [[]],
        },
        "Emissions|OC|MAGICC Fossil and Industrial": {
            "title": "Organic carbon fossil and industrial emissions",
            "comment": "organic carbon emissions from energy use on supply and demand side (IPCC category 1A, 1B), industrial processes (IPCC category 2), waste (IPCC category 4) and other (IPCC category 5)",
            "children": [[]],
        },
        "Emissions|OC|Other": {
            "title": "Organic carbon emissions from other sources",
            "comment": "organic carbon emissions from other sources (please provide a definition)",
            "children": [[]],
        },
        "Emissions|Sulfur": {
            "title": "Sulfur emissions",
            "comment": "total sulfur (as a precursor for sulfates) emissions",
            "children": [
                [
                    "Emissions|Sulfur|MAGICC AFOLU",
                    "Emissions|Sulfur|MAGICC Fossil and Industrial",
                    "Emissions|Sulfur|Other",
                ]
            ],
        },
        "Emissions|Sulfur|MAGICC AFOLU": {
            "title": "Sulfur AFOLU emissions",
            "comment": "sulfur (as a precursor for sulfates) emissions from agriculture, forestry and other land use (IPCC category 3), excluding any fossil-fuel based emissions in the Agricultural sector (hence not identical to WG3 AFOLU)",
            "children": [[]],
        },
        "Emissions|Sulfur|MAGICC Fossil and Industrial": {
            "title": "Sulfur fossil and industrial emissions",
            "comment": "sulfur (as a precursor for sulfates) emissions from energy use on supply and demand side (IPCC category 1A, 1B), industrial processes (IPCC category 2), waste (IPCC category 4) and other (IPCC category 5)",
            "children": [[]],
        },
        "Emissions|Sulfur|Other": {
            "title": "Sulfur emissions from other sources",
            "comment": "sulfur (as a precursor for sulfates) emissions from other sources (please provide a definition)",
            "children": [[]],
        },
        "Emissions|VOC": {
            "title": "(Non-methane) volatile organic compounds emissions",
            "comment": "total (non-methane) volatile organic compounds emissions",
            "children": [
                [
                    "Emissions|VOC|MAGICC AFOLU",
                    "Emissions|VOC|MAGICC Fossil and Industrial",
                    "Emissions|VOC|Other",
                ]
            ],
        },
        "Emissions|VOC|MAGICC AFOLU": {
            "title": "(Non-methane) volatile organic compounds AFOLU emissions",
            "comment": "(non-methane) volatile organic compounds emissions from agriculture, forestry and other land use (IPCC category 3), excluding any fossil-fuel based emissions in the Agricultural sector (hence not identical to WG3 AFOLU)",
            "children": [[]],
        },
        "Emissions|VOC|MAGICC Fossil and Industrial": {
            "title": "(Non-methane) volatile organic compounds fossil and industrial emissions",
            "comment": "(non-methane) volatile organic compounds emissions from energy use on supply and demand side (IPCC category 1A, 1B), industrial processes (IPCC category 2), waste (IPCC category 4) and other (IPCC category 5)",
            "children": [[]],
        },
        "Emissions|VOC|Other": {
            "title": "(Non-methane) volatile organic compounds emissions from other sources",
            "comment": "(non-methane) volatile organic compounds emissions from other sources (please provide a definition)",
            "children": [[]],
        },
    },
    "canonical_top_level_category": "Emissions",
}
