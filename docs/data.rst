====
Data
====

Categorizations
===============

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


Categorizations with options
----------------------------

A base categorization can have options, which are patches to the base categorization
and are combined on demand. The categorization with options enabled is named like
``ISO3[eu,unfccc]``, with the options sorted alphabetically. The options are stored
next to the base categorization ``{base}.yaml``: each option in a StrictYaml file
``{base}__{option}.yaml``, and a manifest declaring all options in
``{base}__options.yaml``.

Option files have the following fields:

=====================  ====  =================================================  ============================
Key                    Type  Notes                                              Example
---------------------  ----  -------------------------------------------------  ----------------------------
option                 str   the name of the option, letters, digits, and _     unfccc
title                  str   one-line description                               UNFCCC parties
comment                str   optional, long-form description                    Parties to the UN Framework…
references             str   optional, citable reference(s) and sources         https://unfccc.int/…
last_update            str   date of last change in ISO format                  2026-09-24
requires               list  optional, options which have to be enabled, too    ['eu']
conflicts              list  optional, options which can't be enabled, too      ['other']
add_categories         map   optional, new categories, see below
add_alternative_codes  map   optional, new alternative code → primary code      {'EU': 'EU_2020'}
add_children           map   optional, primary code → list of new child sets    {'World': [['ABW', 'AFG']]}
update_info            map   optional, primary code → info to add               {'BOL': {'unfccc_name': …}}
remove_categories      map   optional, categories to remove, see below
=====================  ====  =================================================  ============================

New categories in ``add_categories`` are specified like categories in categorization
files. ``remove_categories`` has the keys ``codes`` with the list of primary codes to
remove, ``keep_total_sum``, and optionally ``comment``. Removed categories are also
removed from all child sets. If ``keep_total_sum`` is ``yes``, the removed categories
are included in other categories, so child sets still add up to their parent. Otherwise,
in categorizations with ``total_sum``, child sets which contained removed categories
are dropped. The ``comment`` is added to the comment of all categories whose children
were changed. When building a categorization with options, first all additions of all
options are applied in the order of the manifest, then all removals.

The manifest has the following fields:

============  ====  ================================================================  ====================
Key           Type  Notes                                                             Example
------------  ----  ----------------------------------------------------------------  --------------------
base          str   the name of the base categorization                               ISO3
options       list  all options, in the order in which they are applied               ['eu', 'unfccc']
combinations  list  optional, patches applied if all their options are enabled
unsupported   list  optional, combinations of options which are not quality-controlled
aliases       map   optional, names for commonly used combinations of options         {'ISO3_PRIMAP': […]}
============  ====  ================================================================  ====================

Each entry in ``combinations`` has the key ``options`` with the list of options, an
optional ``comment`` and the same patch keys as option files (``add_categories`` etc.).
Use combinations to handle the interaction of options.

Each entry in ``unsupported`` has the key ``options`` with a list of options, and an
optional ``comment`` explaining why they are not supported together. All combinations
of options which contain all options of an entry can only be used with
``allow_unsupported=True``, because they were not checked. All other combinations
are supported, as long as they contain all options required by their options
(``requires``) and no conflicting options (``conflicts``). Use ``conflicts`` in option
files for options which can never be used together, and ``unsupported`` in the
manifest for options which could be used together, but were not checked.

An example manifest:

.. code-block:: yaml

    base: ISO3
    options:
      - eu
      - unfccc
      - gcam
      - pse_in_isr
    unsupported:
      - options:
          - gcam
          - pse_in_isr
        comment: the GCAM regions have PSE separately
    aliases:
      ISO3_PRIMAP:
        - eu
        - pse_in_isr
        - unfccc


Conversions
===========

Conversion rules between categorizations included in this package are stored in comma
separated value files with a tightly specified format.
Commas separate fields, and can be escaped using a backslash.
Two consecutive backslashes are read as a single backslash.

The file consists of a YAML meta data block at the start of the file, and a data block
following it.
The YAML meta data block lines start with the comment char '#'.

Meta data block
---------------

The meta data bloc consists of key-value pairs, one on each line, key and value
separated by a colon.
All meta data are optional, the allowed keys are:

============  ====  ==========================================  ========================================
Key           Type  Notes                                       Example
------------  ----  ------------------------------------------  ----------------------------------------
comment       str   Notes and explanations for humans.          Rules for agriculture are still missing.
references    str   Citable reference(s) for the conversion.    doi:10.00000/00
institution   str   Where the conversion originates.            PIK
last_update   date  ISO format of the date of the last change.  1999-12-31
version       str   The version, if there are multiple.         2.3
============  ====  ==========================================  ========================================

Data block
----------

The data block starts with a header which defines the data columns.
The first column must be the name of the first categorization, the following columns
are the names of auxiliary categorizations, the penultimate column must be the name
of the second categorization, and the last column must be ``comment``.

After the header, any number of rules follow, with one rule per line.
Each rule consists of:

* A formula for the first and second categorizations each, defining which categories
  are converted into each other.
* A list of categories for each auxiliary categorization, limiting the validity of the
  rule to specific categorizations.

The formulas contain sums and differences of category codes.
The lists of auxiliary category codes are separated by whitespace.
In formulas and lists, category codes that
consist of alphanumeric characters and dots can be written directly, and other category
codes must be enclosed in ``"`` characters.

Example
-------

.. code-block:: yaml

    # comment: an example conversion
    # institution: PIK
    IPCC1996,gas,IPCC2006,comment
    4 + 5,,3,Both sectors were combined
    4.D,N2O,3.C.4 + 3.C.5,N2O emissions are separated into own categories
