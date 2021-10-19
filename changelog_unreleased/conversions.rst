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
