==================
Climate categories
==================


.. image:: https://img.shields.io/pypi/v/climate_categories.svg
        :target: https://pypi.python.org/pypi/climate_categories

.. image:: https://readthedocs.org/projects/climate-categories/badge/?version=latest
        :target: https://climate-categories.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4590232.svg
        :target: https://doi.org/10.5281/zenodo.4590232

Commonly used codes, categories, terminologies, and nomenclatures used in climate
policy analysis in a nice Python package.
The documentation can be found at: https://climate-categories.readthedocs.io.

Included categorizations
------------------------

===============  ==================================================================
Name             Title
---------------  ------------------------------------------------------------------
IPCC1996         IPCC GHG emission categories (1996)
IPCC2006         IPCC GHG emission categories (2006)
IPCC2006_PRIMAP  IPCC GHG emission categories (2006) with additional categories
CRF1999          Common Reporting Format GHG emissions categories (1999)
CRF2013          Common Reporting Format GHG emissions categories (2013)
CRF2013_2021     CRF categories extended with country specific categories from
                 2021 submissions
CRF2013_2022     CRF categories extended with country specific categories from
                 2022 submissions
CRF2013_2023     CRF categories extended with country specific categories from
                 2023 submissions
BURDI            BUR GHG emission categories (DI query interface)
BURDI_class      BUR GHG emission categories (DI query interface) + classifications
CRFDI            CRF GHG emission categories (DI query interface)
CRFDI_class      CRF GHG emission categories (DI query interface) + classifications
GCB              Global Carbon Budget CO2 emission categories
RCMIP            RCMIP emissions categories
gas              Gases and other climate-forcing substances
ISO3             Countries and other areas from ISO 3166-1, with options for country
                 groups, see below
ISO3_PRIMAP      ISO3 with EU, UNFCCC and Paris Agreement parties, country groups,
                 and historical countries; Palestine included in Israel
ISO3_GCAM        ISO3 with EU, UNFCCC and Paris Agreement parties, country groups,
                 historical countries, Kosovo, and regions used by the GCAM
                 integrated assessment model
FAO              FAOSTAT climate change agrifood systems GHG emissions categories
CT               Climate Trace categories
===============  ==================================================================

Categorizations with options
-----------------------------

Some categorizations have options, which add or remove categories. For example,
``climate_categories.cats["ISO3[eu,unfccc]"]`` or equivalently
``climate_categories.ISO3.with_options(["eu", "unfccc"])`` gives the ISO 3166-1 countries
together with the European Union and the parties to the UNFCCC.
``climate_categories.ISO3.available_options`` lists the options and
``climate_categories.ISO3.supported_combinations`` lists the quality-controlled
combinations of options. Aliases like ``ISO3_PRIMAP`` name commonly used combinations
of options; note that the options of an alias can be extended in later versions.

You can also apply your own options to any categorization using
``Categorization.apply``, or share them as a file with a ``base`` field naming the
categorization they extend, which ``climate_categories.load_extension`` reads and
applies. Several extensions of the same categorization can be loaded together, and later
extensions can require earlier ones.

Included conversions between categorizations
--------------------------------------------

* IPCC1996 <-> IPCC2006
* FAO <-> IPCC2006_PRIMAP
* CT <-> IPCC2006_PRIMAP

Status
------
Climate categories is still in development and the API and names of categorizations
are still subject to change.

License
-------
Copyright 2021, Potsdam-Institut für Klimafolgenforschung e.V.

Copyright 2021, Robert Gieseke

Copyright 2023-2025, Climate Resource Pty Ltd

Copyright 2026, Climate Resource S GmbH

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
file except in compliance with the License. You may obtain a copy of the License at

https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the specific language governing
permissions and limitations under the License.

Citation
--------
If you use this library and want to cite it, please cite it as:

Mika Pflüger, Daniel Busch, Annika Günther, Johannes Gütschow, and Robert Gieseke. (2026-09-24).
primap-community/climate_categories: climate_categories Version 0.15.0.
Zenodo. https://doi.org/10.5281/zenodo.22943797
