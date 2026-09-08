"""Run this via `make climate_categories/data/ISO3_GCAM.yaml` in the main
directory."""

import collections
import csv
import datetime
import pathlib

import requests
import tqdm
from utils import write_categorization

import climate_categories

OUTPATH = pathlib.Path("./climate_categories/data/ISO3_GCAM.yaml")

# ISO3 categorization amended with GCAM regions.
#
# The region definitions are read from the model's input data in the gcam-core
# repository.

RAW_URL = "https://raw.githubusercontent.com/JGCRI/gcam-core"
WEB_URL = "https://github.com/JGCRI/gcam-core/blob"

#: All released GCAM versions which ship region definitions, oldest first. GCAM 3.x
#: and earlier predate the mapping files, but their regions are still available, see
#: ``GCAM3_VERSION``.
GCAM_VERSIONS = (
    "4.0",
    "4.1",
    "4.2",
    "4.3",
    "4.4",
    "4.4.1",
    "5.1",
    "5.1.1",
    "5.1.2",
    "5.1.3",
    "5.2",
    "5.3",
    "5.4",
    "6.0",
    "7.0",
    "7.1",
    "7.2",
    "7.3",
    "7.4",
    "8.0",
    "8.1",
    "8.2",
    "8.3",
    "8.4",
    "8.5",
    "8.6",
    "8.7",
    "8.8",
    "8.9",
    "8.10",
    "8.11",
    "9.0",
    "9.1",
)

#: The mapping files moved twice, so we have to try all directories they lived in.
MAPPING_DIRS = (
    "input/gcamdata/inst/extdata/common",  # GCAM 5.1 and later
    "input/gcam-data-system/_common/mappings",  # GCAM 4.3 to 4.4.1
    "Main_User_Workspace/input/gcam-data-system/_common/mappings",  # GCAM 4.0 to 4.2
)

#: Maps GCAM region IDs to region names.
NAMES_FILE = "GCAM_region_names.csv"

#: Maps countries to GCAM region IDs, and additionally contains the region of each
#: country in GCAM 3 in its ``region_GCAM3`` column.
REGIONS_FILE = "iso_GCAM_regID.csv"

#: The GCAM version we take the GCAM 3 regions from. GCAM only ever added countries to
#: the ``region_GCAM3`` column (checked in :func:`check_gcam3_additive`), so the newest
#: release contains the most complete definition of the GCAM 3 regions.
GCAM3_VERSION = GCAM_VERSIONS[-1]

#: Entries in the ``iso`` column which are not ISO 3166-1 alpha-3 codes, mapped to the
#: code to use instead, or to None if there is no country to map them to.
ISO_FIXES = {
    "rom": "ROU",  # Romania, GCAM 7.0 and later list both rom and rou
    "ant": None,  # Netherlands Antilles, dissolved in 2010
    "chi": None,  # Channel Islands, a World Bank aggregate of Guernsey and Jersey
    "pci": None,  # Pacific Islands Trust Territory, dissolved in 1994
    "scg": None,  # Serbia and Montenegro, dissolved in 2006
    "yug": None,  # Yugoslavia, dissolved in 2003
}

#: Categories we have to add before we can use them in a region. GCAM 7.4 and later
#: use Kosovo, which is not part of ISO 3166-1, and we want to follow GCAM closely, so
#: we add it here. Like the GCAM regions themselves, it is not part of any of the
#: groupings inherited from ISO3.
ADDITIONAL_COUNTRIES = {
    "XKX": {
        "title": "Kosovo",
        "comment": "Kosovo, as used by GCAM 7.4 and later. Not part of ISO 3166-1, "
        "XKX is the user-assigned code commonly used for it",
        "alternative_codes": ["XK"],
    },
}

#: Additional names for regions, used as alternative codes. The GCAM documentation
#: spells some region names differently from the mapping files, and we want both
#: spellings to work.
REGION_ALIASES = {
    "Australia_NZ": ("Australia and New Zealand",),
    "Central America and Caribbean": ("Central America and the Caribbean",),
}

