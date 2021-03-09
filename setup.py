#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.rst") as history_file:
    history = history_file.read()

requirements = ["networkx", "pandas", "strictyaml"]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Mika Pflüger",
    author_email="mika.pflueger@pik-potsdam.de",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Commonly used codes, categories, terminologies, and nomenclatures"
    " used in climate policy analysis as a Python package.",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="climate_categories",
    name="climate_categories",
    packages=find_packages(include=["climate_categories", "climate_categories.*"]),
    setup_requires=setup_requirements,
    test_suite="climate_categories/tests",
    tests_require=test_requirements,
    url="https://github.com/pik-primap/climate_categories",
    version="0.2.2",
    zip_safe=False,
)
