====
Data
====

The categorizations included in this package are stored as YAML 1.2 files.
The data files must only use the subset of YAML's features understood by
`StrictYaml <https://github.com/crdoconnor/strictyaml>`_.
The allowed contents are defined here.

Simple Categorizations
----------------------

Non-hierarchical categorizations are stored in StrictYaml files with the following
fields:

============  ====  =========================================  ===================================
Key           Type  Notes                                      Example
------------  ----  -----------------------------------------  -----------------------------------
name          str   a valid python variable name               IPCC2006
title         str   one-line description                       IPCC GHG emission categories (2006)
comment       str   long-form description                      IPCC classification of green-house…
references    str   citable reference(s) and sources           IPCC 2006, 2006 IPCC Guidelines…
institution   str   where the categorization is from           IPCC
last_update   str   date of last change in ISO format          2010-06-30
hierarchical  bool  has to be ``no``, ``false``, or ``False``  no
version       str   optional                                   2006
categories    map   see below
============  ====  =========================================  ===================================

The metadata attributes are inspired by the
`CF conventions <https://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#description-of-file-contents>`_
for the description of file contents.

The categories are given as a map from the primary code of the category to a
dictionary specification with the following fields:

=================  ====  =========================================  ===================================
Key                Type  Notes                                      Example
-----------------  ----  -----------------------------------------  -----------------------------------
title              str   one-line description of the category       Energy
comment            str   optional, long-form description            Includes all GHG…
alternative_codes  list  optional, alias codes                      ['1A', '1 A']
info               map   optional, arbitrary metadata               {'gases': ['CO2', 'NH3']}
=================  ====  =========================================  ===================================

The examples in the table are given in python syntax. An example in YAML syntax
would be:

.. code-block:: yaml

    categories:
      '1':
        title: ENERGY
        comment: This category includes all GHG emissions arising from combustion and
          fugitive releases of fuels. Emissions from the non-energy uses of fuels are
          generally not included here, but reported under Industrial Processes and Product
          Use Sector.
        info:
          gases:
          - CO2
          - CH4
      1.A:
        title: Fuel Combustion Activities
        comment: Emissions from the intentional oxidation of materials within an apparatus
          that is designed to raise heat and provide it either as heat or as mechanical
          work to a process or for use away from the apparatus.
        alternative_codes:
        - 1A
        info:
          gases:
          - CO
          - NMVOC
          corresponding_categories_IPCC1996:
          - 1A


Hierarchical Categorizations
----------------------------

Hierarchical categorizations are also stored in StrictYaml files, with additional
meta data fields:

============================  ====  =========================================  =======
Key                           Type  Notes                                      Example
----------------------------  ----  -----------------------------------------  -------
hierarchical                  str   has to be ``yes``, ``true``, or ``True``   yes
total_sum                     bool  if parents are the sum of their children   True
canonical_top_level_category  str   optional, code of the highest category     TOTAL
============================  ====  =========================================  =======


In the category specifications, an additional optional key ``children`` is introduced
which contains lists of lists of codes of children. Since some categories can be
composed of different sets of children, it is necessary to give a list of lists.

An example in StrictYaml syntax with two categories would be:

.. code-block:: yaml

    categories:
      '1':
        title: ENERGY
        comment: This category includes all GHG emissions arising from combustion and
          fugitive releases of fuels. Emissions from the non-energy uses of fuels are
          generally not included here, but reported under Industrial Processes and Product
          Use Sector.
        info:
          gases:
          - CO2
          - CH4
        children:
          - - 1.A
            - 1.B
      1.A:
        title: Fuel Combustion Activities
        comment: Emissions from the intentional oxidation of materials within an apparatus
          that is designed to raise heat and provide it either as heat or as mechanical
          work to a process or for use away from the apparatus.
        alternative_codes:
        - 1A
        info:
          gases:
          - CO
          - NMVOC
          corresponding_categories_IPCC1996:
          - 1A
