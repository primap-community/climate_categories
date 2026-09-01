"""Update the citation information in the README from the zenodo API.

With ``--wait-for-version X.Y.Z``, wait until zenodo has minted the record for that
version before writing. Zenodo needs a few minutes after a GitHub release, so the
release workflow cannot simply read the record right away.
"""

import argparse
import sys
import time

import requests

RECORD_URL = "https://zenodo.org/api/records/4590232"
POLL_INTERVAL = 60  # seconds
POLL_TIMEOUT = 15 * 60  # seconds


def fetch_record():
    resp = requests.get(RECORD_URL)
    resp.raise_for_status()
    return resp.json()


def fetch_record_for_version(version: str):
    """Poll zenodo until the newest record is the one for `version`."""
    deadline = time.monotonic() + POLL_TIMEOUT
    while True:
        record = fetch_record()
        title = record["metadata"]["title"]
        if title.endswith(f"Version {version}"):
            return record
        if time.monotonic() >= deadline:
            raise SystemExit(
                f"zenodo still reports {title!r} after"
                f" {POLL_TIMEOUT // 60} minutes, giving up. Re-run the"
                f' "Update citation info" workflow once the record for'
                f" {version} shows up at https://doi.org/10.5281/zenodo.4590232 ."
            )
        print(f"zenodo reports {title!r}, waiting for version {version} ...")
        sys.stdout.flush()
        time.sleep(POLL_INTERVAL)


def update_readme(record) -> None:
    new_link = record["links"]["doi"]
    new_date = record["metadata"]["publication_date"]
    new_title = record["metadata"]["title"]

    citation = f"""Citation
--------
If you use this library and want to cite it, please cite it as:

Mika Pflüger, Daniel Busch, Annika Günther, Johannes Gütschow, and Robert Gieseke. ({new_date}).
{new_title}.
Zenodo. {new_link}
"""

    with open("README.rst") as fd:
        old_content = fd.read().splitlines(keepends=True)

    with open("README.rst", "w") as fd:
        skip_to_next_section = False
        i = 0
        while True:
            try:
                line = old_content[i]
            except IndexError:
                break
            if line == "Citation\n":
                fd.write(citation)
                skip_to_next_section = True
                i += 2
            elif skip_to_next_section:
                if line.startswith("---"):
                    fd.write("\n")
                    fd.write(old_content[i - 1])
                    fd.write(line)
                    skip_to_next_section = False
                i += 1
            else:
                fd.write(line)
                i += 1

        fd.truncate()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wait-for-version",
        metavar="X.Y.Z",
        help="wait until zenodo has minted the record for this version",
    )
    args = parser.parse_args()

    if args.wait_for_version:
        record = fetch_record_for_version(args.wait_for_version)
    else:
        record = fetch_record()

    update_readme(record)


if __name__ == "__main__":
    main()
