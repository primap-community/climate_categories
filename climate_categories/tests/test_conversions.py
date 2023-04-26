"""Tests for _conversions"""

import datetime
import importlib
import importlib.resources
from io import StringIO

import pytest
import strictyaml as sy

import climate_categories
import climate_categories._conversions as conversions
import climate_categories.tests
import climate_categories.tests.data


class TestConversionRuleSpec:
    def test_to_csv_row(self):
        crs = conversions.ConversionRuleSpec(
            factors_categories_a={"A": 1, "B": -1},
            factors_categories_b={"C": 1},
            auxiliary_categories={"aux": {"auxB", "auxA"}},
            comment="nice comment",
        )
        assert crs.to_csv_row() == [
            "A - B",
            "auxA auxB",
            "C",
            "nice comment",
        ]

    def test_str(self):
        crs = conversions.ConversionRuleSpec(
            factors_categories_a={"A": 1, "B": -1},
            factors_categories_b={"C": 1},
            auxiliary_categories={"aux": set()},
            comment="nice comment",
        )
        assert str(crs) == "A - B,,C,nice comment"
        crs_csv = conversions.ConversionRuleSpec(
            factors_categories_a={"A": 1, "B": -1},
            factors_categories_b={"C": 1},
            auxiliary_categories={"aux": {"auxB", "auxA"}},
            comment="nice comment",
            csv_original_text='A-B, auxB auxA, "C",nice comment',
            csv_line_number=4,
        )
        assert str(crs_csv) == 'A-B, auxB auxA, "C",nice comment'


class TestConversionRule:
    def test_str(self):
        C96 = climate_categories.IPCC1996
        C06 = climate_categories.IPCC2006
        gas = climate_categories.gas
        cr = conversions.ConversionRule(
            factors_categories_a={C96["1"]: 1, C96["2"]: -1},
            factors_categories_b={C06["3"]: 1},
            auxiliary_categories={gas: set()},
            comment="nice comment",
        )
        assert str(cr) == "1 - 2,,3,nice comment"

        reparsed = conversions.ConversionRuleSpec.from_csv_row(
            str(cr).split(","), ["gas"]
        ).hydrate(C96, C06, {"gas": gas})
        assert reparsed == cr

        cr_csv = conversions.ConversionRule(
            factors_categories_a={C96["1"]: 1, C96["2"]: -1},
            factors_categories_b={C06["3"]: 1},
            auxiliary_categories={gas: {gas["CO2"]}},
            comment="nice comment",
            csv_original_text='"1"-"2", CO2 , "3",nice comment',
            csv_line_number=4,
        )
        assert str(cr_csv) == '"1"-"2", CO2 , "3",nice comment'

    def test_format_with_lineno(self):
        C96 = climate_categories.IPCC1996
        C06 = climate_categories.IPCC2006
        gas = climate_categories.gas
        cr = conversions.ConversionRule(
            factors_categories_a={C96["1"]: 1, C96["2"]: -1},
            factors_categories_b={C06["3"]: 1},
            auxiliary_categories={gas: set()},
            comment="nice comment",
            csv_line_number=4,
        )
        assert cr.format_with_lineno() == "<Rule '1 - 2,,3,nice comment' from line 4>"

    def test_cardinality(self):
        C96 = climate_categories.IPCC1996
        C06 = climate_categories.IPCC2006
        cr = conversions.ConversionRule(
            factors_categories_a={C96["1"]: 1, C96["2"]: -1},
            factors_categories_b={C06["3"]: 1},
            auxiliary_categories={},
            comment="",
            csv_line_number=4,
        )
        assert cr.cardinality_a == "many"
        assert cr.cardinality_b == "one"

    def test_restricted(self):
        C96 = climate_categories.IPCC1996
        C06 = climate_categories.IPCC2006
        gas = climate_categories.gas
        unrestricted = conversions.ConversionRule(
            factors_categories_a={C96["1"]: 1, C96["2"]: -1},
            factors_categories_b={C06["3"]: 1},
            auxiliary_categories={},
            comment="",
            csv_line_number=4,
        )
        restricted = conversions.ConversionRule(
            factors_categories_a={C96["1"]: 1, C96["2"]: -1},
            factors_categories_b={C06["3"]: 1},
            auxiliary_categories={gas: set("NO2")},
            comment="",
            csv_line_number=4,
        )
        assert not unrestricted.is_restricted
        assert restricted.is_restricted


