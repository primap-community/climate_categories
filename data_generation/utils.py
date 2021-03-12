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
