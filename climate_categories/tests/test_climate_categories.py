#!/usr/bin/env python
"""Tests for `climate_categories` package."""

import datetime

import pandas as pd
import pytest

import climate_categories


class TestSimple:
    def test_meta(self, SimpleCat: climate_categories.Categorization):
        assert SimpleCat.name == "SimpleCat"
        assert SimpleCat.title == "Simple Categorization"
        assert SimpleCat.references == "doi:00000/00000"
        assert SimpleCat.last_update == datetime.date(2021, 2, 23)
        assert SimpleCat.institution == "PIK"
        assert SimpleCat.version == "1"
        assert (
            SimpleCat.comment
            == "A simple example categorization without relationships between"
            " categories"
        )
        assert SimpleCat.hierarchical is False

    def test_categories(self, SimpleCat: climate_categories.Categorization):
        assert "1" in SimpleCat
        assert SimpleCat["1"].title == "Category 1" == str(SimpleCat["1"])
        assert SimpleCat["1"].comment == "The first category"
        assert SimpleCat["1"].codes == ["1", "A", "CatA"]
        assert SimpleCat["1"] == SimpleCat["A"] == SimpleCat["CatA"]
        assert SimpleCat["1"] != SimpleCat["2"]
        assert SimpleCat["unnumbered"].title == "The unnumbered category"
        assert (
            repr(SimpleCat["1"])
            == "<Category 'Category 1' ['1', 'A', 'CatA'] 'The first category'>"
        )

    def test_dict_like(self, SimpleCat: climate_categories.Categorization):
        assert "A" in SimpleCat
        assert list(SimpleCat) == [
            "1",
            "A",
            "CatA",
            "2",
            "B",
            "CatB",
            "3",
            "C",
            "CatC",
            "unnumbered",
        ]
        assert list(SimpleCat.keys()) == ["1", "2", "3", "unnumbered"]
        assert len(SimpleCat) == 4

    def test_df(self, SimpleCat: climate_categories.Categorization):
        expected = pd.DataFrame(
            {
                "code": ["1", "2", "3", "unnumbered"],
                "title": [
                    "Category 1",
                    "Category 2",
                    "Category 3",
                    "The unnumbered category",
                ],
                "comment": [
                    "The first category",
                    "The second category",
                    "The third category",
                    None,
                ],
                "alternative_codes": [
                    ("A", "CatA"),
                    ("B", "CatB"),
                    ("C", "CatC"),
                    tuple(),
                ],
            }
        )
        assert SimpleCat.df == expected


class TestHierarchical:
    def test_meta(self, HierCat: climate_categories.HierarchicalCategorization):
        assert HierCat.name == "HierCat"
        assert HierCat.title == "Hierarchical Categorization"
        assert HierCat.references == "doi:00000/00000"
        assert HierCat.last_update == datetime.date(2021, 2, 23)
        assert HierCat.institution == "PIK"
        assert HierCat.version == "one"
        assert (
            HierCat.comment
            == "A simple hierarchical categorization with categories with relationships"
        )
        assert HierCat.hierarchical is True

    def test_categories(self, HierCat: climate_categories.HierarchicalCategorization):
        assert "0" in HierCat
        assert HierCat["0"].title == "Category 0" == str(HierCat["0"])
        assert HierCat["0"].comment == "Top-most category"
        assert HierCat["0"].codes == ["0", "TOTAL"]
        assert HierCat["0"] == HierCat["TOTAL"]
        assert HierCat["0"] != HierCat["1"]
        assert (
            repr(HierCat["0"])
            == "<Category 'Category 0' ['0', 'TOTAL'] 'Top-most category'"
            " children: [(1, 2, 3), (0X3, 3)]>"
        )

    def test_category_relationships(
        self, HierCat: climate_categories.HierarchicalCategorization
    ):
        assert HierCat["0"].children == [
            {HierCat["1"], HierCat["2"], HierCat["3"]},
            {HierCat["OX3"], HierCat["3"]},
        ]
        assert HierCat["1"].parents == {HierCat["0"], HierCat["0X3"]}
        assert HierCat["0"].level == 1
        with pytest.raises(
            ValueError,
            match="'OT' is not a transitive child of the canonical top level '0'.",
        ):
            HierCat["OT"].level
        assert HierCat.canonical_top_level_category == HierCat["0"]
        assert HierCat["1"].level == 2
        assert HierCat["2"].level == 2
        assert HierCat["0X3"].level == 2
        assert HierCat["1B"].level == 3

    def test_dict_like(self, HierCat: climate_categories.HierarchicalCategorization):
        assert "0" in HierCat
        assert list(HierCat) == [
            "0",
            "TOTAL",
            "1",
            "2",
            "3",
            "1A",
            "1a",
            "1B",
            "1b",
            "2A",
            "2a",
            "2B",
            "2b",
            "3A",
            "3a",
            "0X3",
            "0E3",
            "OT",
        ]
        assert list(HierCat.keys()) == [
            "0",
            "1",
            "2",
            "3",
            "1A",
            "1B",
            "2A",
            "2B",
            "3A",
            "0X3",
            "OT",
        ]
        assert len(HierCat) == 11

    def test_df(self, HierCat: climate_categories.HierarchicalCategorization):
        expected = pd.DataFrame(
            {
                "code": ["0", "1", "2"],
                "title": ["Category 0", "Category 1", "Category 2"],
                "comment": [
                    "Top-most category",
                    "The first category",
                    "The second category",
                ],
                "alternative_codes": [("TOTAL",), tuple(), tuple()],
                "children": [
                    ({"1", "2", "3"}, {"0X3", "OE3"}),
                    ({"1A", "1B"},),
                    ({"2A", "2B"},),
                ],
            }
        )
        assert HierCat.df.head(3) == expected