class TestConversionSpec:
    def test_good_csv(self, tmp_path):
        # write CSV resource to file to test also file opening path
        good_csv = (
            importlib.resources.files("climate_categories.tests.data")
            .joinpath("good_conversion.csv")
            .open()
        )
        temp_csv = tmp_path / "gc.csv"
        with temp_csv.open("w") as fd2:
            fd2.write(good_csv.read())

        # Now actually read from the file
        conv = conversions.ConversionSpec.from_csv(temp_csv)
        assert conv.categorization_a_name == "A"
        assert conv.categorization_b_name == "B"
        assert conv.comment == "A correct conversion specification file"
        assert conv.version == "1.2.3.4"
        assert conv.references == "expert judgement"
        assert conv.last_update == datetime.datetime(2099, 12, 31, 0, 0)
        assert conv.auxiliary_categorizations_names == ["aux1", "aux2"]
        assert len(conv.rule_specs) == 9
        assert conv.rule_specs[0] == conversions.ConversionRuleSpec(
            factors_categories_a={"asdf": 1, "fdsa": 1},
            factors_categories_b={"asdf": 1},
            auxiliary_categories={"aux1": set(), "aux2": set()},
            csv_line_number=6,
            csv_original_text="asdf + fdsa,,,asdf",
        )
        assert conv.rule_specs[1] == conversions.ConversionRuleSpec(
            factors_categories_a={"A.5": 1},
            factors_categories_b={"4": 1},
            auxiliary_categories={
                "aux1": {"3", "4", "A", "argl-5"},
                "aux2": {"B A", "A", "B"},
            },
            csv_line_number=7,
            csv_original_text='A.5,3 4 A "argl-5", "B A" B A,4',
        )
        assert conv.rule_specs[2] == conversions.ConversionRuleSpec(
            factors_categories_a={"b": 1, "argl.5": 1, "c": 1},
            factors_categories_b={"D": 1},
            auxiliary_categories={"aux1": set(), "aux2": set()},
            comment="nobody needs argl",
            csv_line_number=8,
            csv_original_text='b + "argl.5" + c,,,D,nobody needs argl',
        )
        assert conv.rule_specs[3] == conversions.ConversionRuleSpec(
            factors_categories_a={"b": 1, "argl,5": 1, "c": 1},
            factors_categories_b={"D": 1},
            auxiliary_categories={"aux1": set(), "aux2": set()},
            csv_line_number=9,
            csv_original_text='b + "argl,5" + c,,,D',
        )
        assert conv.rule_specs[4] == conversions.ConversionRuleSpec(
            factors_categories_a={"b": 1, 'argl"5': 1, "c": 1},
            factors_categories_b={"D": 1},
            auxiliary_categories={"aux1": set(), "aux2": set()},
            csv_line_number=10,
            csv_original_text='b + "argl\\"5" + c,,,D',
        )
        assert conv.rule_specs[5] == conversions.ConversionRuleSpec(
            factors_categories_a={"b": 1, 'argl"5': 1, "c": 1},
            factors_categories_b={"D": 1, "E": 1},
            auxiliary_categories={"aux1": set(), "aux2": set()},
            csv_line_number=11,
            csv_original_text='b + "argl\\"5" + c,,,D+E',
        )
        assert conv.rule_specs[6] == conversions.ConversionRuleSpec(
            factors_categories_a={"argl,5": 1},
            factors_categories_b={"D": 1},
            auxiliary_categories={"aux1": set(), "aux2": set()},
            csv_line_number=12,
            csv_original_text='"argl,5",,,D',
        )
        assert conv.rule_specs[7] == conversions.ConversionRuleSpec(
            factors_categories_a={"+": 1, "-": -1},
            factors_categories_b={"-": 1},
            auxiliary_categories={"aux1": set(), "aux2": set()},
            csv_line_number=13,
            csv_original_text='"+" - "-",,,"-"',
        )
        assert conv.rule_specs[8] == conversions.ConversionRuleSpec(
            factors_categories_a={"b": 1},
            factors_categories_b={"asdf": 1, "4": 1},
            auxiliary_categories={"aux1": set(), "aux2": set()},
            csv_line_number=14,
            csv_original_text="b,,,asdf+4",
        )

        assert repr(conv) == "<ConversionSpec 'A' <-> 'B' with 9 rules>"

    def test_formula_broken(self):
        csv = StringIO(
            "# comment: no comment\n"
            "A,species,B,comment\n"
            "A.1+,something,C,broken formula\n"
        )
        with pytest.raises(ValueError, match="line 3.*Could not parse"):
            climate_categories._conversions.ConversionSpec.from_csv(csv)

    def test_unknown_meta_data(self):
        csv = StringIO(
            "# comment: no comment\n"
            "# interjection: What you guys are referring to as Linux\n"
        )
        with pytest.raises(sy.exceptions.YAMLValidationError):
            climate_categories._conversions.ConversionSpec.from_csv(csv)

    def test_comment_missing(self):
        csv = StringIO("# comment: no comment\n" "A,aux,B\n" "A.1,D,A.2\n")
        with pytest.raises(
            ValueError, match="Last column must be 'comment', but isn't."
        ):
            climate_categories._conversions.ConversionSpec.from_csv(csv)


