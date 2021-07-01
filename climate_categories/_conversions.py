"""Classes to represent conversion rules between categorizations."""
import csv
import pathlib
import typing
from typing import TYPE_CHECKING

import pyparsing

if TYPE_CHECKING:
    from ._categories import Categorization


class Conversion:
    """Rules for conversion between two categorizations.

    #TODO: always take categorization objects, not strs"""

    # Parsing rules for simple formulas in the CSV
    # Supported operators at the moment are plus and minus
    _operator = pyparsing.Char("+") ^ pyparsing.Char("-")
    _operator_factors = {"+": 1, "-": -1}
    # alphanumeric category codes can be given directly, others have to be quoted
    _category_code = pyparsing.Word(pyparsing.alphanums + ".") ^ pyparsing.QuotedString(
        quoteChar='"', escChar="\\"
    )
    _formula = (
        pyparsing.StringStart()
        + pyparsing.Optional(_operator("unary_op"))
        + _category_code("category_code")
        + pyparsing.ZeroOrMore(_operator("binary_op") + _category_code("category_code"))
        + pyparsing.StringEnd()
    )

    def __init__(
        self,
        categorization_a: str,
        categorization_b: str,
        conversion_factors: typing.List[
            typing.Tuple[typing.Dict[str, int], typing.Dict[str, int]]
        ],
    ):
        self.categorization_a = categorization_a
        self.categorization_b = categorization_b
        self.conversion_factors = conversion_factors

    def _get_categorizations(
        self, cats: typing.Dict[str, "Categorization"]
    ) -> ("Categorization", "Categorization"):
        """Returns categorization_a and categorization_b as Categorization objects."""
        try:
            cat_a = cats[self.categorization_a]
        except KeyError:
            raise KeyError(f"{self.categorization_a!r} not found in categorizations.")
        try:
            cat_b = cats[self.categorization_b]
        except KeyError:
            raise KeyError(f"{self.categorization_b!r} not found in categorizations.")

        return cat_a, cat_b

    def ensure_valid(self, cats: typing.Dict[str, "Categorization"]) -> None:
        """Check if all used codes are contained in the categorizations."""
        cat_a, cat_b = self._get_categorizations(cats)

        for f_a, f_b in self.conversion_factors:
            for code_factors, cat in ((f_a, cat_a), (f_b, cat_b)):
                for code in code_factors:
                    if code not in cat:
                        raise KeyError(f"{code!r} not in {cat}.")

    def describe_detailed(self, cats: typing.Dict[str, "Categorization"]) -> str:
        """Detailed human-readable description of the conversion rules."""
        cat_a, cat_b = self._get_categorizations(cats)
        ret = f"# Mapping between {cat_a} and {cat_b}\n\n"

        ret += "## Simple direct mappings\n\n"
        for f_a, f_b in self.conversion_factors:
            if len(f_a) == 1 and len(f_b) == 1:
                node_a = cat_a[next(iter(f_a))]
                ret += f"<{cat_a}> {node_a}\n"
                node_b = cat_b[next(iter(f_b))]
                ret += f"<{cat_b}> {node_b}\n\n"

        ret += f"## One-to-many mappings - one {cat_a} to many {cat_b}\n\n"
        for f_a, f_b in self.conversion_factors:
            if len(f_a) == 1 and len(f_b) != 1:
                code_a = next(iter(f_a))
                node_a = cat_a[code_a]
                ret += f"<{cat_a}> {node_a}\n"
                b = [f"<{cat_b}> {cat_b[x]}" for x in f_b]
                ret += "\n".join(b) + "\n\n"

        ret += f"## One-to-many-mappings - many {cat_a} to one {cat_b}\n\n"
        for f_a, f_b in self.conversion_factors:
            if len(f_a) != 1 and len(f_b) == 1:
                a = [f"<{cat_a}> {cat_a[x]}" for x in f_a]
                ret += "\n".join(a) + "\n"
                code_b = next(iter(f_b))
                node_b = cat_b[code_b]
                ret += f"<{cat_b}> {node_b}\n\n"

        ret += "## Many-to-many-mappings\n\n"
        for f_a, f_b in self.conversion_factors:
            if len(f_a) != 1 and len(f_b) != 1:
                a = [f"<{cat_a}> {cat_a[x]}" for x in f_a]
                ret += "\n".join(a) + "\n"
                b = [f"<{cat_b}> {cat_b[x]}" for x in f_b]
                ret += "\n".join(b) + "\n\n"

        ret += "## Unmapped categories\n\n"
        fs_a = set()
        fs_b = set()
        for f_a, f_b in self.conversion_factors:
            for code in f_a:
                fs_a.add(cat_a[code])
            for code in f_b:
                fs_b.add(cat_b[code])
        fm_a = set(cat_a.values()) - fs_a
        fm_b = set(cat_b.values()) - fs_b
        ret += f"### {cat_a}\n"
        ret += "\n".join(sorted((str(x) for x in fm_a))) + "\n\n"
        ret += f"### {cat_b}\n"
        ret += "\n".join(sorted((str(x) for x in fm_b))) + "\n\n"

        return ret

    @classmethod
    def _parse_formula(cls, formula: str) -> typing.Dict[str, int]:
        """Parse a formula into factors for categories.

        Parameters
        ----------
        formula: str
            Formula comprising category codes connected with + or - . Alphanumeric
            category codes can be given directly, other category codes must be quoted
            using double quotes.

        Returns
        -------
        code_factors: dict
            mapping of category codes to factors

        Examples
        --------
        >>> Conversion._parse_formula("A + B")
        {'A': 1, 'B': 1}
        >>> Conversion._parse_formula("-A+B")
        {'A': -1, 'B': 1}
        >>> Conversion._parse_formula('"-asdf.#" + B')
        {'-asdf.#': 1, 'B': 1}
        >>> Conversion._parse_formula(" A  -  B")
        {'A': 1, 'B': -1}
        >>> Conversion._parse_formula("-A")
        {'A': -1}
        >>> Conversion._parse_formula('-A+B - "A"')
        {'A': -2, 'B': 1}
        >>> Conversion._parse_formula("-A-")
        Traceback (most recent call last):
        ...
        ValueError: Could not parse: '-A-', error: Expected ...
        >>> Conversion._parse_formula("")
        Traceback (most recent call last):
        ...
        ValueError: Could not parse: '', error: Expected ...
        """
        try:
            tokens = cls._formula.parseString(formula)
        except pyparsing.ParseException as exc:
            raise ValueError(
                f"Could not parse: {formula!r}, error: {exc.msg},"
                f" error at char {exc.loc}"
            )
        code_factors = {}
        # first operator is implicitly a plus, have to handle it specially
        if "unary_op" in tokens:
            op = tokens.pop(0)
        else:
            op = "+"
        code = tokens.pop(0)
        code_factors[code] = cls._operator_factors[op]
        while tokens:
            op = tokens.pop(0)
            code = tokens.pop(0)
            if code in code_factors:
                code_factors[code] += cls._operator_factors[op]
            else:
                code_factors[code] = cls._operator_factors[op]

        return code_factors

    @classmethod
    def _from_csv(cls, fd: typing.TextIO) -> "Conversion":
        conversion_factors = []
        reader = csv.reader(fd, quoting=csv.QUOTE_NONE, escapechar="\\")
        header = next(reader)
        for i, row in enumerate(reader):
            try:
                conversion_factors.append(
                    (cls._parse_formula(row[0]), cls._parse_formula(row[1]))
                )
            except ValueError as err:
                raise ValueError(f"Error in line {i + 2}: {err}")

        return cls(
            categorization_a=header[0],
            categorization_b=header[1],
            conversion_factors=conversion_factors,
        )

    @classmethod
    def from_csv(
        cls, filepath: typing.Union[str, pathlib.Path, typing.TextIO]
    ) -> "Conversion":
        """Read conversion from comma-separated-values file."""
        if not isinstance(filepath, (str, pathlib.Path)):
            return cls._from_csv(filepath)
        fp = pathlib.Path(filepath)
        with fp.open(filepath, newline="") as fd:
            return cls._from_csv(fd)
