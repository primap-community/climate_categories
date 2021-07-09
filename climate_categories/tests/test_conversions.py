"""Tests for _conversions"""

import datetime
import importlib
import importlib.resources

import pytest

import climate_categories
import climate_categories._conversions
import climate_categories.tests
import climate_categories.tests.data
from climate_categories._conversions import ConversionRule


class TestConversions:
    def test_good_csv(self):
        fd = importlib.resources.open_text(
            climate_categories.tests.data,
            "good_conversion.csv",
        )
        conv = climate_categories._conversions.ConversionRules.from_csv(fd)
        assert conv.categorization_a_name == "A"
        assert conv.categorization_b_name == "B"
        assert conv.comment == "A correct conversion specification file"
        assert conv.version == "1.2.3.4"
        assert conv.references == "expert judgement"
        assert conv.last_update == datetime.date(2099, 12, 31)
        assert conv.auxiliary_categorizations_names == ["aux1", "aux2"]
        assert len(conv.rules) == 7
        assert conv.rules[0] == ConversionRule(
            factors_categories_a={"asdf": 1, "fdsa": 1},
            factors_categories_b={"asdf": 1},
            auxiliary_categories={},
        )
        assert conv.rules[1] == ConversionRule(
            factors_categories_a={"A.5": 1},
            factors_categories_b={"4": 1},
            auxiliary_categories={
                "aux1": {"3", "4", "A", "argl-5"},
                "aux2": {"B A", "A", "B"},
            },
        )
        assert conv.rules[2] == ConversionRule(
            factors_categories_a={"b": 1, "argl.5": 1, "c": 1},
            factors_categories_b={"D": 1},
            auxiliary_categories={},
            comment="nobody needs argl",
        )
        assert conv.rules[3] == ConversionRule(
            factors_categories_a={"b": 1, "argl,5": 1, "c": 1},
            factors_categories_b={"D": 1},
            auxiliary_categories={},
        )
        assert conv.rules[4] == ConversionRule(
            factors_categories_a={"b": 1, 'argl"5': 1, "c": 1},
            factors_categories_b={"D": 1},
            auxiliary_categories={},
        )
        assert conv.rules[5] == ConversionRule(
            factors_categories_a={"argl,5": 1},
            factors_categories_b={"D": 1},
            auxiliary_categories={},
        )
        assert conv.rules[6] == ConversionRule(
            factors_categories_a={"+": 1, "-": -1},
            factors_categories_b={"-": 1},
            auxiliary_categories={},
        )

    def test_formula_broken(self):
        csv = ["comment,no comment", "", "A,B,comment", "A.1+,C,broken formula"]
        with pytest.raises(ValueError, match="line 4.*Could not parse"):
            climate_categories._conversions.ConversionRules.from_csv(csv)

    def test_meta_data_incomplete(self):
        csv = ["comment,no comment", "references"]
        with pytest.raises(
            ValueError, match="Meta data specification is incomplete in line 2"
        ):
            climate_categories._conversions.ConversionRules.from_csv(csv)

    def test_extraneous_comma(self):
        csv = ["comment,you know, nothing really works"]
        with pytest.raises(ValueError, match="did you forget to escape a comma?"):
            climate_categories._conversions.ConversionRules.from_csv(csv)

        csv = ["comment,you know\\, nothing really works", "", "A,B,comment"]
        cr = climate_categories._conversions.ConversionRules.from_csv(csv)
        assert cr.comment == "you know, nothing really works"

    def test_unknown_meta_data(self):
        csv = [
            "comment,no comment",
            "interjection,What you guys are referring to as Linux",
        ]
        with pytest.raises(
            ValueError, match="Unknown meta data key in line 2: interjection"
        ):
            climate_categories._conversions.ConversionRules.from_csv(csv)

    def test_comment_missing(self):
        csv = ["comment,no comment", "", "A,aux,B", "A.1,D,A.2"]
        with pytest.raises(
            ValueError, match="Last column must be 'comment', but isn't."
        ):
            climate_categories._conversions.ConversionRules.from_csv(csv)
