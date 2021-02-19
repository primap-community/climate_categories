==========
API Design
==========

Querying
--------

Use cases
~~~~~~~~~

* get a list of all categorizations
* get a list of all codes in a categorization
* get metadata about a categorization (is it hierarchical, source, description,
  last update, version)
* translate a code into its meaning using a specific categorization
* find a code in any categorization, maybe using levenshtein distance or so?
* for hierarchical categorizations: Get the level of a code, get the ancestors, get
  the descendants
* get a categorization as a pandas dataframe

Open questions
~~~~~~~~~~~~~~

* What about categorizations with multiple codes meaning the same thing?
* What about code normalization?

Definition
----------

Use cases
~~~~~~~~~

* extend a categorization with some additional categories
* define a new categorization from a file

File format
~~~~~~~~~~~

* flat YAML in the https://github.com/crdoconnor/strictyaml flavour will be used as the
  preferred form for modification.
* compiled to whatever is fast / easy to parse.

Other use cases
---------------

* Open: mapping between categorizations, e.g. different versions
* Visualization of categorizations
* Do we need more than just a code and a meaning for categories? Like for
  whole categorizations: a code, a title, a comment? How would that map to a pythonic
  API?
* Updated datasets: Cases like ISO-3166, which are updated regularly, and it is
  necessary to read also
  historical datasets containing old codes which either have to be translated or
  even split into other codes. It would be great if the user does not have to
  specify a version, but things happen automatically.
* Alternative subcategories: Cases like IPCC sectoral categories, which are sometimes
  reported with different
  resolution (like only a report for the sum of categories 2B2 + 2B3). Here, it
  should still be possible to calculate 2B from all its children. "alternative
  children". Ideally, it would be possible to determine the correct version
  of the hierarchy automatically.
