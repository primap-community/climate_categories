* The withdrawn countries of the ``historical`` option which were split up or renamed
  now have their successors as children, like the USSR (``SUN``) its 15 republics, and
  dependent territories in ``ISO3`` have their sovereign country in the ``sovereign``
  info, like ``ISO3["GRL"].info["sovereign"] == "DNK"``. With the ``Kosovo`` option,
  Kosovo (``XKX``) is a child of Yugoslavia (``YUG``) and of Serbia and Montenegro
  (``SCG``) too.
* Added the option ``CEDS`` with the area of the Community Emissions Data System which
  is not a country: international shipping and aviation (``CEDS|global``).
* In ``ISO3_PRIMAP1``, the territories which PRIMAP-hist v2.x did not report (``BVT``,
  ``IOT``, ``PCN``, and ``SGS``) are now kept outside of ``World`` instead of being
  removed, because its input data partly contain them. In ``ISO3_PRIMAP1_INPUTS``,
  ``FSU`` is now an alternative code of the USSR (``SUN``), which includes the CIS
  region of EDGAR-HYDE, and the ``CEDS`` option is included.
* Merging categories into a category which has them as children, like the successors
  of a historical country into it, no longer makes the receiving category its own
  child.
* Options can remove categories from the child sets of given parents without removing
  them from the categorization with ``leave_parents``, the counterpart of
  ``join_parents``, e.g. ``{"PCN": ["World"]}``.
