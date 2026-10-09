* Added ``Categorization.apply`` to apply your own option to any categorization, given
  as a ``CategorizationOption`` or as an option file. The result is named
  ``{name}_{option}`` and its categories are comparable to the categories of the
  original categorization. Option files can name the categorization they are for in
  the new ``base`` field, and ``climate_categories.load_extension`` reads such a file
  and applies it to its base, so that extensions of categorizations can be shared
  as a file, for example together with a dataset (#12).
