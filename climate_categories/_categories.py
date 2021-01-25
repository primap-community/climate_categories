"""Classes to represent and query categorical systems."""

import csv
import datetime
import pathlib
from typing import Dict, Iterable, List, Optional, Tuple, Union

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
    def from_csvs(
        cls,
        *,
        metadata_csv: Union[pathlib.Path, str],
        data_csv: Union[pathlib.Path, str],
    ) -> "Categorization":
        """Construct a Categorization object from two CSV files.

        Parameters
        ----------
        metadata_csv : Path or str
            CSV file which contains the metadata as (key, value) pairs where the key
            is the attribute name and one (key, value) pair per row.
        data_csv : Path or str
            CSV file which contains the translation of category codes to their meanings
            as (code, meaning) pairs with one pair per row.

        Returns
        -------
        Categorization
        """
        meta = {}
        with open(metadata_csv, newline="") as fd:
            r = csv.reader(fd)
            for key, value in r:
                meta[key] = value

        code_meanings = {}
        with open(data_csv, newline="") as fd:
            r = csv.reader(fd)
            for key, value in r:
                code_meanings[key] = value

        return cls(
            code_meanings=code_meanings,
            name=meta["name"],
            references=meta["references"],
            title=meta["title"],
            comment=meta["comment"],
            institution=meta["institution"],
            last_update=datetime.date.fromisoformat(meta["last_update"]),
            version=meta["version"] if "version" in meta else None,
            hierarchical=meta["bool"] == "True" if "bool" in meta else False,
        )

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
        hierarchy: Dict[str, Iterable[str]],
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

    @staticmethod
    def _parse_hierarchy_csv(reader: csv.reader) -> List[Tuple[str, str]]:
        parents = []
        previous_lvl = -1
        previous_code = None
        edges = []
        for i, row in enumerate(reader):
            for lvl, code in enumerate(row):
                if code:
                    break
            if lvl == previous_lvl + 1:  # child of previous node
                if previous_code is not None:  # not first row
                    parents.append(previous_code)
            elif lvl == previous_lvl:
                pass  # same parents
            elif lvl < previous_lvl:
                parents = parents[:lvl]
            else:
                raise ValueError(
                    f"Unexpected indent at line {i} for {code}."
                    "Should be at most one level deeper than the previous line."
                )

            if parents:
                edges.append((parents[-1], code))

            previous_lvl = lvl
            previous_code = code

        return edges

    @classmethod
    def from_csvs(
        cls,
        *,
        metadata_csv: Union[pathlib.Path, str],
        data_csv: Union[pathlib.Path, str],
        hierarchy_csv: Union[pathlib.Path, str],
    ) -> "HierarchicalCategorization":
        """Construct a Categorization object from three CSV files.

        Parameters
        ----------
        metadata_csv : Path or str
            CSV file which contains the metadata as (key, value) pairs where the key
            is the attribute name and one (key, value) pair per row.
        data_csv : Path or str
            CSV file which contains the translation of category codes to their meanings
            as (code, meaning) pairs with one pair per row.
        hierarchy_csv : Path or str
            CSV file which contains the hierarchy of categories. Categories are
            represented by their codes. There should be one code per row, the column
            of the code determines the categories level, child categories are one
            column to the right of parent categories.

        Returns
        -------
        HierarchicalCategorization
        """
        meta = {}
        with open(metadata_csv, newline="") as fd:
            r = csv.reader(fd)
            for key, value in r:
                meta[key] = value

        code_meanings = {}
        with open(data_csv, newline="") as fd:
            r = csv.reader(fd)
            for key, value in r:
                code_meanings[key] = value

        with open(hierarchy_csv, newline="") as fd:
            edges = cls._parse_hierarchy_csv(csv.reader(fd))

        hierarchy = {}
        for parent, child in edges:
            if parent in hierarchy:
                hierarchy[parent].append(child)
            else:
                hierarchy[parent] = [child]

        return cls(
            code_meanings=code_meanings,
            hierarchy=hierarchy,
            name=meta["name"],
            references=meta["references"],
            title=meta["title"],
            comment=meta["comment"],
            institution=meta["institution"],
            last_update=datetime.date.fromisoformat(meta["last_update"]),
            version=meta["version"] if "version" in meta else None,
            total_sum=meta["total_sum"] == "True" if "total_sum" in meta else False,
        )

    def extend(
        self,
        *,
        name: str,
        categories: Dict[str, str],
        children: Optional[Dict[str, Iterable[str]]] = None,
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
        children : dict, optional
           Map of parent category codes to lists of child category codes. The given
           relationships are inserted into the hierarchy. Both existing and new category
           codes can be used as parents or children.
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

        hierarchy = self._hierarchy.copy()
        hierarchy.update(children)

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
        hierarchy: Dict[str, Iterable[str]],
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
           Map of parent category codes to lists of child category codes. The given
           hierarchy replaces the original hierarchy.
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
        """
        raise NotImplementedError

    def parents(self, code: str) -> List[str]:
        """The direct parents of the given category."""
        return [x for x in self._hierarchy if code in self._hierarchy[x]]

    def children(self, code: str) -> List[str]:
        """The direct children of the given category."""
        return list(self._hierarchy[code])

    @property
    def hierarchy(self) -> Dict[str, List[str]]:
        """The full hierarchy as a dict mapping parent codes to lists of children."""
        return {x: list(self._hierarchy[x]) for x in self._hierarchy}
