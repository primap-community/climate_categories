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

Open questions
~~~~~~~~~~~~~~

 * What would be a good file format for categorizations? "Three CSVs" is fast and
   easily modifiable in Excel / Calc / pycharm, but somewhat unorganized. YAML is
   slow to parse, arbitrarily complex and there are no sophisticated editors.
   pon or python files would be great for python, but maybe we also want the same
   data for R or julia or whatever. Maybe we need to parse and "compile" YAML files
   during build, that at least would alleviate the problem of YAML being slow to parse.

Other use cases
---------------

 * Open: mapping between categorizations, e.g. different versions
 * Visualization of categorizations
 * Do we need more than just a code and a meaning for categories? Like for
   whole categorizations: a code, a title, a comment? How would that map to a pythonic
   API?
