"""Classes to represent and query categorical systems."""

import datetime
import pathlib
from typing import Iterable, List, Optional, Union

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
        name: str,
        references: str,
        title: str,
        comment: str,
        institution: str,
        last_update: datetime.date,
        version: Optional[str] = None,
        hierarchical: bool = False,
    ):
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

    def __getitem__(self, code: str) -> str:
        """Get the meaning for a code."""
        raise NotImplementedError

    def keys(self) -> Iterable:
        """Iterable of all category codes."""
        raise NotImplementedError

    @property
    def df(self) -> "pandas.Dataframe":
        """All category codes and meanings as a pandas dataframe."""
        raise NotImplementedError


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
            name=name,
            references=references,
            title=title,
            comment=comment,
            institution=institution,
            last_update=last_update,
            version=version,
            hierarchical=True,
        )
        self.total_sum = total_sum

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
        raise NotImplementedError

    def level(self, code: str) -> int:
        """The level of the given code.

        The topmost category has level 1 and its children have level 2 etc.
        """
        raise NotImplementedError

    def parents(self, code: str) -> List[str]:
        """The direct parents of the given category."""
        raise NotImplementedError

    def children(self, code: str) -> List[str]:
        """The direct children of the given category."""
        raise NotImplementedError
