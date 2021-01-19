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

API
~~~

::

    import climate_categories
    climate_categories.cat  # dict mapping categorization names to objects
    climate_categories.CategoryName  # categorization object
    CategoryName.name: str
    CategoryName.references: str  # Papers, URLs etc. describing the categorization
    CategoryName.title: str  # a succinct description
    CategoryName.comment: str  # a long-form description or notes
    CategoryName.institution: str  # where the categorization originates
    CategoryName.last_update: datetime.date  # last time the categorization was changed
    CategoryName.version: Optional[str]  # if applicable, the version
    CategoryName[code]  # translate a code into its meaning
    CategoryName.keys()  # iterable of all codes in the categorization
    CategoryName.hierarchical: bool  # are descendants and ancestors defined
    CategoryName.total_sum: bool  # does the sum of direct descendants equal the total
    CategoryName.level(code) -> int  # get the level of a code
    CategoryName.parents(code) -> list[str]  # get the codes of direct parents
    CategoryName.children(code) -> list[str]  # get the codes of direct children
    CategoryName.df: pd.DataFrame  # code, meaning(, level) as a dataframe
    climate_categories.find(code) -> list[(str, str)]  # find a code anywhere
