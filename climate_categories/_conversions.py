"""Classes to represent conversions between categorizations."""
import csv
import dataclasses
import datetime
import pathlib
import typing
from typing import TYPE_CHECKING

import pyparsing

if TYPE_CHECKING:
    from ._categories import Categorization, Category


@dataclasses.dataclass(frozen=True)
class ConversionRuleSpec:
    """Specification of a rule to convert between categories from two different
     categorizations.

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
    comment : str
        A human-readable comment explaining the rule or adding additional information.
    """

    factors_categories_a: typing.Dict[str, int]
    factors_categories_b: typing.Dict[str, int]
    auxiliary_categories: typing.Dict[str, typing.Set[str]]
    comment: str = ""

    def hydrate(
        self,
        categorization_a: "Categorization",
        categorization_b: "Categorization",
        cats: typing.Dict[str, "Categorization"],
    ) -> "ConversionRule":
        """Convert this specification into a ConversionRule object with full
        functionality."""

        auxiliary_categories_hydrated = {}
        for aux_categorization_name, categories in self.auxiliary_categories.items():
            aux_categorization = cats[aux_categorization_name]
            auxiliary_categories_hydrated[aux_categorization] = {
                aux_categorization[code] for code in categories
            }

        return ConversionRule(
            factors_categories_a={
                categorization_a[code]: factor
                for code, factor in self.factors_categories_a.items()
            },
            factors_categories_b={
                categorization_b[code]: factor
                for code, factor in self.factors_categories_b.items()
            },
            auxiliary_categories=auxiliary_categories_hydrated,
            comment=self.comment,
        )


@dataclasses.dataclass(frozen=True)
class ConversionRule:
    """A rule to convert between categories from two different categorizations.

    Supports one-to-one relationships, one-to-many relationships in both directions and
    many-to-many relationships. For each category, a factor is given which can also be
    negative to model relationships like A = B - C.

    Using auxiliary_categories, a rule can be restricted to specific auxiliary
    categories only.

    Attributes
    ----------
    factors_categories_a : dict mapping categories to factors
        Map of categories from the first categorization to factors. For a simple
        addition, use factor 1, to subtract the category, use factor -1.
    factors_categories_b : dict mapping categories to factors
        Map of categories from the second categorization to factors. For a simple
        addition, use factor 1, to subtract the category, use factor -1.
    auxiliary_categories : dict[Categorization, set[Category]]
        Map of auxiliary categorizations to sets of auxiliary categories. Not
        all auxiliary categorizations need to be specified, and if an auxiliary
        categorization is not specified (or an empty set of category codes is given),
        the validity of the rule is not restricted.
        If an auxiliary categorization is specified and categories are given, the
        rule is only valid for the given categories. If multiple auxiliary
        categorizations are given, the rule is only valid if all auxiliary
        categorizations match.
    comment : str
        A human-readable comment explaining the rule or adding additional information.
    cardinality_a : str
        The cardinality of the rule on side a. Is "one" if there is exactly one category
        in factors_categories_a, and "many" otherwise.
    cardinality_b : str
        The cardinality of the rule on side b. Is "one" if there is exactly one category
        in factors_categories_b, and "many" otherwise.
    """

    factors_categories_a: typing.Dict["Category", int]
    factors_categories_b: typing.Dict["Category", int]
    auxiliary_categories: typing.Dict["Categorization", typing.Set["Category"]]
    comment: str = ""
    cardinality_a: str = dataclasses.field(init=False)
    cardinality_b: str = dataclasses.field(init=False)

    def __post_init__(self):
        # Have to use object.__setattr__ because the class is frozen. This is fine
        # because we are in __post_init__, so we operate on a not-yet-finished object
        object.__setattr__(
            self,
            "cardinality_a",
            "one" if len(self.factors_categories_a) == 1 else "many",
        )
        object.__setattr__(
            self,
            "cardinality_b",
            "one" if len(self.factors_categories_b) == 1 else "many",
        )
        # Clean up auxiliary categories: empty specs have the same meaning as no spec
        for key, val in self.auxiliary_categories.items():
            if not val:
                del self.auxiliary_categories[key]

    def format_human_readable(self) -> str:
        """Format the rule for humans."""
        if self.auxiliary_categories:
            aux_info = [
                f"{aux_categorization} in {categories}"
                for aux_categorization, categories in self.auxiliary_categories.items()
            ]
            r = "Only for " + " and ".join(aux_info) + "\n"
        else:
            r = ""

        r += "\n".join(
            (f"{cat.categorization.name} {cat}" for cat in self.factors_categories_a)
        )
        r += "\n"
        r += (
            "\n".join(
                (
                    f"{cat.categorization.name} {cat}"
                    for cat in self.factors_categories_b
                )
            )
            + "\n"
        )

        if self.comment:
            r += f"# Comment: {self.comment!r}\n"

        return r

    def to_spec(self) -> ConversionRuleSpec:
        """Return a serializable specification.

        Returns
        -------
        spec: ConversionRuleSpec
        """
        return ConversionRuleSpec(
            factors_categories_a={
                category.codes[0]: factor
                for category, factor in self.factors_categories_a.items()
            },
            factors_categories_b={
                category.codes[0]: factor
                for category, factor in self.factors_categories_b.items()
            },
            auxiliary_categories={
                categorization.name: {category.codes[0] for category in categories}
                for categorization, categories in self.auxiliary_categories.items()
            },
            comment=self.comment,
        )


