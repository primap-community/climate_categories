"""Classes to represent conversions between categorizations."""
import csv
import dataclasses
import datetime
import pathlib
import typing
from typing import TYPE_CHECKING

import pyparsing

if TYPE_CHECKING:
    from ._categories import Categorization, Category, HierarchicalCategory


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
    csv_line_number: typing.Optional[int] = None
    csv_original_text: typing.Optional[str] = None

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
            csv_line_number=self.csv_line_number,
            csv_original_text=self.csv_original_text,
        )

    # Parsing rules for simple formulas from str
    # Supported operators at the moment are plus and minus
    _operator = pyparsing.Char("+") ^ pyparsing.Char("-")
    _operator_factors = {"+": 1, "-": -1}
    _factor_operators = {1: "+", -1: "-"}
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
        >>> ConversionRuleSpec._parse_aux_codes("A B")
        ['A', 'B']
        >>> ConversionRuleSpec._parse_aux_codes('"a b" c')
        ['a b', 'c']
        >>> ConversionRuleSpec._parse_aux_codes("")
        []
        >>> ConversionRuleSpec._parse_aux_codes("A + B")
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
        >>> ConversionRuleSpec._parse_formula("A + B")
        {'A': 1, 'B': 1}
        >>> ConversionRuleSpec._parse_formula("-A+B")
        {'A': -1, 'B': 1}
        >>> ConversionRuleSpec._parse_formula('"-asdf.#" + B')
        {'-asdf.#': 1, 'B': 1}
        >>> ConversionRuleSpec._parse_formula(" A  -  B")
        {'A': 1, 'B': -1}
        >>> ConversionRuleSpec._parse_formula("-A")
        {'A': -1}
        >>> ConversionRuleSpec._parse_formula('-A+B - "A"')
        {'A': -2, 'B': 1}
        >>> ConversionRuleSpec._parse_formula("-A-")
        Traceback (most recent call last):
        ...
        ValueError: Could not parse: '-A-', error: Expected ...
        >>> ConversionRuleSpec._parse_formula("")
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
    def from_csv_row(
        cls,
        irow: typing.Iterator[str],
        aux_names: typing.List[str],
        line_number: typing.Optional[int] = None,
    ) -> "ConversionRuleSpec":
        """Parse a ConversionRuleSpec from a row in a CSV file.

        Parameters
        ----------
        irow: iterable of str
            An iterable (e.g. list) of strings. The first string is the formula for
            the left side (categorization_a), then come the specifications for
            auxiliary categories, with as many fields as there are aux_names, then
            comes the formula for the right side (categorization_b), and finally an
            optional comment.
        aux_names: list of str
            List of names of the auxiliary categorizations.
        line_number: int, optional
            The line number within the CSV, used for nicer error messages if available.

        Returns
        -------
        self: ConversionRuleSpec
            The parsed ConverionRuleSpec.
        """

        n_aux = len(aux_names)
        row = list(irow)

        auxiliary_categories = {}
        factors_a = cls._parse_formula(row[0])
        for i in range(n_aux):
            aux_codes = cls._parse_aux_codes(row[i + 1])
            if aux_codes:
                auxiliary_categories[aux_names[i]] = set(aux_codes)
        factors_b = cls._parse_formula(row[n_aux + 1])

        try:
            comment = row[n_aux + 2]
        except IndexError:
            comment = ""

        return cls(
            factors_categories_a=factors_a,
            factors_categories_b=factors_b,
            auxiliary_categories=auxiliary_categories,
            comment=comment,
            csv_line_number=line_number,
            csv_original_text=",".join(row),
        )

    @classmethod
    def _factors_categories_formula(
        cls, factors_categories: typing.Dict[str, int]
    ) -> str:
        formula = ""
        first = True
        for category, factor in factors_categories.items():
            while factor != 0:
                if factor > 0:
                    op = "+"
                    factor -= 1
                else:
                    op = "-"
                    factor += 1

                if first:
                    if op == "+":
                        formula += cls._escape_code(category)
                    first = False
                else:
                    formula += f" {op} {cls._escape_code(category)}"
        return formula

    @staticmethod
    def _escape_code(code: str) -> str:
        """Escape a category code for serialization.

        Examples
        --------
        >>> ConversionRuleSpec._escape_code("A")
        'A'
        >>> ConversionRuleSpec._escape_code("2.A")
        '2.A'
        >>> ConversionRuleSpec._escape_code("$1")
        '"$1"'
        >>> ConversionRuleSpec._escape_code('"')
        '"\\\\""'
        """
        if code.isalnum() or code.replace(".", "").isalnum():
            return code
        # replace:
        # \ -> \\
        # " -> \"
        esc = code.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{esc}"'

    def to_csv_row(self) -> typing.List[str]:
        """Return a representation of this rule suitable for writing to a CSV file."""
        row = [self._factors_categories_formula(self.factors_categories_a)]
        for aux_categories in self.auxiliary_categories.values():
            row.append(" ".join(map(self._escape_code, aux_categories)))
        row.append(self._factors_categories_formula(self.factors_categories_b))
        row.append(self.comment)
        return row

    def __str__(self) -> str:
        if self.csv_original_text is not None:
            return self.csv_original_text
        return ",".join(self.to_csv_row())


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
    csv_line_number: typing.Optional[int] = None
    csv_original_text: typing.Optional[str] = None
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
                f"{aux_categorization} in {[c.codes[0] for c in sorted(categories)]}"
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
            csv_line_number=self.csv_line_number,
            csv_original_text=self.csv_original_text,
        )

    def __str__(self):
        return str(self.to_spec())

    def format_with_lineno(self) -> str:
        """Human-readable string representation of the rule with information in which
        line in the CSV file it was defined, if that is available."""
        s = f"<Rule '{self!s}'"
        if self.csv_line_number is not None:
            s += f" from line {self.csv_line_number}"
        s += ">"
        return s


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
        for row in reader:
            irow = iter(row)
            try:
                rule_specs.append(
                    ConversionRuleSpec.from_csv_row(
                        irow, aux_names=aux_names, line_number=reader.line_num
                    )
                )
            except ValueError as err:
                raise ValueError(f"Error in line {reader.line_num}: {err}")

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


