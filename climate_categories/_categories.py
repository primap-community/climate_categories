"""Classes to represent and query categorical systems."""

import datetime
import pathlib
import typing

import pandas
import strictyaml


class Category:
    """A single category."""

    def __init__(
        self,
        codes: typing.Tuple[str],
        categorization: "Categorization",
        title: str,
        comment: typing.Optional[str] = None,
    ):
        self.codes = codes
        self.title = title
        self.comment = comment
        self.categorization = categorization

    @classmethod
    def from_spec(cls, code: str, spec: typing.Dict, categorization: "Categorization"):
        codes = [code]
        if "alternative_codes" in spec:
            codes += spec["alternative_codes"]
            del spec["alternative_codes"]
        return cls(codes=tuple(codes), categorization=categorization, **spec)

    def to_spec(self) -> (str, typing.Dict):
        code = self.codes[0]
        spec = {"title": self.title}
        if self.comment is not None:
            spec["comment"] = self.comment
        if len(self.codes) > 1:
            spec["alternative_codes"] = self.codes[1:]
        return code, spec

    def __str__(self) -> str:
        return self.title

    def __eq__(self, other: "Category"):
        return any((x in other.codes for x in self.codes)) and (
            self.categorization is other.categorization
            or self.categorization.name.startswith(other.categorization.name)
            or other.categorization.name.startswith(self.categorization.name)
        )

    def __repr__(self) -> str:
        return f"<Category {self.title!r} {self.codes!r} {self.comment!r}>"


class HierarchicalCategory(Category):
    """A single category from a HierarchicalCategorization."""

    def __init__(
        self,
        codes: typing.Tuple[str],
        categorization: "HierarchicalCategorization",
        title: str,
        comment: typing.Optional[str] = None,
    ):
        Category.__init__(self, codes, categorization, title, comment)
        self.categorization = categorization

    @property
    def children(self) -> typing.List[typing.Set["HierarchicalCategory"]]:
        """The sets of subcategories comprising this category.

        The first set is canonical, the other sets are alternative.
        Only the canonical sets are used to calculate the level of a category."""
        return self.categorization.children(self)

    @property
    def parents(self) -> typing.Set["HierarchicalCategory"]:
        """The super-categories where this category is a member of any set of children.

        Note that all possible parents are returned, not "canonical" parents.
        """
        return self.categorization.parents(self)

    @property
    def level(self) -> int:
        """The level of the category.

        The canonical top-level category has level 1 and its children have level 2 etc.

        To calculate the level, only the first ("canonical") set of children is
        considered for intermediate categories.
        """
        return self.categorization.level(self)

    def __repr__(self) -> str:
        return (
            f"<Category {self.title!r} {self.codes!r} {self.comment!r} "
            f"children: {self.children!r}>"
        )


