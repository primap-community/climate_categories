import pathlib
import re
import shutil

import requests

import climate_categories


def write_categorization(
    categorization: "climate_categories.Categorization", yaml_path: pathlib.Path
) -> None:
    """Write a categorization as YAML and as the cached Python spec next to it.

    The Python spec is generated from the YAML we just wrote, so it goes through
    exactly the same code path as ``make recache`` and the two cannot disagree.
    Reading the YAML back in also validates it.
    """
    categorization.to_yaml(yaml_path)
    climate_categories.from_yaml(yaml_path).to_python(yaml_path.with_suffix(".py"))


def write_option_family(
    base: "climate_categories.Categorization",
    options: list["climate_categories.CategorizationOption"],
    manifest: "climate_categories.OptionManifest",
    directory: pathlib.Path,
) -> None:
    """Write a base categorization with its options and manifest as YAML and as the
    cached Python specs next to them.

    Like ``write_categorization``, the Python specs are generated from the YAML files
    we just wrote. Option files of the base which are not part of the manifest any
    more are deleted. Afterwards, the family is read back in, which validates it.
    """
    write_categorization(base, directory / f"{base.name}.yaml")

    stems = {climate_categories.manifest_stem(base.name)}
    for option in options:
        stem = climate_categories.option_stem(base.name, option.name)
        stems.add(stem)
        option.to_yaml(directory / f"{stem}.yaml")
        climate_categories.CategorizationOption.from_yaml(
            directory / f"{stem}.yaml"
        ).to_python(directory / f"{stem}.py")

    manifest_path = directory / f"{climate_categories.manifest_stem(base.name)}.yaml"
    manifest.to_yaml(manifest_path)
    climate_categories.OptionManifest.from_yaml(manifest_path).to_python(
        manifest_path.with_suffix(".py")
    )

    for path in directory.glob(f"{base.name}__*"):
        if path.suffix in (".yaml", ".py") and path.stem not in stems:
            print(f"Deleting {path}, which is not an option of {base.name} any more.")
            path.unlink()

    climate_categories.OptionFamily.from_yaml(manifest_path)


def all_codes(categories: dict[str, dict]) -> set[str]:
    """All primary and alternative codes in a specification of categories."""
    codes = set(categories)
    for spec in categories.values():
        codes.update(spec.get("alternative_codes", []))
    return codes


def download_cached(url: str, fpath: pathlib.Path):
    if not fpath.exists():
        print(f"{fpath} not found, downloading it.")
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with fpath.open("wb") as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            raise FileNotFoundError(f"Could not download {url!r}")


def title_case(instr: str) -> str:
    return (
        instr.title()
        .replace(" And ", " and ")
        .replace(" Of ", " of ")
        .replace(" On ", " on ")
        .replace(" Or ", " or ")
        .replace(" To ", " to ")
        .replace(" As ", " as ")
        .replace(" For ", " for ")
        .replace(" From ", " from ")
        .replace(" With ", " with ")
        .replace(" Without ", " without ")
        .replace("Nox", "NOx")
        .replace("Nh3", "NH3")
        .replace("Co2", "CO2")
        .replace("Sf6", "SF6")
        .replace("Pfc", "PFC")
        .replace("Tft", "TFT")
    )


#: Chemical formulae as they are written in category titles, mapped to their LaTeX
#: representation.
LATEX_FORMULAE = {
    "CH4": "CH$_4$",
    "CO2": "CO$_2$",
    "N2O": "N$_2$O",
    "NF3": "NF$_3$",
    "NH3": "NH$_3$",
    "NOx": r"NO$_\text{x}$",
    "SF6": "SF$_6$",
    "SO2": "SO$_2$",
}

_LATEX_FORMULAE_RE = re.compile(
    r"\b(" + "|".join(sorted(LATEX_FORMULAE, key=len, reverse=True)) + r")\b"
)


def latex_title(title: str) -> str | None:
    """Typeset the chemical formulae in a category title for LaTeX.

    Returns None if the title contains no chemical formula, i.e. if it needs no
    separate LaTeX title.
    """
    latex = _LATEX_FORMULAE_RE.sub(lambda m: LATEX_FORMULAE[m.group()], title)
    if latex == title:
        return None
    return latex