def load_conversion_from_csv(fname: str):
    fd = (
        importlib.resources.files("climate_categories.tests.data")
        .joinpath(fname)
        .open()
    )
    gc = conversions.ConversionSpec.from_csv(fd)

    cats = {
        cat_name: climate_categories.Categorization.from_yaml(
            importlib.resources.files("climate_categories.tests.data")
            .joinpath(f"good_conversion_{cat_name}.yaml")
            .open()
        )
        for cat_name in ("A", "B", "aux1", "aux2")
    }

    return gc.hydrate(cats)


@pytest.fixture
def good_conversion():
    return load_conversion_from_csv("good_conversion.csv")


@pytest.fixture
def good_conversion_reversed():
    return load_conversion_from_csv("good_conversion_reversed.csv")


class TestConversion:
    def test_not_implemented(self):
        with pytest.raises(NotImplementedError):
            climate_categories.IPCC1996.conversion_to(climate_categories.gas)

    def test_symmetry(self):
        a = climate_categories.IPCC1996.conversion_to(climate_categories.IPCC2006)
        b = climate_categories.IPCC2006.conversion_to(climate_categories.IPCC1996)
        assert a == b.reversed()
        assert a == a.reversed().reversed()

    def test_str_arg(self):
        a = climate_categories.IPCC1996.conversion_to(climate_categories.IPCC2006)
        b = climate_categories.IPCC1996.conversion_to("IPCC2006")
        assert a == b

    def test_find_unmapped_categories(self, good_conversion: conversions.Conversion):
        missing_a, missing_b = good_conversion.find_unmapped_categories()
        assert missing_a == {good_conversion.categorization_a["unmapped"]}
        assert missing_b == set()

    def test_reverse(
        self,
        good_conversion: conversions.Conversion,
        good_conversion_reversed: conversions.Conversion,
    ):
        assert good_conversion.reversed() == good_conversion_reversed
        assert good_conversion_reversed.reversed() == good_conversion

    def test_repr(self, good_conversion: conversions.Conversion):
        assert repr(good_conversion) == "<Conversion 'A' <-> 'B' with 9 rules>"

    def test_not_allowed(self):
        with pytest.raises(ValueError, match="Error in line 10: Could not parse:"):
            load_conversion_from_csv("broken_conversion_not_allowed.csv")

    def test_not_existing(self):
        with pytest.raises(
            ValueError, match="Error in line 10: 'notexisting' not in A"
        ):
            load_conversion_from_csv("broken_conversion_not_existing.csv")

    def test_describe(self, good_conversion: conversions.Conversion):
        assert (
            good_conversion.describe_detailed()
            == """# Mapping between A and B

## Simple direct mappings

Only for aux1 in ['3', '4', 'A', 'argl-5'] and aux2 in ['A', 'B', 'B A']
A A.5 The category A.5, aka b
B 4 the number four

A argl,5 weirder characters
B D d


## One-to-many mappings - one A to many B

A A.5 The category A.5, aka b
⮁
B asdf ASDF
B 4 the number four


## Many-to-one mappings - many A to one B

A asdf ASDF
A fdsa FDSA
⮁
B asdf ASDF

A A.5 The category A.5, aka b
A argl.5 We are testing weird characters
A c The sea
⮁
B D d
# Comment: 'nobody needs argl'

A A.5 The category A.5, aka b
A argl,5 weirder characters
A c The sea
⮁
B D d

A A.5 The category A.5, aka b
A argl"5 stretching the dredibility
A c The sea
⮁
B D d

A + sure, make the code for your category a plus sign
-1 * A - even better
⮁
B - a minus sign


## Many-to-many mappings - many A to many B

A A.5 The category A.5, aka b
A argl"5 stretching the dredibility
A c The sea
⮁
B D d
B E e


## Unmapped categories

### A
unmapped it hurts to be forgotten

### B


"""
        )


def test_over_counting_problem():
    C96 = climate_categories.IPCC1996
    C06 = climate_categories.IPCC2006
    OP = conversions.OverCountingProblem(
        category=C96["1"],
        leave_node_groups=[{C06["1"], C06["2"]}],
        rules=[
            conversions.ConversionRule(
                factors_categories_a={C96["1"]: 1},
                factors_categories_b={C06["1"]: 1, C06["2"]: 1},
                auxiliary_categories={},
            )
        ],
    )

    assert (
        str(OP)
        == """<IPCC1996: '1'> is possibly counted multiple times
involved leave groups categories: [[<IPCC2006: '1'>, <IPCC2006: '2'>]]
involved rules: <Rule '1,1 + 2,'>."""
    )


def test_relevant_rules():
    C96 = climate_categories.IPCC1996
    C06 = climate_categories.IPCC2006

    conv = C96.conversion_to(C06)

    assert conv.relevant_rules({C96["1"], C96["2"]}) == conv.relevant_rules(
        {C96["1"], C96["2"]}, source_categorization=C96
    )

    assert len(conv.relevant_rules({C96["4.D"]})) == 1
    assert len(conv.relevant_rules({C96["4.B.10"]}, simple_sums_only=True)) == 1
    assert conv.relevant_rules(set()) == []