class Categorization:
    """A single categorization system.

    A categorization system comprises a set of categories, and their relationships as
    well as metadata describing the categorization system itself.

    Use the categorization object like a dictionary, where codes can be translated
    to their meaning using ``cat[code]`` and all codes are available using
    ``cat.keys()``. Metadata about the categorization is provided in attributes.
    If `pandas` is available, you can access a `pandas.DataFrame` with all
    category codes, and their meanings at ``cat.df``.

    Attributes
    ----------
    name : str
        The unique name/code
    references : str
        Citable reference(s)
    title : str
        A short, descriptive title for humans
    comment : str
        Notes and explanations for humans
    institution : str
        Where the categorization originates
    last_update : datetime.date
        The date of the last change
    version : str, optional
        The version of the Categorization, if there are multiple versions
    hierarchical : bool
        True if descendants and ancestors are defined
    """

    hierarchical: bool = False

    def __init__(
        self,
        *,
        categories: typing.Dict[str, typing.Union[typing.Dict, Category]],
        name: str,
        title: str,
        comment: str,
        references: str,
        institution: str,
        last_update: datetime.date,
        version: typing.Optional[str] = None,
    ):
        self._primary_code_map = {}
        self._all_codes_map = {}
        for code, spec in categories.items():
            if isinstance(spec, Category):
                cat = spec
            else:
                cat = Category.from_spec(code=code, spec=spec, categorization=self)

            self._primary_code_map[code] = cat
            for icode in cat.codes:
                self._all_codes_map[icode] = cat

        self.name = name
        self.references = references
        self.title = title
        self.comment = comment
        self.institution = institution
        self.last_update = last_update
        self.version = version

    @classmethod
    def from_yaml(cls, file: typing.Union[str, pathlib.Path]) -> "Categorization":
        """Read Categorization from a StrictYaml file."""
        with open(file) as fd:
            yaml = strictyaml.load(fd.read())
        last_update = datetime.date.fromisoformat(yaml.data["last_update"])
        return cls(
            categories=yaml.data["categories"],
            name=yaml.data["name"],
            title=yaml.data["title"],
            comment=yaml.data["comment"],
            references=yaml.data["references"],
            institution=yaml.data["institution"],
            last_update=last_update,
            version=yaml.data.get("version", None),
        )

    def keys(self) -> typing.KeysView[str]:
        """Iterate over the codes for all categories."""
        return self._primary_code_map.keys()

    def values(self) -> typing.ValuesView[Category]:
        """Iterate over the categories."""
        return self._primary_code_map.values()

    def items(self) -> typing.ItemsView[str, Category]:
        """Iterate over (primary code, category) pairs."""
        return self._primary_code_map.items()

    def all_keys(self) -> typing.KeysView[str]:
        """Iterate over all codes for all categories."""
        return self._all_codes_map.keys()

    def __iter__(self) -> typing.Iterable[str]:
        return iter(self._primary_code_map)

    def __getitem__(self, code: str) -> Category:
        """Get the category for a code."""
        return self._all_codes_map[code]

    def __contains__(self, code: str) -> bool:
        """Can the code be mapped to a category?"""
        return code in self._all_codes_map

    def __len__(self) -> int:
        return len(self._primary_code_map)

    def __repr__(self) -> str:
        return (
            f"<Categorization {self.name} {self.title!r} with {len(self)} categories>"
        )

    def __str__(self) -> str:
        return self.name

    @property
    def df(self) -> "pandas.DataFrame":
        """All category codes as a pandas dataframe."""
        titles = []
        comments = []
        alternative_codes = []
        for cat in self.values():
            titles.append(cat.title)
            comments.append(cat.comment)
            alternative_codes.append(cat.codes[1:])
        return pandas.DataFrame(
            index=self.keys(),
            data={
                "title": titles,
                "comment": comments,
                "alternative_codes": alternative_codes,
            },
        )

    def _extend_prepare(
        self,
        *,
        categories: typing.Optional[typing.Dict[str, typing.Dict]] = None,
        alternative_codes: typing.Optional[typing.Dict[str, str]] = None,
        name: str,
        title: typing.Optional[str] = None,
        comment: typing.Optional[str] = None,
        last_update: typing.Optional[datetime.date] = None,
    ):
        if title is None:
            title = f"{self.title} + {name}"
        else:
            title = self.title + title

        if comment is None:
            comment = f"{self.comment} extended by {name}"
        else:
            comment = self.comment + comment

        if last_update is None:
            last_update = datetime.date.today()

        # serialize the current categories to make sure that we don't modify the
        # old categories' values.
        new_categories = dict((x.to_spec() for x in self.values()))
        if categories is not None:
            new_categories.update(categories)

        if alternative_codes is not None:
            for alias, primary in alternative_codes.items():
                if "alternative_codes" not in new_categories[primary]:
                    new_categories[primary]["alternative_codes"] = tuple()
                new_categories[primary]["alternative_codes"] = new_categories[primary][
                    "alternative_codes"
                ] + (alias,)

        return (name, new_categories, title, comment, last_update)

    def extend(
        self,
        *,
        categories: typing.Optional[typing.Dict[str, typing.Dict]] = None,
        alternative_codes: typing.Optional[typing.Dict[str, str]] = None,
        name: str,
        title: typing.Optional[str] = None,
        comment: typing.Optional[str] = None,
        last_update: typing.Optional[datetime.date] = None,
    ) -> "Categorization":
        """Extend the categorization with additional categories, yielding a new
        categorization.

        Metadata: the ``name``, ``title``, ``comment``, and ``last_update`` are updated
        automatically (see below), the ``institution`` and ``references`` are deleted
        and the values for ``version`` and ``hierarchical`` are kept.
        You can set more accurate metadata (for example, your institution) on the
        returned object if needed.

        Parameters
        ----------
        categories: dict, optional
           Map of new category codes to their specification. The specification is a
           dictionary with the keys "title", optionally "comment", and optionally
           "alternative_codes".
        alternative_codes: dict, optional
           Map of new alternative codes. A dictionary with the new alternative code
           as key and existing code as value.
        name : str
           The name of your extension. The returned Categorization will have a name
           of "{old_name}_{name}", indicating that it is an extension of the underlying
           Categorization.
        title : str, optional
           A string to add to the original title. If not provided, " + {name}" will be
           used.
        comment : str, optional
           A string to add to the original comment. If not provided,
           " extended by {name}" will be used.
        last_update : datetime.date, optional
           The date of the last update to this extension. Today will be used if not
           provided.

        Returns
        -------
        Extended categorization : Categorization
        """
        (name, categories, title, comment, last_update) = self._extend_prepare(
            name=name,
            categories=categories,
            title=title,
            comment=comment,
            last_update=last_update,
            alternative_codes=alternative_codes,
        )

        return Categorization(
            categories=categories,
            name=f"{self.name}_{name}",
            references="",
            title=title,
            comment=comment,
            institution="",
            last_update=last_update,
            version=self.version,
        )


