"""Tests for `climate_categories` package."""

import datetime
import pathlib

import pandas as pd
import pytest
import strictyaml

import climate_categories


class TestSimple:
    def test_meta(self, SimpleCat: climate_categories.Categorization):
        assert SimpleCat.name == "SimpleCat" == str(SimpleCat)
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
        assert (
            repr(SimpleCat)
            == "<Categorization SimpleCat 'Simple Categorization' with 4 categories>"
        )

    def test_categories(self, SimpleCat: climate_categories.Categorization):
        assert "1" in SimpleCat
        assert SimpleCat["1"].title == "Category 1"
        assert SimpleCat["1"].comment == "The first category"
        assert SimpleCat["1"].codes == ("1", "A", "CatA")
        assert SimpleCat["1"] == SimpleCat["A"] == SimpleCat["CatA"]
        assert SimpleCat["1"] != SimpleCat["2"]
        assert SimpleCat["unnumbered"].title == "The unnumbered category"
        assert repr(SimpleCat["1"]) == "<Category 1>"
        assert str(SimpleCat["1"]) == "1 Category 1"
        assert SimpleCat["1"].info == {
            "important_data": ["A", "B", "C"],
            "other_important_thing": "ABC",
        }
        assert SimpleCat["2"].info == {}

    def test_dict_like(self, SimpleCat: climate_categories.Categorization):
        assert "A" in SimpleCat
        assert list(SimpleCat.all_keys()) == [
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
            index=["1", "2", "3", "unnumbered"],
            data={
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
            },
        )
        pd.testing.assert_frame_equal(SimpleCat.df, expected)

    def test_extend(self, SimpleCat: climate_categories.Categorization):
        SimpleCat_ext = SimpleCat.extend(
            name="ext",
            categories={
                "4": {
                    "title": "Category 4",
                    "comment": "The fourth category",
                    "alternative_codes": ["D", "CatD"],
                },
                "t": {"title": "Category T"},
            },
            title=" title_ext",
            alternative_codes={"I": "1", "II": "2", "III": "3", "drai": "3", "IV": "4"},
        )
        assert SimpleCat_ext.name == "SimpleCat_ext"
        assert SimpleCat_ext.title == "Simple Categorization title_ext"
        assert SimpleCat_ext.references == ""
        assert SimpleCat_ext.last_update == datetime.date.today()
        assert SimpleCat_ext.institution == ""
        assert SimpleCat_ext.version == "1"
        assert (
            SimpleCat_ext.comment
            == "A simple example categorization without relationships between"
            " categories extended by ext"
        )
        assert SimpleCat_ext.hierarchical is False

        assert "1" in SimpleCat_ext
        assert SimpleCat_ext["1"].title == "Category 1"
        assert SimpleCat_ext["1"].comment == "The first category"
        assert SimpleCat_ext["1"].codes == ("1", "A", "CatA", "I")
        assert SimpleCat_ext["1"] == SimpleCat_ext["A"] == SimpleCat["CatA"]
        assert SimpleCat_ext["1"] != SimpleCat_ext["2"]
        assert SimpleCat_ext["unnumbered"].title == "The unnumbered category"
        assert repr(SimpleCat_ext["1"]) == "<Category 1>"
        assert str(SimpleCat_ext["1"]) == "1 Category 1"

        assert "A" in SimpleCat_ext
        assert "D" in SimpleCat_ext
        assert SimpleCat_ext["1"] == SimpleCat_ext["I"]
        assert SimpleCat_ext["III"] == SimpleCat["3"] == SimpleCat_ext["drai"]
        assert list(SimpleCat_ext.all_keys()) == [
            "1",
            "A",
            "CatA",
            "I",
            "2",
            "B",
            "CatB",
            "II",
            "3",
            "C",
            "CatC",
            "III",
            "drai",
            "unnumbered",
            "4",
            "D",
            "CatD",
            "IV",
            "t",
        ]
        assert list(SimpleCat_ext.keys()) == ["1", "2", "3", "unnumbered", "4", "t"]
        assert len(SimpleCat_ext) == 6


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
        assert HierCat["0"].title == "Category 0"
        assert HierCat["0"].comment == "Top-most category"
        assert HierCat["0"].codes == ("0", "TOTAL")
        assert HierCat["0"] == HierCat["TOTAL"]
        assert HierCat["0"] != HierCat["1"]
        assert repr(HierCat["0"]) == "<HierarchicalCategory 0>"
        assert str(HierCat["0"]) == "0 Category 0"
        assert HierCat["1"].info == {
            "SomeInfo": "A",
            "OtherInfo": ["A", "B", "C"],
        }
        assert HierCat["2"].info == {}

    def test_category_relationships(
        self, HierCat: climate_categories.HierarchicalCategorization
    ):
        assert HierCat["0"].children == [
            {HierCat["1"], HierCat["2"], HierCat["3"]},
            {HierCat["0X3"], HierCat["3"]},
            {HierCat["1A"], HierCat["1B"], HierCat["2"], HierCat["3"]},
        ]
        assert HierCat["1"].parents == {HierCat["0"], HierCat["0X3"]}
        assert HierCat.canonical_top_level_category == HierCat["0"]

        assert HierCat.level("0") == 1
        assert HierCat.level("1") == 2
        assert HierCat.level("2") == 2
        assert HierCat.level("0X3") == 2
        assert HierCat.level("1B") == 3

        with pytest.raises(
            ValueError,
            match="'OT' is not a transitive child of the canonical top level '0'.",
        ):
            HierCat.level("OT")

    def test_dict_like(self, HierCat: climate_categories.HierarchicalCategorization):
        assert "0" in HierCat
        assert list(HierCat.all_keys()) == [
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
            index=["0", "1", "2"],
            data={
                "title": ["Category 0", "Category 1", "Category 2"],
                "comment": [
                    "Top-most category",
                    "The first category",
                    "The second category",
                ],
                "alternative_codes": [("TOTAL",), tuple(), tuple()],
                "children": [
                    (("1", "2", "3"), ("0X3", "3"), ("1A", "1B", "2", "3")),
                    (("1A", "1B"),),
                    (("2A", "2B"),),
                ],
            },
        )
        pd.testing.assert_frame_equal(HierCat.df.head(3), expected)

    def test_extend(self, HierCat: climate_categories.HierarchicalCategorization):
        HierCat_ext = HierCat.extend(
            name="ext",
            categories={
                "2A1": {"title": "Category 2A1"},
                "2A2": {"title": "Category 2A2"},
            },
            children=[("2A", ("2A1", "2A2")), ("2", ("2A1", "2A2", "2B"))],
        )
        assert HierCat_ext.name == "HierCat_ext"
        assert HierCat_ext.title == "Hierarchical Categorization + ext"
        assert HierCat_ext.references == ""
        assert HierCat_ext.last_update == datetime.date.today()
        assert HierCat_ext.institution == ""
        assert HierCat_ext.version == "one"
        assert (
            HierCat_ext.comment
            == "A simple hierarchical categorization with categories with relationships"
            " extended by ext"
        )
        assert HierCat_ext.hierarchical is True

        self.test_categories(HierCat=HierCat_ext)

        assert HierCat_ext["2"].children == [
            {HierCat_ext["2A"], HierCat_ext["2B"]},
            {HierCat_ext["2A1"], HierCat_ext["2A2"], HierCat_ext["2B"]},
        ]
        assert HierCat_ext["2A1"].level == 4
        assert HierCat_ext["2A1"].title == "Category 2A1"
        assert HierCat_ext["2A1"].comment is None
        assert HierCat_ext["2A1"].children == []

        assert "0" in HierCat_ext
        assert list(HierCat_ext.all_keys()) == [
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
            "2A1",
            "2A2",
        ]
        assert list(HierCat_ext.keys()) == [
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
            "2A1",
            "2A2",
        ]
        assert len(HierCat_ext) == 13

    def test_roundtrip(self, HierCat, tmpdir):
        f = pathlib.Path(tmpdir) / "thing.yaml"
        HierCat.to_yaml(f)
        ReRead = climate_categories.HierarchicalCategorization.from_yaml(f)
        assert HierCat.name == ReRead.name
        assert HierCat.title == ReRead.title
        assert HierCat.comment == ReRead.comment
        assert HierCat.references == ReRead.references
        assert HierCat.hierarchical == ReRead.hierarchical
        assert HierCat.total_sum == ReRead.total_sum
        assert HierCat.last_update == ReRead.last_update
        assert HierCat.version == ReRead.version
        for key in HierCat:
            assert key in ReRead
            assert HierCat[key] == ReRead[key]
        assert HierCat == ReRead


def test_broken():
    with pytest.raises(
        strictyaml.YAMLValidationError,
        match="unexpected key not in schema 'reefrences'",
    ):
        climate_categories.HierarchicalCategorization.from_yaml(
            pathlib.Path(__file__).parent
            / "data"
            / "broken_hierarchical_categorization.yaml"
        )
