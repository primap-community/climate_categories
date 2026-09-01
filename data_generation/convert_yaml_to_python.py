"""Convert categorizations stored in StrictYaml files to Python files for faster
loading.

Each categorization is written next to its YAML file, with the extension changed to
``.py``. Parsing StrictYaml is slow -- which is why the Python files exist in the
first place -- so the files are converted in parallel.
"""

import argparse
import concurrent.futures
import pathlib
import sys

import climate_categories


def convert(yaml_path: pathlib.Path) -> pathlib.Path:
    """Convert one YAML file to the Python file next to it."""
    python_path = yaml_path.with_suffix(".py")
    climate_categories.from_yaml(yaml_path).to_python(python_path)
    return python_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "yaml_files",
        metavar="FILE.yaml",
        nargs="+",
        type=pathlib.Path,
        help="categorization to convert, written to FILE.py",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=None,
        help="number of files to convert in parallel (default: one per CPU)",
    )
    args = parser.parse_args()

    errors = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.jobs) as executor:
        futures = {executor.submit(convert, f): f for f in args.yaml_files}
        for future in concurrent.futures.as_completed(futures):
            yaml_path = futures[future]
            try:
                print(future.result(), flush=True)
            except Exception as err:  # noqa: BLE001
                errors.append((yaml_path, err))

    for yaml_path, err in errors:
        print(f"error: converting {yaml_path} failed: {err}", file=sys.stderr)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
