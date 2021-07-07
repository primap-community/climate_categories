"""Classes to represent conversion rules between categorizations."""
import csv
import dataclasses
import datetime
import pathlib
import typing
from typing import TYPE_CHECKING

import pyparsing

if TYPE_CHECKING:
    from ._categories import Categorization


@dataclasses.dataclass(frozen=True)
class ConversionRule:
    """Rule to convert between categories from two different categorizations.

    Supports one-to-one relationships, one-to-many relationships in both directions and
    many-to-many relationships. For each category, a factor is given which can also be
    negative to model relationships like A = B - C.

    Using auxiliary_categories, a rule can be restricted to specific auxiliary
    categories only.

    Attributes
    ----------
    factors_categories_a : dict mapping codes to factors
        Map of category codes from the first categorization to factors. For a simple
        addition, use factor 1, to subtract the category, use factor -1.
    factors_categories_b : dict mapping codes to factors
        Map of category codes from the second categorization to factors. For a simple
        addition, use factor 1, to subtract the category, use factor -1.
    auxiliary_categories : dict[str, set[str]]
        Map of auxiliary categorization names to sets of auxiliary category codes. Not
        all auxiliary categorizations need to be specified, and if an auxiliary
        categorization is not specified (or an empty set of category codes is given),
        the validity of the rule is not restricted.
        If an auxiliary categorization is specified and category codes are given, the
        rule is only valid for the given category codes. If multiple auxiliary
        categorizations are given, the rule is only valid if all auxiliary
        categorizations match.
    """

    factors_categories_a: typing.Dict[str, int]
    factors_categories_b: typing.Dict[str, int]
    auxiliary_categories: typing.Dict[str, typing.Set[str]]


@dataclasses.dataclass
class ConversionRules:
    """Rules for conversion between two categorizations, with support for
    alternative rules depending on auxiliary categorizations.

    This class supports parsing the rules from a specification file and other
    operations which can be performed on the pure rules without knowledge of the
    categorization objects themselves.

    Attributes
    ----------
    categorization_a_name : str
        Name of the first categorization.
    categorization_b_name : str
        Name of the second categorization.
    auxiliary_categorizations_names : list of str, optional
        Names of the auxiliary categorizations.
    rules : list of ConversionRule
        The actual rules for conversion between individual categories or sets of
        categories.
    comment : str, optional
        Notes and explanations for humans.
    references : str, optional
        Citable reference(s) for the conversion.
    institution : str, optional
        Where the conversion originates.
    last_update : datetime.date, optional
        The date of the last change.
    version : str, optional
        The version of the ConversionRules, if there are multiple versions.
    """

    categorization_a_name: str
    categorization_b_name: str
    rules: typing.List[ConversionRule]
    auxiliary_categorizations_names: typing.Optional[typing.List[str]] = None
    comment: typing.Optional[str] = None
    references: typing.Optional[str] = None
    institution: typing.Optional[str] = None
    last_update: typing.Optional[datetime.date] = None
    version: typing.Optional[str] = None

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
    _auxiliary_codes = (
        pyparsing.StringStart()
        + pyparsing.ZeroOrMore(_category_code("aux_category_code"))
        + pyparsing.StringEnd()
    )

    @classmethod
    def _parse_aux_codes(cls, aux_codes_str: str) -> typing.List[str]:
        """Parse a whitespace-separated list of auxiliary codes.

        Parameters
        ----------
        aux_codes_str: str
            Category codes separated by whitespace. Alphanumeric category codes can be
            given directly, other category codes must be quoted using double quotes.

        Returns
        -------
        aux_codes: list
            List of the category codes.

        Examples
        --------
        >>> ConversionRules._parse_aux_codes("A B")
        ['A', 'B']
        >>> ConversionRules._parse_aux_codes('"a b" c')
        ['a b', 'c']
        >>> ConversionRules._parse_aux_codes("")
        []
        >>> ConversionRules._parse_aux_codes("A + B")
        Traceback (most recent call last):
        ...
        ValueError: Could not parse: 'A + B', error: Expected ...
        """
        try:
            tokens = cls._auxiliary_codes.parseString(aux_codes_str)
        except pyparsing.ParseException as exc:
            raise ValueError(
                f"Could not parse: {aux_codes_str!r}, error: {exc.msg},"
                f" error at char {exc.loc}"
            )
        return list(tokens)

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
        >>> ConversionRules._parse_formula("A + B")
        {'A': 1, 'B': 1}
        >>> ConversionRules._parse_formula("-A+B")
        {'A': -1, 'B': 1}
        >>> ConversionRules._parse_formula('"-asdf.#" + B')
        {'-asdf.#': 1, 'B': 1}
        >>> ConversionRules._parse_formula(" A  -  B")
        {'A': 1, 'B': -1}
        >>> ConversionRules._parse_formula("-A")
        {'A': -1}
        >>> ConversionRules._parse_formula('-A+B - "A"')
        {'A': -2, 'B': 1}
        >>> ConversionRules._parse_formula("-A-")
        Traceback (most recent call last):
        ...
        ValueError: Could not parse: '-A-', error: Expected ...
        >>> ConversionRules._parse_formula("")
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
    def _from_csv(cls, fd: typing.TextIO) -> "ConversionRules":
        rules = []
        reader = csv.reader(fd, quoting=csv.QUOTE_NONE, escapechar="\\")
        header = next(reader)
        n_aux = len(header) - 2
        for i, row in enumerate(reader):
            try:
                factors_a = cls._parse_formula(row[0])
                factors_b = cls._parse_formula(row[-1])

                auxiliary_categories = {}
                for i_aux in range(n_aux):
                    categories = row[i_aux + 1]
                    if categories:
                        auxiliary_categorization: str = header[i_aux + 1]
                        auxiliary_categories[auxiliary_categorization] = set(
                            cls._parse_aux_codes(categories)
                        )

            except ValueError as err:
                raise ValueError(f"Error in line {i + 2}: {err}")

            rules.append(
                ConversionRule(
                    factors_categories_a=factors_a,
                    factors_categories_b=factors_b,
                    auxiliary_categories=auxiliary_categories,
                )
            )

        return cls(
            categorization_a_name=header[0],
            categorization_b_name=header[-1],
            rules=rules,
            auxiliary_categorizations_names=header[1 : n_aux + 1] if n_aux else None,
            comment="TODO",
            references="TODO",
            institution="TODO",
            last_update="TODO",
            version="TODO",
        )

    @classmethod
    def from_csv(
        cls, filepath: typing.Union[str, pathlib.Path, typing.TextIO]
    ) -> "ConversionRules":
        """Read conversion from comma-separated-values file."""
        if not isinstance(filepath, (str, pathlib.Path)):
            return cls._from_csv(filepath)
        fp = pathlib.Path(filepath)
        with fp.open(filepath, newline="") as fd:
            return cls._from_csv(fd)


class Conversion:
    """Rules for conversion between two categorizations."""

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
