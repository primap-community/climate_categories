"""Classes to represent conversion rules between categorizations."""
import csv
import pathlib
import typing

import pyparsing

from ._categories import Categorization


class Conversion:
    """Rules for conversion between two categorizations."""

    # Parsing rules for simple formulas in the CSV
    # Supported operators at the moment are plus and minus
    _operator = pyparsing.Char("+") ^ pyparsing.Char("-")
    _operator_factors = {"+": 1, "-": -1}
    # alphanumeric category codes can be given directly, others have to be quoted
    _category_code = pyparsing.Word(pyparsing.alphanums) ^ pyparsing.QuotedString(
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

    def ensure_valid(self, cats: typing.Dict[str, Categorization]) -> None:
        """Check if all used codes are contained in the categorizations."""
        try:
            cat_a = cats[self.categorization_a]
        except KeyError:
            raise KeyError(f"{self.categorization_a!r} not found in categorizations.")
        try:
            cat_b = cats[self.categorization_b]
        except KeyError:
            raise KeyError(f"{self.categorization_b!r} not found in categorizations.")

        for f_a, f_b in self.conversion_factors:
            for code_factors, cat in ((f_a, cat_a), (f_b, cat_b)):
                for code in code_factors:
                    if code not in cat:
                        raise KeyError(f"{code!r} not in {cat}.")

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