class ConversionSpec:
    """Specification of rules for conversion between two categorizations, with support
    for alternative rules depending on auxiliary categorizations.

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
    rule_specs : list of ConversionRuleSpec
        The rule specifications for conversion between individual categories or sets of
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

    _meta_data_keys = ["comment", "references", "institution", "last_update", "version"]
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

    def __init__(
        self,
        *,
        categorization_a_name: str,
        categorization_b_name: str,
        rule_specs: typing.List[ConversionRuleSpec],
        auxiliary_categorizations_names: typing.Optional[typing.List[str]] = None,
        comment: typing.Optional[str] = None,
        references: typing.Optional[str] = None,
        institution: typing.Optional[str] = None,
        last_update: typing.Optional[datetime.date] = None,
        version: typing.Optional[str] = None,
    ):
        self.categorization_a_name = categorization_a_name
        self.categorization_b_name = categorization_b_name
        self.rule_specs = rule_specs
        self.auxiliary_categorizations_names = auxiliary_categorizations_names
        self.comment = comment
        self.references = references
        self.institution = institution
        self.last_update = last_update
        self.version = version

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
        >>> ConversionSpec._parse_aux_codes("A B")
        ['A', 'B']
        >>> ConversionSpec._parse_aux_codes('"a b" c')
        ['a b', 'c']
        >>> ConversionSpec._parse_aux_codes("")
        []
        >>> ConversionSpec._parse_aux_codes("A + B")
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
        >>> ConversionSpec._parse_formula("A + B")
        {'A': 1, 'B': 1}
        >>> ConversionSpec._parse_formula("-A+B")
        {'A': -1, 'B': 1}
        >>> ConversionSpec._parse_formula('"-asdf.#" + B')
        {'-asdf.#': 1, 'B': 1}
        >>> ConversionSpec._parse_formula(" A  -  B")
        {'A': 1, 'B': -1}
        >>> ConversionSpec._parse_formula("-A")
        {'A': -1}
        >>> ConversionSpec._parse_formula('-A+B - "A"')
        {'A': -2, 'B': 1}
        >>> ConversionSpec._parse_formula("-A-")
        Traceback (most recent call last):
        ...
        ValueError: Could not parse: '-A-', error: Expected ...
        >>> ConversionSpec._parse_formula("")
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
    def _read_csv_meta(cls, reader: csv.reader) -> typing.Dict[str, str]:
        """Read the metadata section of a CSV conversion specification file. It consists
        of key, value pairs, one pair on each line. A single empty line terminates the
        metadata section.

        Parameters
        ----------
        reader: a CSV reader object as returned by csv.reader
            Use a CSV reader object which was not used before to read from. The reader
            object will be iterated up to the end of the meta data section, so that
            after calling _read_csv_meta you can directly start reading the data
            section.

        Returns
        -------
        meta_data: dict
            lineno Mapping of meta data keys to values.
        """
        meta_data = {}
        for row in reader:
            if not row:
                break
            if len(row) < 2:
                raise ValueError(
                    f"Meta data specification is incomplete in line {reader.line_num}:"
                    f" {row!r}."
                )
            if len(row) > 2:
                raise ValueError(
                    f"Meta data specification has extraneous fields in line"
                    f" {reader.line_num}:"
                    f" {row!r}, did you forget to escape a comma?"
                )
            if row[0] not in cls._meta_data_keys:
                raise ValueError(
                    f"Unknown meta data key in line {reader.line_num}: {row[0]}."
                )

            meta_data[row[0]] = row[1]

        if "last_update" in meta_data:
            meta_data["last_update"] = datetime.date.fromisoformat(
                meta_data["last_update"]
            )
        return meta_data

    @classmethod
    def _read_csv_rules(
        cls, reader: csv.reader
    ) -> typing.Tuple[str, str, typing.List[str], typing.List[ConversionRuleSpec]]:
        """Read the data section of a CSV specification file. It consists of a header,
        followed by rules, with each rule on one line.

        Parameters
        ----------
        reader: CSV reader object as returned by csv.reader
            The reader object must already be advanced to the rules section, so that
            the first read yields the data header.

        Returns
        -------
        a_name, b_name, aux_names, rule_specs: str, str, list, list
           The name of categorizations A and B, the names of the auxiliary categories,
           and the parsed rules.
        """
        rule_specs = []
        header = next(reader)
        a_name = header[0]
        b_name = header[-2]
        if header[-1] != "comment":
            raise ValueError("Last column must be 'comment', but isn't.")
        aux_names = header[1:-2]
        n_aux = len(aux_names)
        for row in reader:
            irow = iter(row)
            auxiliary_categories = {}
            try:
                factors_a = cls._parse_formula(next(irow))
                for i in range(n_aux):
                    aux_codes = cls._parse_aux_codes(next(irow))
                    if aux_codes:
                        auxiliary_categories[aux_names[i]] = set(aux_codes)
                factors_b = cls._parse_formula(next(irow))
            except ValueError as err:
                raise ValueError(f"Error in line {reader.line_num}: {err}")

            try:
                comment = next(irow)
            except StopIteration:
                comment = ""

            rule_specs.append(
                ConversionRuleSpec(
                    factors_categories_a=factors_a,
                    factors_categories_b=factors_b,
                    auxiliary_categories=auxiliary_categories,
                    comment=comment,
                )
            )

        return a_name, b_name, aux_names, rule_specs

    @classmethod
    def _from_csv(cls, fd: typing.TextIO) -> "ConversionSpec":
        reader = csv.reader(fd, quoting=csv.QUOTE_NONE, escapechar="\\")

        meta_data = cls._read_csv_meta(reader)
        a_name, b_name, aux_names, rule_specs = cls._read_csv_rules(reader)

        return cls(
            categorization_a_name=a_name,
            categorization_b_name=b_name,
            rule_specs=rule_specs,
            auxiliary_categorizations_names=aux_names or None,
            **meta_data,
        )

    @classmethod
    def from_csv(
        cls,
        filepath: typing.Union[str, pathlib.Path, typing.TextIO, typing.Iterable[str]],
    ) -> "ConversionSpec":
        """Read conversion from comma-separated-values file."""
        if not isinstance(filepath, (str, pathlib.Path)):
            return cls._from_csv(filepath)
        fp = pathlib.Path(filepath)
        with fp.open(newline="") as fd:
            return cls._from_csv(fd)

    def __repr__(self):
        return (
            f"<ConversionSpec {self.categorization_a_name!r} <->"
            f" {self.categorization_b_name!r} with {len(self.rule_specs)} rules>"
        )

    def hydrate(
        self,
        cats: typing.Dict[str, "Categorization"],
    ) -> "Conversion":
        """Convert this Specification into a Conversion object with full
        functionality."""
        categorization_a = cats[self.categorization_a_name]
        categorization_b = cats[self.categorization_b_name]
        auxiliary_categorizations = (
            [cats[x] for x in self.auxiliary_categorizations_names]
            if self.auxiliary_categorizations_names
            else None
        )
        return Conversion(
            categorization_a=categorization_a,
            categorization_b=categorization_b,
            rules=[
                rule_spec.hydrate(
                    categorization_a=categorization_a,
                    categorization_b=categorization_b,
                    cats=cats,
                )
                for rule_spec in self.rule_specs
            ],
            auxiliary_categorizations=auxiliary_categorizations,
            comment=self.comment,
            references=self.references,
            institution=self.institution,
            last_update=self.last_update,
            version=self.version,
        )


class Conversion(ConversionSpec):
    """Conversion between two categorizations.

    This class collects functionality which needs access to the actual categorizations
    and categories.

    Attributes
    ----------
    categorization_a : Categorization
        The first categorization.
    categorization_b : Categorization
        The second categorization.
    auxiliary_categorizations : list of Categorization, optional
        The auxiliary categorizations, if any.
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

    def __init__(
        self,
        *,
        categorization_a: "Categorization",
        categorization_b: "Categorization",
        rules: typing.List[ConversionRule],
        auxiliary_categorizations: typing.Optional[
            typing.List["Categorization"]
        ] = None,
        comment: typing.Optional[str] = None,
        references: typing.Optional[str] = None,
        institution: typing.Optional[str] = None,
        last_update: typing.Optional[datetime.date] = None,
        version: typing.Optional[str] = None,
    ):
        ConversionSpec.__init__(
            self,
            categorization_a_name=categorization_a.name,
            categorization_b_name=categorization_b.name,
            rule_specs=[rule.to_spec() for rule in rules],
            auxiliary_categorizations_names=[x.name for x in auxiliary_categorizations]
            if auxiliary_categorizations
            else None,
            comment=comment,
            references=references,
            institution=institution,
            last_update=last_update,
            version=version,
        )
        self.categorization_a = categorization_a
        self.categorization_b = categorization_b
        self.rules = rules
        self.auxiliary_categorizations = auxiliary_categorizations

    def ensure_valid(self, cats: typing.Dict[str, "Categorization"]) -> None:
        """Check if all used codes are contained in the categorizations."""
        # TODO

    def describe_detailed(self) -> str:
        """Detailed human-readable description of the conversion rules."""
        one_to_one = []
        one_to_many = []
        many_to_one = []
        many_to_many = []
        cats_a = set()
        cats_b = set()
        for rule in self.rules:
            cats_a.update(rule.factors_categories_a.keys())
            cats_b.update(rule.factors_categories_b.keys())
            if rule.cardinality_a == "one" and rule.cardinality_b == "one":
                one_to_one.append(rule)
            elif rule.cardinality_a == "one":
                one_to_many.append(rule)
            elif rule.cardinality_b == "one":
                many_to_one.append(rule)
            else:
                many_to_many.append(rule)

        cat_a, cat_b = self.categorization_a.name, self.categorization_b.name

        r = f"# Mapping between {cat_a} and {cat_b}\n\n"
        r += "## Simple direct mappings\n\n"
        r += "\n".join(rule.format_human_readable() for rule in one_to_one)
        r += "\n\n"
        r += f"## One-to-many mappings - one {cat_a} to many {cat_b}\n\n"
        r += "\n".join((rule.format_human_readable()) for rule in one_to_many)
        r += "\n\n"
        r += f"## Many-to-one mappings - many {cat_a} to one {cat_b}\n\n"
        r += "\n".join((rule.format_human_readable()) for rule in many_to_one)
        r += "\n\n"
        r += f"## Many-to-many mappings - many {cat_a} to many {cat_b}\n\n"
        r += "\n".join((rule.format_human_readable()) for rule in many_to_many)
        r += "\n\n"

        r += "## Unmapped categories\n\n"
        cats_missing_a = set(self.categorization_a.values()) - cats_a
        cats_missing_b = set(self.categorization_b.values()) - cats_b
        r += f"### {cat_a}\n"
        r += "\n".join(sorted((str(x) for x in cats_missing_a))) + "\n\n"
        r += f"### {cat_b}\n"
        r += "\n".join(sorted((str(x) for x in cats_missing_b))) + "\n\n"

        return r
