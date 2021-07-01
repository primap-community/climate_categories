"""Tests for _conversions"""

import importlib
import importlib.resources

import pytest

import climate_categories
import climate_categories._conversions
import climate_categories.tests
import climate_categories.tests.data


class TestConversions:
    def test_good_csv(self):
        fd = importlib.resources.open_text(
            climate_categories.tests.data,
            "good_conversion.csv",
        )
        conv = climate_categories._conversions.Conversion.from_csv(fd)
        assert conv.categorization_a == "A"
        assert conv.categorization_b == "B"
        assert conv.conversion_factors == [
            ({"asdf": 1, "fdsa": 1}, {"asdf": 1}),
            ({"A.5": 1}, {"4": 1}),
            ({"b": 1, "argl.5": 1, "c": 1}, {"D": 1}),
            ({"b": 1, "argl,5": 1, "c": 1}, {"D": 1}),
            ({"b": 1, 'argl"5': 1, "c": 1}, {"D": 1}),
            ({"argl,5": 1}, {"D": 1}),
            ({"+": 1, "-": 1}, {"-": 1}),
        ]

    def test_bad_csv(self):
        fd = importlib.resources.open_text(
            climate_categories.tests.data,
            "bad_conversion.csv",
        )
        with pytest.raises(ValueError, match="line 4"):
            climate_categories._conversions.Conversion.from_csv(fd)
