"""Access to all categorizations is provided directly at the module level, using the
names of categorizations. To access the example categorization `Excat`, simply use
`climate_categories.Excat` .
"""

__author__ = """Mika Pflüger"""
__email__ = "mika.pflueger@pik-potsdam.de"
# fmt: off
# bump2version wants single quotes
__version__ = '0.1.0'
# fmt: on

import datetime
import typing

from . import search
from ._categories import Categorization, HierarchicalCategorization

Excat = Categorization(
    name="Excat",
    references="doi:0000000/000000000000",
    title="The Example Categorization",
    comment="This is an example of a simple categorization.",
    institution="PIK",
    last_update=datetime.date(2021, 1, 19),
    code_meanings={"A": "Category A", "B": "Category B"},
)

cats = {"Excat": Excat}


def find(code: str) -> typing.List[typing.Tuple[str, str]]:
    """Find the given code in all known categorizations."""
    return search.search(code, cats.values())


__all__ = ["cats", "Categorization", "HierarchicalCategorization", "Excat", "find"]
