"""Classes to represent conversions between categorizations."""
import csv
import dataclasses
import datetime
import pathlib
import typing
from typing import TYPE_CHECKING

import immutables
import pyparsing
import strictyaml as sy

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

    factors_categories_a: dict[str, int]
    factors_categories_b: dict[str, int]
    auxiliary_categories: dict[str, set[str]]
    comment: str = ""
    csv_line_number: typing.Optional[int] = None
    csv_original_text: typing.Optional[str] = None

    def hydrate(
        self,
        categorization_a: "Categorization",
        categorization_b: "Categorization",
        cats: dict[str, "Categorization"],
    ) -> "ConversionRule":
        """Convert this specification into a ConversionRule object with full
        functionality."""

        auxiliary_categories_hydrated = {}
        for aux_categorization_name, categories in self.auxiliary_categories.items():
            aux_categorization = cats[aux_categorization_name]
            auxiliary_categories_hydrated[
                aux_categorization
            ] = self._hydrate_handle_errors(categories, aux_categorization)

        return ConversionRule(
            factors_categories_a=self._hydrate_handle_errors(
                self.factors_categories_a, categorization_a
            ),
            factors_categories_b=self._hydrate_handle_errors(
                self.factors_categories_b, categorization_b
            ),
            auxiliary_categories=auxiliary_categories_hydrated,
            comment=self.comment,
            csv_line_number=self.csv_line_number,
            csv_original_text=self.csv_original_text,
        )

    @typing.overload
    def _hydrate_handle_errors(
        self, to_hydrate: dict[str, int], categorization: "Categorization"
    ) -> dict["Category", int]:
        ...

    @typing.overload
    def _hydrate_handle_errors(
        self, to_hydrate: set[str], categorization: "Categorization"
    ) -> set["Category"]:
        ...

    def _hydrate_handle_errors(
        self,
        to_hydrate: typing.Union[dict[str, int], set[str]],
        categorization: "Categorization",
    ) -> typing.Union[dict["Category", int], set["Category"]]:
        """Hydrate a dict/set while nicely handling errors."""
        try:
            if isinstance(to_hydrate, dict):
                return {
                    categorization[code]: factor for code, factor in to_hydrate.items()
                }
            else:
                return {categorization[code] for code in to_hydrate}
        except KeyError as err:
            code = err.args[0]
            raise ValueError(
                f"Error in line {self.csv_line_number}: {code!r} not in"
                f" {categorization}."
            ) from None

    # Parsing rules for simple formulas from str
    # Supported operators at the moment are plus and minus
    _operator = pyparsing.Char("+") ^ pyparsing.Char("-")
    _operator_factors = immutables.Map({"+": 1, "-": -1})
    _factor_operators = immutables.Map({1: "+", -1: "-"})
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
    def _parse_aux_codes(cls, aux_codes_str: str) -> list[str]:
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
            ) from None
        return list(tokens)

    @classmethod
    def _parse_formula(cls, formula: str) -> dict[str, int]:
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
            ) from None
        # first operator is implicitly a plus, have to handle it specially
        if "unary_op" in tokens:
            op = tokens.pop(0)
        else:
            op = "+"
        code = tokens.pop(0)
        code_factors = {code: cls._operator_factors[op]}
        while len(tokens):
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
        aux_names: list[str],
        line_number: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
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
    def _factors_categories_formula(cls, factors_categories: dict[str, int]) -> str:
        """Serialize a dict mapping categories to factors to a formula string.

        Parameters
        ----------
        factors_categories: dict
            Mapping of categories to factors.

        Returns
        -------
        formula: str
            String representation of the input.
        """
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

    def to_csv_row(self) -> list[str]:
        """Return a representation of this rule suitable for writing to a CSV file."""
        row = [self._factors_categories_formula(self.factors_categories_a)]
        for aux_categories in self.auxiliary_categories.values():
            row.append(" ".join(sorted(map(self._escape_code, aux_categories))))
        row.extend(
            (
                self._factors_categories_formula(self.factors_categories_b),
                self.comment,
            )
        )
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
    is_restricted : bool
        The rule is restricted if and only if for at least one auxiliary categorization
        at least one category is specified, so that the rule is only valid for a
        subset of cases. Otherwise, the rule is unrestricted and valid for all
        cases.
    """

    factors_categories_a: dict["Category", int]
    factors_categories_b: dict["Category", int]
    auxiliary_categories: dict["Categorization", set["Category"]]
    comment: str = ""
    csv_line_number: typing.Optional[int] = None
    csv_original_text: typing.Optional[str] = None
    cardinality_a: str = dataclasses.field(init=False)
    cardinality_b: str = dataclasses.field(init=False)
    is_restricted: bool = dataclasses.field(init=False)

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
        object.__setattr__(
            self, "is_restricted", any(self.auxiliary_categories.values())
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConversionRule):
            return NotImplemented
        return (
            self.factors_categories_a == other.factors_categories_a
            and self.factors_categories_b == other.factors_categories_b
            and self.auxiliary_categories == other.auxiliary_categories
            and self.comment == other.comment
        )

    def reversed(self) -> "ConversionRule":
        """Return the ConversionRule with categorization_a and categorization_b
        swapped."""
        return ConversionRule(
            factors_categories_a=self.factors_categories_b,
            factors_categories_b=self.factors_categories_a,
            auxiliary_categories=self.auxiliary_categories,
            comment=self.comment,
            csv_line_number=self.csv_line_number,
            csv_original_text=self.csv_original_text,
        )

    @staticmethod
    def _format_factor_category_human_readable(
        factor: int, category: "Category"
    ) -> str:
        """Format a single category and its factor for humans."""
        if factor == 1:
            return f"{category.categorization.name} {category}"
        else:
            return f"{factor} * {category.categorization.name} {category}"

    def format_human_readable(self, categorization_separator: str = "⮁\n") -> str:
        """Format the rule for humans.

        Parameters
        ----------
        categorization_separator: str, optional
            The categorization_separator is printed between the categories from
            the source categorization and the categories from the target categorization
            to make the difference clear.

        Returns
        -------
        human_readable: str
            The rule in a format optimized for error-free parsing by humans.
        """
        if any(self.auxiliary_categories.values()):
            aux_info = [
                f"{aux_categorization} in {[c.codes[0] for c in sorted(categories)]}"
                for aux_categorization, categories in self.auxiliary_categories.items()
            ]
            r = "Only for " + " and ".join(aux_info) + "\n"
        else:
            r = ""

        r += "\n".join(
            self._format_factor_category_human_readable(f, cat)
            for cat, f in self.factors_categories_a.items()
        )
        r += "\n"
        r += categorization_separator
        r += "\n".join(
            self._format_factor_category_human_readable(f, cat)
            for cat, f in self.factors_categories_b.items()
        )
        r += "\n"

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


class ConversionBase:
    """Common base of ConversionSpec and Conversion.

    Mainly used to hold a single definition of the metadata attributes

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

    def __init__(
        self,
        *,
        categorization_a_name: str,
        categorization_b_name: str,
        rule_specs: list[ConversionRuleSpec],
        auxiliary_categorizations_names: typing.Optional[list[str]] = None,
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


class ConversionSpec(ConversionBase):
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

    _strictyaml_metadata_schema = sy.Map(
        {
            sy.Optional("comment"): sy.Str(),
            sy.Optional("references"): sy.Str(),
            sy.Optional("institution"): sy.Str(),
            sy.Optional("last_update"): sy.Datetime(),
            sy.Optional("version"): sy.Str(),
        }
    )

    def __init__(
        self,
        *,
        categorization_a_name: str,
        categorization_b_name: str,
        rule_specs: list[ConversionRuleSpec],
        auxiliary_categorizations_names: typing.Optional[list[str]] = None,
        comment: typing.Optional[str] = None,
        references: typing.Optional[str] = None,
        institution: typing.Optional[str] = None,
        last_update: typing.Optional[datetime.date] = None,
        version: typing.Optional[str] = None,
    ):
        ConversionBase.__init__(
            self,
            categorization_a_name=categorization_a_name,
            categorization_b_name=categorization_b_name,
            rule_specs=rule_specs,
            auxiliary_categorizations_names=auxiliary_categorizations_names,
            comment=comment,
            references=references,
            institution=institution,
            last_update=last_update,
            version=version,
        )

    @classmethod
    def _read_csv_meta(cls, fd: typing.TextIO):
        """Read the metadata section of a CSV conversion specification file. It consists
        of YAML key, value pairs, one pair on each line separated by a colon.
        Each line is prefixed with the comment char "#".

        Parameters
        ----------
        fd: a CSV file object
            Use a file object which was not used before to read from.
            The file object will be iterated up to the end of the meta data
            section, so that after calling _read_csv_meta you can directly
            start reading the data section.

        Returns
        -------
        meta_data: dict
            Mapping of meta data keys to values.
        linecount: int
            Count of lines of the metadata block
        """
        yaml_header = ""
        last_pos = fd.tell()
        line = fd.readline()
        while line.startswith("#"):
            # remove leading comment and whitespace
            yaml_header += line[1:].lstrip()
            last_pos = fd.tell()
            line = fd.readline()
        fd.seek(last_pos)
        meta_data = sy.load(yaml_header, schema=cls._strictyaml_metadata_schema).data

        return meta_data, yaml_header.count("\n")

    @classmethod
    def _read_csv_rules(
        cls, reader: csv.reader, offset: int
    ) -> tuple[str, str, list[str], list[ConversionRuleSpec]]:
        """Read the data section of a CSV specification file. It consists of a header,
        followed by rules, with each rule on one line.

        Parameters
        ----------
        reader: CSV reader object as returned by csv.reader
            The reader object must already be advanced to the rules section, so that
            the first read yields the data header.
        offset: int
            Number of lines of the metadata block.

        Returns
        -------
        a_name, b_name, aux_names, rule_specs: str, str, list, list
           The name of categorizations A and B, the names of the auxiliary categories,
           and the parsed rules.
        """
        rule_specs = []
        header: list[str] = next(reader)
        a_name = header[0]
        b_name = header[-2]
        if header[-1] != "comment":
            raise ValueError("Last column must be 'comment', but isn't.")
        aux_names = header[1:-2]
        for row in reader:
            line_num = reader.line_num + offset
            irow = iter(row)
            try:
                rule_specs.append(
                    ConversionRuleSpec.from_csv_row(
                        irow, aux_names=aux_names, line_number=line_num
                    )
                )
            except ValueError as err:
                raise ValueError(f"Error in line {line_num}: {err}") from None

        return a_name, b_name, aux_names, rule_specs

    @classmethod
    def _from_csv(
        cls,
        fd: typing.TextIO,
    ) -> "ConversionSpec":
        meta_data, len_meta_data = cls._read_csv_meta(fd)
        reader = csv.reader(fd, quoting=csv.QUOTE_NONE, escapechar="\\")
        a_name, b_name, aux_names, rule_specs = cls._read_csv_rules(
            reader, len_meta_data
        )

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
        filepath: typing.Union[str, pathlib.Path, typing.TextIO],
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
        cats: dict[str, "Categorization"],
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
class OverCountingProblem:
    """A suspected over counting problem."""

    category: "HierarchicalCategory"
    leave_node_groups: list[set["HierarchicalCategory"]]
    rules: list[ConversionRule]

    def __str__(self):
        involved_rules_str = ", ".join(rule.format_with_lineno() for rule in self.rules)
        sorted_leave_node_groups = [sorted(g) for g in self.leave_node_groups]
        return (
            f"{self.category!r} is possibly counted multiple times"
            f"\ninvolved leave groups categories: {sorted_leave_node_groups!r}"
            f"\ninvolved rules: {involved_rules_str}."
        )


class Conversion(ConversionBase):
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
        rules: list[ConversionRule],
        auxiliary_categorizations: typing.Optional[list["Categorization"]] = None,
        comment: typing.Optional[str] = None,
        references: typing.Optional[str] = None,
        institution: typing.Optional[str] = None,
        last_update: typing.Optional[datetime.date] = None,
        version: typing.Optional[str] = None,
    ):
        ConversionBase.__init__(
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

    def reversed(self) -> "Conversion":
        """Returns the Conversion with categorization_a and categorization_b swapped."""
        return Conversion(
            categorization_a=self.categorization_b,
            categorization_b=self.categorization_a,
            rules=[rule.reversed() for rule in self.rules],
            auxiliary_categorizations=self.auxiliary_categorizations,
            comment=self.comment,
            references=self.references,
            institution=self.institution,
            last_update=self.last_update,
            version=self.version,
        )

    def __repr__(self):
        return (
            f"<Conversion {self.categorization_a_name!r} <->"
            f" {self.categorization_b_name!r} with {len(self.rule_specs)} rules>"
        )

    def describe_detailed(self) -> str:
        """Detailed human-readable description of the conversion rules.

        Sections are added for direct one-to-one mappings, one-to-many mappings,
        many-to-one mappings, and many-to-many mappings, respectively.

        Factors are shown at the start of the line if they don't equal 1, like this:
        -1 * IPCC1996 4 Agriculture
        to indicate that category 4 should be subtracted.
        """
        one_to_one = []
        one_to_many = []
        many_to_one = []
        many_to_many = []
        cats_a: set["Category"] = set()
        cats_b: set["Category"] = set()
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
        r += "\n".join(
            rule.format_human_readable(categorization_separator="")
            for rule in one_to_one
        )
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
        r += "\n".join(sorted(str(x) for x in cats_missing_a)) + "\n\n"
        r += f"### {cat_b}\n"
        r += "\n".join(sorted(str(x) for x in cats_missing_b)) + "\n\n"

        return r

    def find_unmapped_categories(
        self,
    ) -> tuple[set["Category"], set["Category"]]:
        """Find categories for which no rule exists to map them.

        Returns
        -------
        missing_categories_a, missing_categories_b: set, set
            A list of categories missing from categorization_a and categorization_b,
            respectively.
        """
        cats_a: set["Category"] = set()
        cats_b: set["Category"] = set()
        for rule in self.rules:
            cats_a.update(rule.factors_categories_a.keys())
            cats_b.update(rule.factors_categories_b.keys())

        cats_missing_a = set(self.categorization_a.values()) - cats_a
        cats_missing_b = set(self.categorization_b.values()) - cats_b
        return cats_missing_a, cats_missing_b

    def find_over_counting_problems(self) -> list[OverCountingProblem]:
        """Check if any category from one side is counted more than once on the
        other side.

        Note that the algorithm at the moment can't reliably detect all over counting
        problems and also some suspected problems might be fine under closer
        examination, so use this function only to generate hints for possible problems.

        Returns
        -------
        problems: list of OverCountingProblem objects
            All detected suspected problems.
        """
        for categorization in self.categorization_a, self.categorization_b:
            if not categorization.hierarchical:
                raise ValueError(
                    f"{categorization} is not hierarchical, without "
                    f"a hierarchy, over counting can not be evaluated."
                )
            if not categorization.total_sum:  # type: ignore
                raise ValueError(
                    f"For {categorization} it is not specified that the "
                    f"sum of a set of children equals the parent, so "
                    f"over counting can not be evaluated."
                )

        problems = []
        for categorization in self.categorization_a, self.categorization_b:
            # used to cache costly descendant evaluation
            descendants: dict[str, set[str]] = {}
            for category in categorization.values():
                prob = self._check_over_counting_category(
                    category, categorization, descendants  # type: ignore
                )
                if prob:
                    problems.append(prob)

        return problems

    @staticmethod
    def _leave_node_group(
        categories: typing.Iterable["HierarchicalCategory"],
        hull: set[str],
        descendants: dict[str, set[str]],
    ) -> bool:
        """Are all of the given categories leave nodes of the given hull?

        Parameters
        ----------
        categories: list of HierarchicalCategory objects
            Categories that will be checked. If any of the categories has descendants
            outside of the hull, the function will return False.
        hull: set of strings
            Set of primary codes of HierarchicalCategories, which define the hull
            that will be used to check the categories.
        descendants: dict[str, list[str]]
            Mapping of primary codes of parent HierarchicalCategories to the codes
            of their descendants. Will be filled with additional mappings if they are
            computed. Re-use the dictionary for better performance.

        Returns
        -------
        all_leave: bool
            If all categories are leave categories within the given hull, returns True.
            Otherwise, returns false.
        """
        for c in categories:
            # Use cached descendants information if it is available, compute and cache
            # it otherwise
            try:
                desc = descendants[c.codes[0]]
            except KeyError:
                desc = {d.codes[0] for d in c.descendants}
                descendants[c.codes[0]] = desc

            for d in desc:
                if d in hull:
                    return False
        return True

    def relevant_rules(
        self,
        categories: set["HierarchicalCategory"],
        source_categorization: typing.Optional["Categorization"] = None,
        simple_sums_only: bool = False,
    ) -> list[ConversionRule]:
        """Returns all rules which involve the given categories.

        Parameters
        ----------
        categories: set of HierarchicalCategory
            The categories to limit the rules to.
        source_categorization: Categorization, optional
            The categorization that the categories are part of, either
            self.categorization_a or self.categorization_b.
        simple_sums_only: bool, default False
            If true, only consider rules where the given categories enter as simple
            summands (i.e. with a factor of 1).

        Returns
        -------
        relevant_rules:
            All rules which touch the given categories.
        """
        relevant_rules: list[ConversionRule] = []
        if not categories:
            return relevant_rules

        if source_categorization is None:
            source_categorization = next(iter(categories)).categorization

        for rule in self.rules:
            if source_categorization == self.categorization_a:
                fc = rule.factors_categories_a
            else:
                fc = rule.factors_categories_b

            if simple_sums_only:
                rule_source_categories = {
                    cat for cat, factor in fc.items() if factor == 1
                }
            else:
                rule_source_categories = {cat for cat, factor in fc.items()}

            if categories.intersection(rule_source_categories):
                relevant_rules.append(rule)

        return relevant_rules

    def _check_over_counting_category(
        self,
        category: "HierarchicalCategory",
        source_categorization: "Categorization",
        descendants: dict[str, set[str]],
    ) -> typing.Optional[OverCountingProblem]:
        """Finds possible over counting problems for the specified category.

        Parameters
        ----------
        category: HierarchicalCategory
            The category to check.
        source_categorization: Categorization
            The categorization which contains the category (either self.categorization_a
            or self.categorization_b).
        descendants: dict
            Caching dict with descendant information. Before calculating potentially
            costly descendant information, it will be taken from this dict. If new
            descendant information is calculated, it will be put into this dict.

        Notes
        -----
        The algorithm is:

        Definition:
        The ancestral set A(c) of a category c is the set
        comprising the category, its parents, and all members of the ancestral set of
        each of its parents.

        Definition:
        The descendents D(c) of a category c are the children of c, and all
        descendents of the children of c.

        Definition:
        The projection P_S(c) of a category c using the conversion S is the set of
        categories which receive at least a part of the contents of category c according
        to the rules of conversion S.
        I assume without loss of generality that c is part of the left-hand-side
        Categorization of S.
        Then, assuming that the conversion S only contains simple sums
        without repeated categories in its rules, it follows that P_S(c) is the set of
        categories which are in the right hand side of rules in S where c is in the
        left hand side.

        Definition:
        The ancestral projections PA_S(c) of a category c using the conversion S is the
        set of projections of the ancestral set, i.e.
        PA_S(c) = {P_S(a) for a in A(c)}

        Definition:
        The hull hull(MM) of the set MM, which is comprised of sets itself, is the union
        of all members of MM.

        Definition:
        A largest element max(MM) of the set MM, which is comprised of sets itself, is
        an element with the highest number of elements.

        Definition:
        The leave node groups L(MM) of a set MM, which is comprised of sets itself, are
        the sets in MM which have only members that have no descendant in hull(MM).
        L(MM) = {M in MM and
           (for all members c of M:
               for all descendants d of c:
                d not in hull(MM)
           )}

        Then, an over counting problem is found for category c if
        hull(L(PA_S(c))) != max(L(PA_S(C)))
        """

        # A(c)
        ancestral_set = set(category.ancestors)
        ancestral_set.add(category)

        # PA_S(c)
        relevant_rules = self.relevant_rules(
            categories=ancestral_set,
            source_categorization=source_categorization,
            simple_sums_only=True,
        )
        # TODO: for now, only use rules that don't have aux categories
        relevant_rules = [rule for rule in relevant_rules if not rule.is_restricted]
        projected_ancestral_set: list[set["HierarchicalCategory"]] = []
        for rule in relevant_rules:
            if source_categorization == self.categorization_a:
                fc = rule.factors_categories_b
            else:
                fc = rule.factors_categories_a
            target_categories = {cat for cat, factor in fc.items() if factor == 1}
            projected_ancestral_set.append(target_categories)  # type: ignore

        if not projected_ancestral_set:  # trivial
            return None

        # for performance, use codes (which are guaranteed to be unique within a
        # categorization) for the comparisons here
        projected_ancestral_set_codes = [
            {c.codes[0] for c in group} for group in projected_ancestral_set
        ]

        # hull(PA_S(c))
        hull: set[str] = set().union(*projected_ancestral_set_codes)

        # L(PA_S(c))
        leave_node_groups = [
            m
            for m in projected_ancestral_set
            if self._leave_node_group(m, hull, descendants)
        ]

        leave_hull = set().union(*leave_node_groups)
        largest = max(leave_node_groups, key=len)

        if len(leave_hull) != len(largest):
            return OverCountingProblem(
                category=category,
                rules=relevant_rules,
                leave_node_groups=leave_node_groups,
            )
        else:
            return None

    def __eq__(self, other):
        return (
            isinstance(other, Conversion)
            and self.categorization_a == other.categorization_a
            and self.categorization_b == other.categorization_b
            and self.rules == other.rules
        )
