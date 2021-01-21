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

Other use cases
---------------

 * Open: mapping between categorizations, e.g. different versions
 * Visualization of categorizations
