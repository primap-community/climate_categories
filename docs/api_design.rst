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
* What about categorizations with multiple codes meaning the same thing?

Open questions
~~~~~~~~~~~~~~

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
* compiled to whatever is fast / easy to parse, if necessary.

Other use cases
---------------

* Open: mapping between categorizations, e.g. different versions
* Visualization of categorizations
* Updated datasets: Cases like ISO-3166, which are updated regularly, and it is
  necessary to read also
  historical datasets containing old codes which either have to be translated or
  even split into other codes. It would be great if the user does not have to
  specify a version, but things happen automatically.
