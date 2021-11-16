"""Convert a categorization stored in a StrictYaml file to a Python
file for faster loading."""

import sys

import climate_categories


def main():
    cat = climate_categories.from_yaml(sys.argv[1])
    cat.to_python(sys.argv[2])


if __name__ == "__main__":
    main()