#: Additional names for GCAM versions, used as alternative codes. The CMIP7 runs
#: labelled "GCAM 8s" use the regions of GCAM 8.0, which are the same as in GCAM 7.4,
#: but differ from GCAM 8.1 and later.
VERSION_ALIASES = {
    "8.0": ("8s",),
}


def parse_csv(content: bytes) -> list[dict[str, str]]:
    """Parse one of the GCAM mapping files.

    The files start with a block of ``#``-prefixed metadata lines before the actual
    header line, and the GCAM 4.x files use classic Mac line endings.
    """
    text = content.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    return list(
        csv.DictReader(
            line for line in text.split("\n") if line.strip() and line[0] != "#"
        )
    )


_mapping_dirs: dict[str, str] = {}


def mapping_dir(version: str) -> str:
    """Find the directory the mapping files live in for the given GCAM version."""
    if version not in _mapping_dirs:
        for directory in MAPPING_DIRS:
            response = requests.head(
                f"{RAW_URL}/gcam-v{version}/{directory}/{NAMES_FILE}"
            )
            if response.ok:
                _mapping_dirs[version] = directory
                break
        else:
            raise FileNotFoundError(
                f"Could not find {NAMES_FILE} for GCAM version {version} in any known "
                "location, the gcam-core layout probably changed again."
            )

    return _mapping_dirs[version]


def download_mapping(version: str, filename: str) -> list[dict[str, str]]:
    """Download and parse one of the GCAM mapping files."""
    response = requests.get(
        f"{RAW_URL}/gcam-v{version}/{mapping_dir(version)}/{filename}"
    )
    response.raise_for_status()

    return parse_csv(response.content)


