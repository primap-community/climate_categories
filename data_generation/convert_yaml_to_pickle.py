"""Convert a categorization stored in a StrictYaml file to a python pickle for faster
loading."""

import sys

import climate_categories


def main():
    cat = climate_categories.from_yaml(sys.argv[1])
    cat.to_pickle(sys.argv[2])


if __name__ == "__main__":
    main()
