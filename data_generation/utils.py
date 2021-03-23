import pathlib
import shutil

import requests


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
