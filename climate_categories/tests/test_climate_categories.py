"""Tests for `climate_categories` package."""

import datetime
import importlib
import importlib.resources
import pathlib

import pandas as pd
import pytest
import strictyaml

import climate_categories
import climate_categories.tests
import climate_categories.tests.data


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
        assert repr(SimpleCat["1"]) == "<SimpleCat: '1'>"
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
        assert list(SimpleCat.items()) == [
            ("1", SimpleCat["1"]),
            ("2", SimpleCat["2"]),
            ("3", SimpleCat["3"]),
            ("unnumbered", SimpleCat["unnumbered"]),
        ]
        assert len(SimpleCat) == 4

    def test_comparisons(self, SimpleCat: climate_categories.Categorization):
        assert list(sorted(SimpleCat.values())) == [
            SimpleCat["1"],
            SimpleCat["2"],
            SimpleCat["3"],
            SimpleCat["unnumbered"],
        ]

        assert SimpleCat["1"] != "1"
        assert SimpleCat["1"] != SimpleCat["2"]
        assert SimpleCat["1"] == SimpleCat["1"]
        ext = SimpleCat.extend(
            name="ext",
            categories={"10": {"title": "ten"}},
            alternative_codes={"yksi": "1"},
        )
        assert SimpleCat["1"] == ext["1"]
        assert SimpleCat["2"] == ext["2"]
        assert ext["yksi"] < SimpleCat["2"]
        assert not ext["yksi"] < SimpleCat["1"]

        assert list(sorted(ext.values())) == [
            ext["1"],
            ext["2"],
            ext["3"],
            ext["10"],
            ext["unnumbered"],
        ]

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
        assert repr(SimpleCat_ext["1"]) == "<SimpleCat_ext: '1'>"
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

    def test_extend_defaults(self, SimpleCat: climate_categories.Categorization):
        a = SimpleCat.extend(name="ext")
        assert a.name == "SimpleCat_ext"
        assert a.references == ""
        assert a.institution == ""
        assert a.title == "Simple Categorization + ext"
        assert (
            a.comment == "A simple example categorization without relationships between"
            " categories extended by ext"
        )
        assert a.last_update == datetime.date.today()

    def test_extend_not_defaults(self, SimpleCat: climate_categories.Categorization):
        b = SimpleCat.extend(
            name="ext",
            title="title",
            comment="comment",
            last_update=datetime.date.fromisoformat("2020-02-20"),
        )
        assert b.name == "SimpleCat_ext"
        assert b.references == ""
        assert b.institution == ""
        assert b.title == "Simple Categorizationtitle"
        assert (
            b.comment == "A simple example categorization without relationships between"
            " categoriescomment"
        )
        assert b.last_update == datetime.date.fromisoformat("2020-02-20")


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
        assert repr(HierCat["0"]) == "<HierCat: '0'>"
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

        assert HierCat.ancestors("1A") == {HierCat["1"], HierCat["0"], HierCat["0X3"]}
        assert HierCat.descendants("0X3") == {
            HierCat["1"],
            HierCat["2"],
            HierCat["1A"],
            HierCat["1B"],
            HierCat["2A"],
            HierCat["2B"],
        }

        assert HierCat["1A"].is_leaf
        assert not HierCat["1"].is_leaf
        assert HierCat.is_leaf("3A")
        assert HierCat.leaf_children("1") == [{HierCat["1A"], HierCat["1B"]}]
        assert HierCat.leaf_children("0X3") == [
            {HierCat["1A"], HierCat["1B"], HierCat["2A"], HierCat["2B"]}
        ]
        assert HierCat.leaf_children("0") == [
            {HierCat["1A"], HierCat["1B"], HierCat["2A"], HierCat["2B"], HierCat["3A"]},
            {HierCat["1A"], HierCat["1B"], HierCat["2A"], HierCat["2B"], HierCat["3A"]},
            {HierCat["1A"], HierCat["1B"], HierCat["2A"], HierCat["2B"], HierCat["3A"]},
        ]
        assert HierCat.leaf_children("OT") == [{HierCat["1B"], HierCat["2B"]}]

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
        assert list(HierCat.items()) == [
            ("0", HierCat["0"]),
            ("1", HierCat["1"]),
            ("2", HierCat["2"]),
            ("3", HierCat["3"]),
            ("1A", HierCat["1A"]),
            ("1B", HierCat["1B"]),
            ("2A", HierCat["2A"]),
            ("2B", HierCat["2B"]),
            ("3A", HierCat["3A"]),
            ("0X3", HierCat["0X3"]),
            ("OT", HierCat["OT"]),
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

    def test_extend_new_alternatives(
        self, HierCat: climate_categories.HierarchicalCategorization
    ):
        ext = HierCat.extend(name="ext", alternative_codes={"yksi": "1"})
        assert ext["yksi"] == HierCat["1"]

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

    def test_level_error(self, HierCat: climate_categories.HierarchicalCategorization):
        HierCat.canonical_top_level_category = None
        with pytest.raises(ValueError, match="Can not calculate the level"):
            _ = HierCat["1"].level

    def test_parents_code(self, HierCat):
        assert HierCat.parents(HierCat["1"]) == HierCat.parents("1")

    def test_children_code(self, HierCat):
        assert HierCat.children(HierCat["1"]) == HierCat.children("1")


def test_compare(HierCat, SimpleCat):
    assert HierCat != SimpleCat
    assert HierCat != "HierCat"
    ext = HierCat.extend(name="ext")
    assert HierCat != ext


class TestShowAsTree:
    def test_show_as_tree(self, HierCat):
        assert (
            HierCat.show_as_tree()
            == """0 Category 0
╠╤══ ('0 Category 0's children, option 1)
║├1 Category 1
║│├1A Category 1A
║│╰1B Category 1B
║├2 Category 2
║│├2A Category 2A
║│╰2B Category 2B
║╰3 Category 3
║ ╰3A Category 3A
╠╕ ('0 Category 0's children, option 2)
║├0X3 Total excluding category 3
║│├1 Category 1
║││├1A Category 1A
║││╰1B Category 1B
║│╰2 Category 2
║│ ├2A Category 2A
║│ ╰2B Category 2B
║╰3 Category 3
║ ╰3A Category 3A
╠╕ ('0 Category 0's children, option 3)
║├1A Category 1A
║├1B Category 1B
║├2 Category 2
║│├2A Category 2A
║│╰2B Category 2B
║╰3 Category 3
║ ╰3A Category 3A
╚═══

OT Other top category
├1B Category 1B
╰2B Category 2B
"""
        )

    def test_format_func(self, HierCat):
        assert (
            HierCat.show_as_tree(format_func=lambda x: x.codes[0])
            == """0
╠╤══ ('0's children, option 1)
║├1
║│├1A
║│╰1B
║├2
║│├2A
║│╰2B
║╰3
║ ╰3A
╠╕ ('0's children, option 2)
║├0X3
║│├1
║││├1A
║││╰1B
║│╰2
║│ ├2A
║│ ╰2B
║╰3
║ ╰3A
╠╕ ('0's children, option 3)
║├1A
║├1B
║├2
║│├2A
║│╰2B
║╰3
║ ╰3A
╚═══

OT
├1B
╰2B
"""
        )

    def test_maxdepth(self, HierCat):
        assert (
            HierCat.show_as_tree(maxdepth=2)
            == """0 Category 0
╠╤══ ('0 Category 0's children, option 1)
║├1 Category 1
║├2 Category 2
║╰3 Category 3
╠╕ ('0 Category 0's children, option 2)
║├0X3 Total excluding category 3
║╰3 Category 3
╠╕ ('0 Category 0's children, option 3)
║├1A Category 1A
║├1B Category 1B
║├2 Category 2
║╰3 Category 3
╚═══

OT Other top category
├1B Category 1B
╰2B Category 2B
"""
        )

    def test_root(self, HierCat):
        assert (
            HierCat.show_as_tree(root="1")
            == """1 Category 1
├1A Category 1A
╰1B Category 1B
"""
        )


class TestIO:
    def test_spec_misses_hierarchical(self, spec_simple):
        with pytest.raises(KeyError):
            del spec_simple["hierarchical"]
            climate_categories.Categorization.from_spec(spec_simple)

    def test_spec_wrong_hierarchical(self, spec_simple, spec_hier):
        with pytest.raises(
            ValueError, match="Specification is for a hierarchical categorization"
        ):
            climate_categories.Categorization.from_spec(spec_hier)

        with pytest.raises(
            ValueError, match="Specification is for a non-hierarchical categorization"
        ):
            climate_categories.HierarchicalCategorization.from_spec(spec_simple)

    def test_from_spec(self, spec_simple, SimpleCat):
        fs = climate_categories.from_spec(spec_simple)
        assert fs == SimpleCat
        assert fs.keys() == SimpleCat.keys()
        assert list(fs.values()) == list(SimpleCat.values())

    def test_to_python(self, tmpdir, HierCat):
        HierCat.to_python(tmpdir / "any_cat.py")

    def test_roundtrip(self, tmpdir, any_cat):
        any_cat.to_yaml(tmpdir / "any_cat.yaml")
        any_cat_r = climate_categories.from_yaml(tmpdir / "any_cat.yaml")
        assert any_cat == any_cat_r
        assert list(any_cat.values()) == list(any_cat_r.values())

        any_cat.to_pickle(tmpdir / "any_cat.pickle")
        any_cat_p = climate_categories.from_pickle(tmpdir / "any_cat.pickle")
        assert any_cat == any_cat_p
        assert list(any_cat.values()) == list(any_cat_p.values())

        any_cat.to_python(tmpdir / "any_cat.py")
        any_cat_py = climate_categories.from_python(tmpdir / "any_cat.py")
        assert any_cat == any_cat_py
        assert list(any_cat.values()) == list(any_cat_py.values())

        assert climate_categories.from_pickle(
            tmpdir / "any_cat.pickle"
        ) == climate_categories.Categorization.from_pickle(tmpdir / "any_cat.pickle")

        assert climate_categories.from_python(
            tmpdir / "any_cat.py"
        ) == climate_categories.Categorization.from_python(tmpdir / "any_cat.py")

    def test_roundtrip_hierarchical(self, tmpdir, HierCat):
        HierCat.to_yaml(tmpdir / "HierCat.yaml")
        HierCat_r = climate_categories.HierarchicalCategorization.from_yaml(
            tmpdir / "HierCat.yaml"
        )
        assert HierCat == HierCat_r

    def test_broken(self):
        with pytest.raises(
            strictyaml.YAMLValidationError,
            match="unexpected key not in schema 'reefrences'",
        ):
            climate_categories.HierarchicalCategorization.from_yaml(
                importlib.resources.files("climate_categories.tests.data")
                .joinpath("broken_hierarchical_categorization.yaml")
                .open()
            )

    def test_broken_hierarchical(self):
        with pytest.raises(ValueError, match="'hierarchical' must be "):
            climate_categories.from_yaml(
                importlib.resources.files("climate_categories.tests.data")
                .joinpath("broken_simple_categorization.yaml")
                .open()
            )
