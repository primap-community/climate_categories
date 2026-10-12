* Added the history of the Least Developed Countries (``LDC_YYYY``, from 1991) to the
  ``groups`` option, and of the parties listed in Annex I of the UNFCCC and the other
  parties (``Annex-I_YYYY_MM``, ``Non-Annex-I_YYYY_MM``) to the ``UNFCCC`` option.
  **Breaking change**: ``LDC`` and ``AOSIS`` are now alternative codes of the dated
  categories ``LDC_2024`` and ``AOSIS_2011``, so that they always refer to the current
  members, like ``EU`` and ``UMBRELLA``.
* Added the option ``PRIMAP1`` and the aliases ``ISO3_PRIMAP1`` for PRIMAP-hist up to
  v2.x and ``ISO3_PRIMAP2`` for PRIMAP-hist from v3.0 on. In ``ISO3_PRIMAP1``,
  ``World`` contains exactly the countries and territories of PRIMAP-hist v2.x, and the
  region codes of PRIMAP-hist v2.x refer to its definitions, like ``LDC`` to
  ``LDC_2012`` and ``UMBRELLA`` to ``UMBRELLA_PRIMAP1``.
