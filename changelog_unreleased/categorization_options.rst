* Added options for categorizations: a base categorization can have named options,
  which add or remove categories and are combined on demand, like
  ``climate_categories.cats["ISO3[eu,unfccc]"]`` or
  ``climate_categories.ISO3.with_options(["eu", "unfccc"])``. Options can require or
  conflict with other options, and combinations of options which are declared as not
  quality-controlled can only be used with ``allow_unsupported=True``. Aliases name commonly used
  combinations of options. See ``available_options``, ``supported_combinations``,
  ``enabled_options``, and ``canonical_name`` of categorizations. Options can add,
  update, and remove categories, alternative codes, and child sets. They can also merge
  categories into other categories with ``merge_into``, which records the merged
  categories in the ``includes`` info of the receiving category, or split them from
  other categories with ``split_from``, which records the split categories
  in the ``excludes`` info of the category they are split from. Receiving categories
  which are not a member of any child set yet, like historical countries, take over
  the memberships of the categories merged into them, and ``join_parents`` lists the
  parents, like ``World``, which split categories join.
* **Breaking change**: ``ISO3`` now only contains the countries from ISO 3166-1 and the
  world. The groupings are available as the options ``eu``, ``unfccc`` (including the
  Paris Agreement), and ``groups``. New options are ``historical`` (countries withdrawn
  from ISO 3166-1, like ``SUN`` and ``YUG``), ``kosovo`` (split from Serbia, so ``SRB``
  has ``info["excludes"] == ["XKX"]``, and part of ``World``), and ``pse_in_isr`` (Palestine
  not listed separately, but included in Israel, so ``ISR`` has
  ``info["includes"] == ["PSE"]``). Use the new alias ``ISO3_PRIMAP``
  for the previous contents of ``ISO3``, which additionally includes the withdrawn
  countries and has Palestine included in Israel, like PRIMAP-hist.
* ``ISO3_GCAM`` is now an alias for ISO3 with the new ``gcam`` option and the options
  ``eu``, ``groups``, ``historical``, ``kosovo``, and ``unfccc``, so it also includes the
  withdrawn countries now.
* Categories which compare equal because their categorizations are related, like
  ``ISO3["DEU"]`` and ``ISO3_PRIMAP["DEU"]``, or ``IPCC2006["1.A"]`` and
  ``IPCC2006_PRIMAP["1.A"]``, now also have the same hash.
