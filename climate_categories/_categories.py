"""Classes to represent and query categorical systems."""

import datetime
import pathlib
import typing

import networkx as nx
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
        return cls(
            codes=tuple(codes),
            categorization=categorization,
            title=spec["title"],
            comment=spec.get("comment", None),
        )

    def to_spec(self) -> (str, typing.Dict):
        code = self.codes[0]
        spec = {"title": self.title}
        if self.comment is not None:
            spec["comment"] = self.comment
        if len(self.codes) > 1:
            spec["alternative_codes"] = self.codes[1:]
        return code, spec

    def __str__(self) -> str:
        s = "Category "
        if len(self.codes) == 1:
            s += f"{self.codes[0]}"
        else:
            s += f"{self.codes}"
        if self.title is not None:
            s += f" {self.title!r}"
        return s

    def __eq__(self, other: "Category"):
        if not isinstance(other, Category):
            return False
        return any((x in other.codes for x in self.codes)) and (
            self.categorization is other.categorization
            or self.categorization.name.startswith(other.categorization.name)
            or other.categorization.name.startswith(self.categorization.name)
        )

    def __repr__(self) -> str:
        return f"<Category {self.codes[0]}>"

    def __hash__(self):
        return hash(self.codes[0])


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

    def __str__(self) -> str:
        s = "Category "
        if len(self.codes) == 1:
            s += f"{self.codes[0]}"
        else:
            s += f"{self.codes}"
        if self.title is not None:
            s += f" {self.title!r}"
        s += (
            f" children: "
            f"{[tuple(sorted((c.codes[0] for c in cs))) for cs in self.children]!r}"
        )
        return s

    def __repr__(self) -> str:
        return f"<HierarchicalCategory {self.codes[0]}>"


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

    def _add_categories(self, categories: typing.Dict[str, typing.Dict]):
        for code, spec in categories.items():
            cat = Category.from_spec(code=code, spec=spec, categorization=self)

            self._primary_code_map[code] = cat
            for icode in cat.codes:
                self._all_codes_map[icode] = cat

    def __init__(
        self,
        *,
        categories: typing.Dict[str, typing.Dict],
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
        self._add_categories(categories)

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
    canonical_top_level_category : HierarchicalCategory
        The level of a category is calculated with respect to the canonical top level
        category. Commonly, this will be the world total or a similar category. If the
        canonical top level category is not set (i.e. is ``None``), levels are not
        defined for categories.
    """

    hierarchical = True

    def _add_categories(self, categories: typing.Dict[str, typing.Dict]):
        for code, spec in categories.items():
            cat = HierarchicalCategory.from_spec(
                code=code, spec=spec, categorization=self
            )

            self._primary_code_map[code] = cat
            self._graph.add_node(cat)
            for icode in cat.codes:
                self._all_codes_map[icode] = cat

        for code, spec in categories.items():
            if "children" in spec:
                parent = self._all_codes_map[code]
                for i, child_set in enumerate(spec["children"]):
                    for child_code in child_set:
                        self._graph.add_edge(
                            parent, self._all_codes_map[child_code], set=i
                        )

    def __init__(
        self,
        *,
        categories: typing.Dict[str, typing.Dict],
        name: str,
        title: str,
        comment: str,
        references: str,
        institution: str,
        last_update: datetime.date,
        version: typing.Optional[str] = None,
        total_sum: bool,
        canonical_top_level_category: typing.Optional[str] = None,
    ):
        self._graph = nx.MultiDiGraph()
        Categorization.__init__(
            self,
            categories=categories,
            name=name,
            title=title,
            comment=comment,
            references=references,
            institution=institution,
            last_update=last_update,
            version=version,
        )
        self.total_sum = total_sum
        if canonical_top_level_category is None:
            self.canonical_top_level_category: typing.Optional[
                HierarchicalCategory
            ] = None
        else:
            self.canonical_top_level_category = self._all_codes_map[
                canonical_top_level_category
            ]

    def __getitem__(self, code: str) -> HierarchicalCategory:
        """Get the category for a code."""
        return self._all_codes_map[code]

    def values(self) -> typing.ValuesView[HierarchicalCategory]:
        """Iterate over the categories."""
        return self._primary_code_map.values()

    def items(self) -> typing.ItemsView[str, HierarchicalCategory]:
        """Iterate over (primary code, category) pairs."""
        return self._primary_code_map.items()

    @classmethod
    def from_yaml(
        cls, file: typing.Union[str, pathlib.Path]
    ) -> "HierarchicalCategorization":
        """Read Categorization from a StrictYaml file."""
        with open(file) as fd:
            yaml = strictyaml.dirty_load(fd.read(), allow_flow_style=True)
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
            total_sum=bool(yaml.data["total_sum"]),
            canonical_top_level_category=yaml.data.get(
                "canonical_top_level_category", None
            ),
        )

    @property
    def _canonical_subgraph(self) -> nx.DiGraph:
        return nx.DiGraph(
            self._graph.edge_subgraph(
                ((u, v, 0) for (u, v, s) in self._graph.edges(data="set") if s == 0)
            )
        )

    def extend(
        self,
        *,
        categories: typing.Optional[typing.Dict[str, typing.Dict]] = None,
        alternative_codes: typing.Optional[typing.Dict[str, str]] = None,
        children: typing.Optional[typing.List[tuple]] = None,
        name: str,
        title: typing.Optional[str] = None,
        comment: typing.Optional[str] = None,
        last_update: typing.Optional[datetime.date] = None,
    ) -> "HierarchicalCategorization":
        """Extend the categorization with additional categories and relationships,
        yielding a new categorization.

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
        children: list, optional
           List of ``(parent, (child1, child2, …))`` pairs. The given relationships will
           be inserted in the extended categorization.
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
        Extended categorization : HierarchicalCategorization
        """
        (name, categories, title, comment, last_update) = self._extend_prepare(
            name=name,
            categories=categories,
            title=title,
            comment=comment,
            last_update=last_update,
            alternative_codes=alternative_codes,
        )

        def add_child_set(parent, child_set):
            if "children" not in categories[parent]:
                categories[parent]["children"] = []
            categories[parent]["children"].append(child_set)

        for cat in self.values():
            for child_set in cat.children:
                add_child_set(cat.codes[0], [c.codes[0] for c in child_set])

        if children is not None:
            for parent, child_set in children:
                add_child_set(parent, child_set)

        return HierarchicalCategorization(
            categories=categories,
            name=f"{self.name}_{name}",
            references="",
            title=title,
            comment=comment,
            institution="",
            last_update=last_update,
            version=self.version,
            total_sum=self.total_sum,
            canonical_top_level_category=self.canonical_top_level_category.codes[0],
        )

    @property
    def df(self) -> "pandas.DataFrame":
        """All category codes as a pandas dataframe."""
        titles = []
        comments = []
        alternative_codes = []
        children = []
        for cat in self.values():
            titles.append(cat.title)
            comments.append(cat.comment)
            alternative_codes.append(cat.codes[1:])
            children.append(
                tuple(tuple(sorted(c.codes[0] for c in cs)) for cs in cat.children)
            )
        return pandas.DataFrame(
            index=self.keys(),
            data={
                "title": titles,
                "comment": comments,
                "alternative_codes": alternative_codes,
                "children": children,
            },
        )

    def level(self, cat: typing.Union[str, HierarchicalCategory]) -> int:
        """The level of the given category.

        The canonical top-level category has level 1 and its children have level 2 etc.

        To calculate the level, first only the first ("canonical") set of children is
        considered. Only if no path from the canonical top-level category to the
        given category can be found all other sets of children are considered to
        calculate the level.
        """
        if not isinstance(cat, HierarchicalCategory):
            return self.level(self[cat])
        if not isinstance(self.canonical_top_level_category, HierarchicalCategory):
            raise ValueError(
                "Can not calculate the level without a canonical_top_level_category."
            )

        # first use the canonical subgraph for shortest paths
        csg = self._canonical_subgraph
        try:
            sp = nx.shortest_path_length(csg, self.canonical_top_level_category, cat)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            try:
                sp = nx.shortest_path_length(
                    self._graph, self.canonical_top_level_category, cat
                )
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                raise ValueError(
                    f"{cat.codes[0]!r} is not a transitive child of the "
                    f"canonical top level "
                    f"{self.canonical_top_level_category.codes[0]!r}."
                )

        return sp + 1

    def parents(
        self, cat: typing.Union[str, HierarchicalCategory]
    ) -> typing.Set[HierarchicalCategory]:
        """The direct parents of the given category."""
        if not isinstance(cat, HierarchicalCategory):
            return self.parents(self._all_codes_map[cat])

        return set(self._graph.predecessors(cat))

    def children(
        self, cat: typing.Union[str, HierarchicalCategory]
    ) -> typing.List[typing.Set[HierarchicalCategory]]:
        """The list of sets of direct children of the given category."""
        if not isinstance(cat, HierarchicalCategory):
            return self.children(self._all_codes_map[cat])

        children_dict = {}
        for (_, child, setno) in self._graph.edges(cat, "set"):
            if setno not in children_dict:
                children_dict[setno] = []
            children_dict[setno].append(child)

        children = [set(children_dict[x]) for x in sorted(children_dict.keys())]
        return children