def read_regions(
    version: str, ignored: collections.Counter[str]
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Read the region definitions of one GCAM version.

    Returns the regions of this version and the GCAM 3 regions as recorded by this
    version, both as mappings from the region name to the ISO3 codes of its countries.
    Codes we drop are counted in ``ignored``.
    """
    names = {
        row["GCAM_region_ID"]: row["region"]
        for row in download_mapping(version, NAMES_FILE)
    }
    # start out with all regions in the order GCAM numbers them, so that the generated
    # categorization lists them in the same order as GCAM does
    regions: dict[str, set[str]] = {
        names[region_id]: set() for region_id in sorted(names, key=int)
    }
    regions_gcam3: dict[str, set[str]] = {}

    for row in download_mapping(version, REGIONS_FILE):
        iso = row["iso"]
        if iso in ISO_FIXES:
            if ISO_FIXES[iso] is None:
                ignored[iso] += 1
                continue
            code = ISO_FIXES[iso]
        else:
            code = iso.upper()

        if code not in climate_categories.ISO3 and code not in ADDITIONAL_COUNTRIES:
            raise ValueError(
                f"GCAM version {version} uses the country code {iso!r} which is "
                "neither in ISO3 nor in ADDITIONAL_COUNTRIES, please add it to "
                "ADDITIONAL_COUNTRIES or to ISO_FIXES."
            )

        regions[names[row["GCAM_region_ID"]]].add(code)
        regions_gcam3.setdefault(row["region_GCAM3"], set()).add(code)

    empty = [region for region, codes in regions.items() if not codes]
    if empty:
        raise ValueError(f"GCAM version {version} has empty regions: {empty}")

    return regions, dict(sorted(regions_gcam3.items()))


def check_gcam3_additive(regions_gcam3: dict[str, dict[str, set[str]]]) -> None:
    """Check that we can use the newest GCAM 3 regions for all GCAM versions.

    GCAM only ever added countries to the ``region_GCAM3`` column, never moved or
    removed any, so the newest release has the most complete definition. Should that
    ever change we have to model the GCAM 3 regions per version instead, and this
    check tells us so.
    """
    newest = regions_gcam3[GCAM3_VERSION]
    for version, regions in regions_gcam3.items():
        for region, codes in regions.items():
            if region not in newest or not codes <= newest[region]:
                raise ValueError(
                    f"The GCAM 3 region {region!r} as recorded by GCAM version "
                    f"{version} is not a subset of the region as recorded by GCAM "
                    f"version {GCAM3_VERSION}, so the GCAM 3 regions have to be "
                    "generated per GCAM version."
                )


def deduplicate(
    regions: dict[str, dict[str, set[str]]],
) -> list[tuple[str, list[str], dict[str, set[str]]]]:
    """Group GCAM versions which share the same region definition.

    Returns a list of (version, other versions with the same regions, regions), in the
    order the versions were released.
    """
    groups: list[tuple[str, list[str], dict[str, set[str]]]] = []
    for version, version_regions in regions.items():
        for _, same, group_regions in groups:
            if group_regions == version_regions:
                same.append(version)
                break
        else:
            groups.append((version, [], version_regions))

    return groups


def describe(versions: list[str]) -> str:
    if len(versions) == 1:
        return f"GCAM version {versions[0]}"
    return f"GCAM versions {', '.join(versions)}"


def alternative_codes(versions: list[str], region: str) -> list[str]:
    """All codes for a region besides the canonical one.

    That is the region in all GCAM versions which share this definition of it, under
    all names of those versions and all spellings of its name.
    """
    return [
        f"GCAM {label}|{name}"
        for version in versions
        for label in (version, *VERSION_ALIASES.get(version, ()))
        for name in (region, *REGION_ALIASES.get(region, ()))
        if (label, name) != (versions[0], region)
    ]


def main():
    regions = {}
    regions_gcam3 = {}
    ignored: collections.Counter[str] = collections.Counter()
    for version in tqdm.tqdm(GCAM_VERSIONS):
        regions[version], regions_gcam3[version] = read_regions(version, ignored)

    for iso, count in sorted(ignored.items()):
        print(
            f"Ignored {iso!r} without ISO 3166-1 equivalent in {count} GCAM versions."
        )

    check_gcam3_additive(regions_gcam3)

    categories = dict(ADDITIONAL_COUNTRIES)
    children = []
    references = []

    for version, same_versions, version_regions in deduplicate(regions):
        versions = [version, *same_versions]
        for region, codes in version_regions.items():
            categories[f"GCAM {version}|{region}"] = {
                "title": region,
                "comment": f"Region {region!r} as defined in {describe(versions)}",
                "alternative_codes": alternative_codes(versions, region),
            }
            children.append((f"GCAM {version}|{region}", sorted(codes)))
        references.append(
            f"{describe(versions)} regions, "
            f"{WEB_URL}/gcam-v{version}/{mapping_dir(version)}/{REGIONS_FILE}"
        )

    for region, codes in regions_gcam3[GCAM3_VERSION].items():
        categories[f"GCAM 3.0|{region}"] = {
            "title": region,
            "comment": f"Region {region!r} as defined in GCAM version 3.0, as "
            f"recorded by GCAM version {GCAM3_VERSION}",
            "alternative_codes": alternative_codes(["3.0"], region),
        }
        children.append((f"GCAM 3.0|{region}", sorted(codes)))
    references.append(
        "GCAM version 3.0 regions, region_GCAM3 column of "
        f"{WEB_URL}/gcam-v{GCAM3_VERSION}/{mapping_dir(GCAM3_VERSION)}/{REGIONS_FILE}"
    )

    iso3_gcam = climate_categories.ISO3.extend(
        name="GCAM",
        title=" with GCAM regions",
        comment=" Additionally, includes regions used in the GCAM integrated assessment model",
        last_update=datetime.date.fromisoformat("2026-09-08"),
        categories=categories,
        children=children,
    )

    iso3_gcam.references = climate_categories.ISO3.references + ";\n".join(
        [*references, ""]
    )
    iso3_gcam.institution = "Joint Global Change Research Institute "

    write_categorization(iso3_gcam, OUTPATH)


if __name__ == "__main__":
    main()
