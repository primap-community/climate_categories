"""Run this via `make climate_categories/data/ISO3_GCAM.yaml` in the main
directory."""

import datetime
import pathlib

import pandas as pd
import pycountry
import tqdm

import climate_categories

OUTPATH = pathlib.Path("./climate_categories/data/ISO3_GCAM.yaml")

# ISO3 categorization amended with GCAM regions


def main():
    categories = {}
    children = []

    for gcam_version in tqdm.tqdm(("5.1", "5.2", "5.3", "5.4", "6.0", "7.0")):
        if gcam_version == "7.0":
            url = "https://jgcri.github.io/gcam-doc/overview.html"
        else:
            url = f"https://jgcri.github.io/gcam-doc/v{gcam_version}/overview.html"
        gcam_regions_df = pd.read_html(url, match="GCAM Region", header=0, index_col=0)[
            0
        ]

        for region in gcam_regions_df.index:
            countries = gcam_regions_df.loc[region].iloc[0].split(", ")
            countries_iso3 = []
            for country in countries:
                direct_match = pycountry.countries.get(name=country)
                if direct_match is not None:
                    countries_iso3.append(direct_match.alpha_3)
                elif country in (
                    "Netherlands Antilles",
                    "Pacific Islands Trust Territory",
                ):
                    continue  # TODO: deal with historical countries
                else:
                    print(f"Warning: {country} not found directly")
                    if country == "Swaziland":
                        country = "Eswatini"
                    elif country == "Cote d’Ivoire":  # noqa: RUF001
                        country = "Cote d'Ivoire"
                    elif country == "Democratic Republic of the Congo":
                        country = "Congo, The Democratic Republic of the"
                    elif country == "Cape Verde":
                        country = "Cabo Verde"
                    elif country == "Antigua & Barbuda":
                        country = "Antigua and Barbuda"
                    elif country == "Turkey":
                        country = "turkiye"
                    elif country == "Lao Peoples Democratic Republic":
                        country = "laos"
                    elif country == "Pitcairn Islands":
                        country = "pitcairn"
                    elif country == "Democratic Peoples Republic of Korea":
                        country = "north korea"
                    elif country == "Timor Leste":
                        country = "Timor-Leste"
                    fuzzy_match = pycountry.countries.search_fuzzy(country)[0]
                    print(f"Using {fuzzy_match.name} for {country}")
                    countries_iso3.append(fuzzy_match.alpha_3)

            region_code = f"GCAM {gcam_version}|{region}"
            categories[region_code] = {
                "title": region,
                "comment": f"Region {region!r} as defined in GCAM version {gcam_version}",
            }
            children.append((region_code, countries_iso3))

    iso3_gcam = climate_categories.ISO3.extend(
        name="GCAM",
        title=" with GCAM regions",
        comment=" Additionally, includes regions used in the GCAM integrated assessment model",
        last_update=datetime.date.fromisoformat("2024-01-25"),
        categories=categories,
        children=children,
    )

    iso3_gcam.references = (
        climate_categories.ISO3.references
        + "; https://jgcri.github.io/gcam-doc/index.html"
    )
    iso3_gcam.institution = "Joint Global Change Research Institute "

    iso3_gcam.to_yaml(OUTPATH)

    climate_categories.HierarchicalCategorization.from_yaml(OUTPATH)


if __name__ == "__main__":
    main()