@dataclasses.dataclass(frozen=True)
class OvercountingProblem:
    """A suspected overcounting problem."""

    category: "HierarchicalCategory"
    ancestral_sets_projected: typing.List[typing.Set["HierarchicalCategory"]]
    rules: typing.List[ConversionRule]

    def __str__(self):
        hull: typing.Set["HierarchicalCategory"] = set().union(
            *self.ancestral_sets_projected
        )
        leaves = []
        for category in hull:
            if not category.children:
                leaves.append(category)
            else:
                children = set().union(*category.children)
                if all(child not in hull for child in children):
                    leaves.append(category)

        involved_rules_str = ", ".join(
            (rule.format_with_lineno() for rule in self.rules)
        )
        return (
            f"{self.category!r} is possibly counted multiple times"
            f"\ninvolved mapped categories: {leaves!r} (showing lowest level only)"
            f"\ninvolved rules: {involved_rules_str}."
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

    def find_over_counting_problems(self) -> typing.List[OvercountingProblem]:
        """Check if any category from one side is counted more than once on the
        other side.

        Note that the algorithm at the moment can't reliably detect all over counting
        problems and also some suspected problems might be fine under closer
        examination, so use this function only to generate hints for possible problems.

        Returns
        -------
        problems: list of OvercountingProblem objects
            All detected suspected problems.
        """
        # TODO: properly find B problems.
        # TODO: probably easiest by implementing a "reversed" function.
        for categorization in self.categorization_a, self.categorization_b:
            if not categorization.hierarchical:
                raise ValueError(
                    f"{categorization} is not hierarchical, without "
                    f"a hierarchy, overcounting can not be evaluated."
                )
            if not categorization.total_sum:
                raise ValueError(
                    f"For {categorization} it is not specified that the"
                    f"sum of a set of children equals the parent, so"
                    f"overcounting can not be evaluated."
                )

        problems = []
        for categorization in self.categorization_a, self.categorization_b:
            for category in categorization.values():
                prob = self._check_overcounting_category(category)
                if prob:
                    problems.append(prob)

        return problems

    def _check_overcounting_category(
        self, category: "HierarchicalCategory"
    ) -> typing.Optional[OvercountingProblem]:
        # TODO ALGO idea:
        # A(c) sei die Abstammungslinie einer Kategorie c, also die Menge aller
        # Vorfahren plus der Kategorie selbst.
        # P(A(c)) sei die Projektion von der Abstammungslinie von c (in die andere
        # Kategorisierung)
        # AA(P(A(c))) sei die Menge aller Abstammungslinien der Elemente von P(A(c))
        # Dann muss das größte Element in AA gleich sein mit der Vereinigung aller
        # Elemente von AA.

        # The set of all ancestors of the category plus the category itself
        ancestral_set = {category}
        ancestral_set.update(category.ancestors)

        # The projection of the ancestral set into the other categorization
        projected_ancestral_set: typing.Set["HierarchicalCategory"] = set()
        relevant_rules = []
        for rule in self.rules:
            # for now, skip rules which are valid only for some aux categories
            if rule.auxiliary_categories:
                continue
            # for now, only use simple summation factors
            categories_a: typing.Set["HierarchicalCategory"] = {
                cat for cat, factor in rule.factors_categories_a.items() if factor == 1
            }
            categories_b: typing.Set["HierarchicalCategory"] = {
                cat for cat, factor in rule.factors_categories_b.items() if factor == 1
            }
            if categories_a.intersection(ancestral_set):
                projected_ancestral_set.update(categories_b)
                relevant_rules.append(rule)

        # The ancestral sets of the projected categories
        ancestral_sets_projected = []
        for c in projected_ancestral_set:
            ancestral_set_projected = {c}
            ancestral_set_projected.update(c.ancestors)
            ancestral_sets_projected.append(ancestral_set_projected)

        if not ancestral_sets_projected:
            return

        # Now, the union of the projected ancestral sets (the hull) must be identical to
        # the
        # largest projected ancestral sets, otherwise there is a branching in the
        # projection, i.e. different leave nodes are included in the projected
        # ancestral set, which means we have overcounting.
        hull = set().union(*ancestral_sets_projected)
        largest = max(ancestral_sets_projected, key=len)
        if hull != largest:
            return OvercountingProblem(
                category=category,
                ancestral_sets_projected=ancestral_sets_projected,
                rules=relevant_rules,
            )

    def __eq__(self, other):
        return (
            isinstance(other, Conversion)
            and self.categorization_a == other.categorization_a
            and self.categorization_b == other.categorization_b
            and self.rules == other.rules
        )