class HierarchicalCategorization(Categorization):
    """In a hierarchical categorization, descendants and ancestors (parents and
    children) are defined for each category.

    Attributes
    ----------
    total_sum : bool
        If the sum of the values of children equals the value of the parent for
        extensive quantities. For example, a Categorization containing the Countries in
        the EU and the EU could set `total_sum = True`, because the emissions of all
        parts of the EU must equal the emissions of the EU. On the contrary, a
        categorization of Industries with categories `Power:Fossil Fuels` and
        `Power:Gas` which are both children of `Power` must set `total_sum = False`
        to avoid double counting of fossil gas.
    """

    def __init__(
        self,
        *,
        code_meanings: typing.Dict[str, str],
        hierarchy: typing.Dict[str, typing.List[typing.Set[str]]],
        name: str,
        references: str,
        title: str,
        comment: str,
        institution: str,
        last_update: datetime.date,
        version: typing.Optional[str] = None,
        total_sum: bool = False,
    ):
        super(HierarchicalCategorization, self).__init__(
            code_meanings=code_meanings,
            name=name,
            references=references,
            title=title,
            comment=comment,
            institution=institution,
            last_update=last_update,
            version=version,
            hierarchical=True,
        )
        self._hierarchy = hierarchy
        self.total_sum = total_sum

    @classmethod
    def from_yaml(
        cls, file: typing.Union[str, pathlib.Path]
    ) -> "HierarchicalCategorization":
        """Read HierarchicalCategorization from a StrictYaml file."""
        raise NotImplementedError

    def extend(
        self,
        *,
        name: str,
        categories: typing.Dict[str, str],
        children: typing.Optional[
            typing.Iterable[typing.Tuple[str, typing.Iterable[str]]]
        ] = None,
        title: typing.Optional[str] = None,
        comment: typing.Optional[str] = None,
        last_update: typing.Optional[datetime.date] = None,
    ) -> "HierarchicalCategorization":
        """Extend the categorization with additional categories and relationships,
        yielding a new categorization.

        Metadata: the ``name``, ``title``, ``comment``, and ``last_update`` are updated
        automatically (see below), the ``institution`` is deleted, and the values for
        ``version``, ``hierarchical``, and ``total_sum`` are kept. You can set more
        accurate metadata (for example, your institution) on the returned object if
        needed.

        Using this function, only new relationships between (existing and new)
        categories can be added. If you need to delete or reorder existing
        relationships, look at ``extend_with_hierarchy``.

        Parameters
        ----------
        name : str
           The name of your extension. The returned Categorization will have a name
           of "{old_name}_{name}", indicating that it is an extension of the underlying
           Categorization.
        categories : dict
           Map of new category codes to their meaning.
        children : list of (parent, {child1, child2, …}) mappings
           Map of parent category codes to sets of child category codes. The given
           relationships are inserted into the hierarchy. Both existing and new category
           codes can be used as parents or children. parent codes can be given in
           multiple entries if multiple sets of children are possible. Sets of children
           will be added to the hierarchy in the specified order at the end of the
           list of sets of children.
        title : str, optional
           A string to add to the original title. If not provided, " + {name}" will be
           used.
        comment : str, optional
           A string to add to the original comment. If not provided,
           " extended by {name}" will be used.
        last_update : datetime.date, optional
           The date of the last update to this extension. Today will be used if not
           provided.

        Returns
        -------
        Extended categorization : HierarchicalCategorization
        """
        (name, categories, title, comment, last_update) = self._extend_prepare(
            name, categories, title, comment, last_update
        )

        hierarchy = self._hierarchy.copy()
        if children is not None:
            for (parent, child_set) in children:
                if parent in hierarchy:
                    hierarchy[parent].append(child_set)
                else:
                    hierarchy[parent] = [child_set]

        return HierarchicalCategorization(
            code_meanings=categories,
            hierarchy=hierarchy,
            name=f"{self.name}_{name}",
            references="",
            title=title,
            comment=comment,
            institution="",
            last_update=last_update,
            version=self.version,
        )

    def extend_with_hierarchy(
        self,
        *,
        name: str,
        categories: typing.Dict[str, str],
        hierarchy: typing.Dict[str, typing.List[typing.Set[str]]],
        title: typing.Optional[str] = None,
        comment: typing.Optional[str] = None,
        last_update: typing.Optional[datetime.date] = None,
    ):
        """Extend the categorization with additional categories and a new hierarchy,
        yielding a new categorization.

        Metadata: the ``name``, ``title``, ``comment``, and ``last_update`` are updated
        automatically (see below), the ``institution`` is deleted, and the values for
        ``version``, ``hierarchical``, and ``total_sum`` are kept. You can set more
        accurate metadata (for example, your institution) on the returned object if
        needed.

        Parameters
        ----------
        name : str
           The name of your extension. The returned Categorization will have a name
           of "{old_name}_{name}", indicating that it is an extension of the underlying
           Categorization.
        categories : dict
           Map of new category codes to their meaning.
        hierarchy : dict
           Map of parent category codes to lists of sets of child category codes.
           given hierarchy replaces the original hierarchy.
        title : str, optional
           A string to add to the original title. If not provided, " + {name}" will be
           used.
        comment : str, optional
           A string to add to the original comment. If not provided, " extend by {name}"
           will be used.
        last_update : datetime.date, optional
           The date of the last update to this extension. Today will be used if not
           provided.

        Returns
        -------
        Extended categorization : HierarchicalCategorization
        """

        (name, categories, title, comment, last_update) = self._extend_prepare(
            name, categories, title, comment, last_update
        )

        return HierarchicalCategorization(
            code_meanings=categories,
            hierarchy=hierarchy,
            name=f"{self.name}_{name}",
            references="",
            title=title,
            comment=comment,
            institution="",
            last_update=last_update,
            version=self.version,
        )

    def level(self, code: str) -> int:
        """The level of the given code.

        The topmost category has level 1 and its children have level 2 etc.

        If there is more than one topmost category or multiple ways to the topmost
        category, the shortest path to a topmost category is used to calculate the
        level.
        """
        raise NotImplementedError

    def parents(self, code: str) -> typing.List[str]:
        """The direct parents of the given category."""
        return [x for x in self._hierarchy if code in set().union(*self._hierarchy[x])]

    def children(self, code: str) -> typing.List[typing.Set[str]]:
        """The list of sets of direct children of the given category."""
        if code in self._hierarchy:
            return list(self._hierarchy[code])
        else:
            return []

    @property
    def hierarchy(self) -> typing.Dict[str, typing.List[typing.Set[str]]]:
        """The full hierarchy as a dict mapping parent codes to lists of sets of
        children."""
        return self._hierarchy
