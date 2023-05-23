=========
Changelog
=========

0.8.5 (2023-05-23)
------------------

0.8.4 (2023-05-23)
------------------
* Re-release to make sure py.typed is included in built package.


0.8.3 (2023-05-23)
------------------
* add py.typed file to announce this library is using type hints.

0.8.2 (2023-05-15)
------------------
* Remove pygments-csv-lexer dependency for docs building.
* Add function to find leaf children of a category, useful for re-calculating top-level
  categories from constituents.

0.8.1 (2023-04-26)
------------------
* regenerate data included in the package to benefit
  from latest fixes in data generation scripts.

0.8.0 (2023-04-26)
------------------
* Add updated CRF2013 terminologies for 2021, 2022, and 2023 submission rounds
* The unfccc DI API recently returns unspecified measure IDs.
  data_generation/CRFDI_class.py was fixed to ignore them.
* Add CRF2013 terminology for data submitted by AnnexI countries to the UNFCCC
* Drop support for Python 3.7 and 3.8, add support for Python 3.11

0.7.1 (2021-11-25)
------------------
* Change conversion metadata format to use comment chars and a YAML header.

0.7.0 (2021-11-25)
------------------
* Use Python files instead of pickle objects for caching

0.6.3 (2021-11-05)
------------------
* Export Category and HierarchicalCategory types.
* Add ConversionRule.is_restricted attribute to easily check if a rule is restricted to
  specific auxiliary categories.

0.6.2 (2021-11-05)
------------------
* Export Conversion and ConversionRule types.

0.6.1 (2021-11-04)
------------------
* Add emissions categorization from the `Reduced Complexity Model Intercomparison Project (RCMIP) <https://www.rcmip.org/>`_. Thanks to Robert Gieseke for the contribution and Zeb Nicholls for input.

0.6.0 (2021-10-22)
------------------
* Automate changelog generation from snippets - avoids resolving merge conflicts
  manually
* Automate github releases.
* Add category "0" (National total) to IPCC1996 and IPCC2006 categorizations. While it
  is not in the official specification, it is widely used and adding it also enables
  automatically assigning a level to all other categories.
* Add categorization CRF1999 used within in the common reporting framework data.
* Refactor rendering of large categorizations using ``show_as_tree()``, adding more
  clarity to alternative child sets. Add usage documentation for ``show_as_tree()``.
  Thanks to Robert Gieseke for feedback.
* Fixes for IPCC2006 categorization (and IPCC2006_PRIMAP):

  - proper title for category 3.B.3.a "Grassland Remaining Grassland"
  - correct corresponding 1996 category for category 1.A.4.c.ii

* Fixes for IPCC1996 categorization:

  - category 4.B.10 has the correct title "Anaerobic Lagoons"
  - correct usage of units in the titles of categories 4.C.3.a and 4.C.3.b

* Add mechanism to describe conversions between categorizations.
* Add conversion between IPCC2006 and IPCC1996.
* Add algorithm to detect over counting in conversions between categorizations.
* Refactor generation of IPCC2006 and IPCC1996 categorizations.
* Add function to find unmapped categories in a conversion.

0.5.4 (2021-10-18)
------------------

* Add Global Carbon Budget categorization.

0.5.3 (2021-10-12)
------------------

* Add gas categorization which includes commonly used climate forcing substances.

0.5.2 (2021-05-18)
------------------

* Add IPCC2006_PRIMAP categorization.
* Add refrigerant sub-classes and additional codes to CRFDI_class.

0.5.1 (2021-05-04)
------------------

* Add BURDI, CRFDI, BURDI_class, and CRFDI_class categorizations and scripts to generate
  them from the UNFCCC DI flexible query API.

0.5.0 (2021-03-23)
------------------

* Switch ``to_yaml()`` output to ruamel.yaml so that valid, correctly typed YAML 1.2
  is written. This should enable easier re-use of the data in other contexts.
* Consistently use title case for titles in IPCC categorizations.

0.4.0 (2021-03-17)
------------------

* Add more unit tests.
* Add consistency tests for IPCC categorizations.
* Update documentation.
* Add data format documentation.

0.3.2 (2021-03-16)
------------------

* Use tbump for simpler versioning.

0.3.1 (2021-03-16)
------------------

* Properly include data files in binary releases.

0.3.0 (2021-03-16)
------------------

* Add IPCC1996 categorization and scripts to generate it from the source pdf.
* Change packaging to declarative style.
* Automate generation of pickled files via Makefile.
* Automate loading of included categorizations.

0.2.2 (2021-03-09)
------------------

* Re-release again to trigger zenodo.

0.2.1 (2021-03-09)
------------------

* Re-release to include correct changelog.

0.2.0 (2021-03-09)
------------------

* Introduce API for multiple codes and multiple children.
* Implement classes and functions.
* Add IPCC2006 categorization and scripts to generate it from the source pdf.

0.1.0 (2021-01-18)
------------------

* First release on PyPI.
* Contains documentation and a stub API for querying, but no working code yet.
