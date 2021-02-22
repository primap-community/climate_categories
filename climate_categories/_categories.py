"""Classes to represent and query categorical systems."""

import datetime
import pathlib
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

try:
    import pandas
except ImportError:
    pandas = None


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

    def __init__(
        self,
        *,
        code_meanings: Dict[str, str],
        name: str,
        references: str,
        title: str,
        comment: str,
        institution: str,
        last_update: datetime.date,
        version: Optional[str] = None,
        hierarchical: bool = False,
    ):
        self._codes = code_meanings
        self.name = name
        self.references = references
        self.title = title
        self.comment = comment
        self.institution = institution
        self.last_update = last_update
        self.version = version
        self.hierarchical = hierarchical

    @classmethod
    def from_yaml(cls, file: Union[str, pathlib.Path]) -> "HierarchicalCategorization":
        """Read Categorization from a StrictYaml file."""
        raise NotImplementedError

    def _extend_prepare(
        self,
        name: str,
        categories: Dict[str, str],
        title: Optional[str] = None,
        comment: Optional[str] = None,
        last_update: Optional[datetime.date] = None,
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

        code_meanings = self._codes.copy()
        code_meanings.update(categories)

        return (name, categories, title, comment, last_update)

    def extend(
        self,
        *,
        name: str,
        categories: Dict[str, str],
        title: Optional[str] = None,
        comment: Optional[str] = None,
        last_update: Optional[datetime.date] = None,
    ) -> "Categorization":
        """Extend the categorization with additional categories, yielding a new
        categorization.

        Metadata: the ``name``, ``title``, ``comment``, and ``last_update`` are updated
        automatically (see below), the ``institution`` is deleted, and the values for
        ``version`` and ``hierarchical`` are kept. You can set more accurate metadata
        (for example, your institution) on the returned object if needed.

        Parameters
        ----------
        name : str
           The name of your extension. The returned Categorization will have a name
           of "{old_name}_{name}", indicating that it is an extension of the underlying
           Categorization.
        categories : dict
           Map of new category codes to their meaning.
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
        Extended categorization : Categorization
        """
        (name, categories, title, comment, last_update) = self._extend_prepare(
            name, categories, title, comment, last_update
        )

        return Categorization(
            code_meanings=categories,
            name=f"{self.name}_{name}",
            references="",
            title=title,
            comment=comment,
            institution="",
            last_update=last_update,
            version=self.version,
        )

    def __getitem__(self, code: str) -> str:
        """Get the meaning for a code."""
        return self._codes[code]

    def keys(self) -> Iterable:
        """Iterable of all category codes."""
        return self._codes.keys()

    @property
    def df(self) -> "pandas.DataFrame":
        """All category codes and meanings as a pandas dataframe."""
        if pandas is None:
            raise ImportError("pandas not found")
        return pandas.DataFrame(
            index=self._codes.keys(), data={"meaning": self._codes.values()}
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
        code_meanings: Dict[str, str],
        hierarchy: Dict[str, List[Set[str]]],
        name: str,
        references: str,
        title: str,
        comment: str,
        institution: str,
        last_update: datetime.date,
        version: Optional[str] = None,
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
    def from_yaml(cls, file: Union[str, pathlib.Path]) -> "HierarchicalCategorization":
        """Read HierarchicalCategorization from a StrictYaml file."""
        raise NotImplementedError

    def extend(
        self,
        *,
        name: str,
        categories: Dict[str, str],
        children: Optional[Iterable[Tuple[str, Iterable[str]]]] = None,
        title: Optional[str] = None,
        comment: Optional[str] = None,
        last_update: Optional[datetime.date] = None,
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
        categories: Dict[str, str],
        hierarchy: Dict[str, List[Set[str]]],
        title: Optional[str] = None,
        comment: Optional[str] = None,
        last_update: Optional[datetime.date] = None,
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

    def parents(self, code: str) -> List[str]:
        """The direct parents of the given category."""
        return [x for x in self._hierarchy if code in set().union(*self._hierarchy[x])]

    def children(self, code: str) -> List[Set[str]]:
        """The list of sets of direct children of the given category."""
        if code in self._hierarchy:
            return list(self._hierarchy[code])
        else:
            return []

    @property
    def hierarchy(self) -> Dict[str, List[Set[str]]]:
        """The full hierarchy as a dict mapping parent codes to lists of sets of
        children."""
        return self._hierarchy
