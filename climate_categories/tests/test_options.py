"""Tests for categorizations with options."""

import datetime
import pathlib

import pytest

import climate_categories
import climate_categories.tests.data
from climate_categories import (
    CategorizationOption,
    CategorizationRegistry,
    OptionCombination,
    OptionFamily,
    OptionManifest,
    UnsupportedCombinationError,
    UnsupportedCombinationWarning,
)

DATA_DIR = pathlib.Path(climate_categories.tests.data.__file__).parent


@pytest.fixture
def cats() -> CategorizationRegistry:
    """A registry with the Fam test family registered."""
    family = OptionFamily.from_yaml(DATA_DIR / "Fam__options.yaml")
    registry = CategorizationRegistry()
    registry["Fam"] = family.base
    family.base._cats = registry
    registry.register_family(family)
    return registry


@pytest.fixture
def fam(cats):
    return cats["Fam"]


def children(cat, code: str) -> list[set[str]]:
    return [{c.codes[0] for c in child_set} for child_set in cat[code].children]


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("ISO3", ("ISO3", ())),
        ("ISO3[]", ("ISO3", ())),
        ("ISO3[eu]", ("ISO3", ("eu",))),
        ("ISO3[unfccc,eu]", ("ISO3", ("eu", "unfccc"))),
        ("ISO3[ unfccc, eu ]", ("ISO3", ("eu", "unfccc"))),
        ("ISO3_GCAM", ("ISO3_GCAM", ())),
        ("ISO3[eu]_extended", ("ISO3[eu]_extended", ())),
    ],
)
def test_parse_name(name, expected):
    assert climate_categories.parse_name(name) == expected


def test_parse_name_duplicates():
    with pytest.raises(ValueError, match="multiple times"):
        climate_categories.parse_name("ISO3[eu,eu]")


def test_canonical_name():
    assert climate_categories.canonical_name("ISO3", []) == "ISO3"
    assert climate_categories.canonical_name("ISO3", ["b", "a"]) == "ISO3[a,b]"


def test_base(fam):
    assert fam.canonical_name == "Fam"
    assert fam.family == "Fam"
    assert fam.enabled_options == ()
    assert list(fam.available_options) == ["extra", "more", "no_c", "c_in_b"]
    assert fam.with_options([]) is fam
    assert fam.supported_combinations[0] == ()
    assert ("extra", "more") in fam.supported_combinations


def test_with_options(cats, fam):
    cat = fam.with_options(["extra"])
    assert cat.name == "Fam[extra]"
    assert cat.canonical_name == "Fam[extra]"
    assert cat.family == "Fam"
    assert cat.enabled_options == ("extra",)
    # built only once
    assert fam.with_options(["extra"]) is cat
    assert cats["Fam[extra]"] is cat
    # with_options is always relative to the base
    assert cat.with_options(["no_c"]).name == "Fam[no_c]"
    assert cat.with_options([]) is fam


def test_with_options_signature(fam):
    # a single string is an iterable of strings, too, but almost certainly a mistake
    with pytest.raises(TypeError, match=r"Use \['extra'\]"):
        fam.with_options("extra")
    with pytest.raises(TypeError, match="iterable of option names"):
        fam._option_family.get("extra")
    with pytest.raises(TypeError, match="iterable of option names"):
        climate_categories.IPCC2006.with_options("")
    # allow_unsupported is keyword-only
    with pytest.raises(TypeError):
        fam.with_options(["extra"], True)
    # any iterable works
    assert fam.with_options(("extra",)) is fam.with_options(["extra"])
    assert fam.with_options(iter(["extra"])) is fam.with_options({"extra"})


def test_additions(fam):
    cat = fam.with_options(["extra"])
    assert cat["A+B"] == cat["AB"]
    assert cat["a"] == cat["A"]
    assert cat["A"].info == {"size": "big", "colour": "red"}
    assert children(cat, "AB") == [{"A", "B"}]
    assert children(cat, "T") == [{"A", "B", "C"}, {"AB", "C"}]
    # the base is unchanged
    assert fam["A"].info == {"size": "big"}
    assert "AB" not in fam
    assert children(fam, "T") == [{"A", "B", "C"}]


def test_metadata(fam):
    cat = fam.with_options(["more", "extra"])
    assert cat.title == "Family with extra categories, more categories"
    assert "Option 'extra': Adds the sum of A and B." in cat.comment
    assert cat.references == "doi:00000/00000;\ndoi:00000/00001"
    assert cat.last_update == datetime.date(2026, 3, 1)
    assert cat.version == fam.version
    assert cat.institution == fam.institution
    assert cat.total_sum


def test_removal_drops_child_sets(fam):
    # in a total_sum categorization, child sets which don't add up any more are
    # dropped
    cat = fam.with_options(["no_c"])
    assert "C" not in cat
    assert children(cat, "T") == []
    assert cat["T"].comment == "C is missing."


def test_merge_into(fam):
    cat = fam.with_options(["c_in_b"])
    assert "C" not in cat
    assert children(cat, "T") == [{"A", "B"}]
    assert cat["T"].comment == "C (Category C) is included in B (Category B)."
    assert cat["B"].info == {"includes": ["C"]}
    assert cat["B"].comment == "Includes C (Category C)."
    assert cat.total_sum
    assert "includes" not in fam["B"].info


def test_removal_after_additions(fam):
    # removals also affect categories added by other options, regardless of the
    # order of the options
    cat = fam.with_options(["c_in_b", "more", "extra"])
    assert children(cat, "T") == [{"A", "B"}, {"AB"}]
    assert children(cat, "ABC") == [{"AB"}]


def test_removal_deduplicates_child_sets(fam):
    # after removing C, the child sets [A, B, C] and [A, B] of T are identical, so
    # only one of them is kept
    ab_set = CategorizationOption(
        name="ab_set",
        title="A and B as a child set",
        last_update=datetime.date(2026, 1, 1),
        add_children={"T": [["A", "B"]]},
    )
    c_in_b = fam.available_options["c_in_b"]
    family = OptionFamily(
        base=fam,
        manifest=OptionManifest(base="Fam", options=("ab_set", "c_in_b")),
        options={"ab_set": ab_set, "c_in_b": c_in_b},
    )
    assert children(family.build(["ab_set"]), "T") == [{"A", "B", "C"}, {"A", "B"}]
    cat = family.build(["ab_set", "c_in_b"])
    assert children(cat, "T") == [{"A", "B"}]
    assert cat.total_sum


def test_combination(fam):
    cat = fam.with_options(["extra", "no_c"])
    assert cat["AB"].info == {"note": "without C"}
    assert "combined: Without C, the extra categories are noted." in cat.comment
    assert "note" not in fam.with_options(["extra"])["AB"].info


def test_invalid_options(fam):
    with pytest.raises(ValueError, match="Unknown options"):
        fam.with_options(["nope"])
    with pytest.raises(ValueError, match="requires"):
        fam.with_options(["more"])
    with pytest.raises(ValueError, match="conflicts"):
        fam.with_options(["no_c", "c_in_b"])
    with pytest.raises(ValueError, match="multiple times"):
        fam.with_options(["extra", "extra"])


def test_supported_combinations(fam):
    # all valid combinations, except the ones containing more and no_c
    assert fam.supported_combinations == [
        (),
        ("c_in_b",),
        ("extra",),
        ("no_c",),
        ("c_in_b", "extra"),
        ("extra", "more"),
        ("extra", "no_c"),
        ("c_in_b", "extra", "more"),
    ]
    family = fam._option_family
    assert family.is_supported(["extra", "no_c"])
    assert not family.is_supported(["extra", "more", "no_c"])
    with pytest.raises(ValueError, match="requires"):
        family.is_supported(["more"])


def test_unsupported(cats, fam):
    with pytest.raises(
        UnsupportedCombinationError,
        match=r"the options \['more', 'no_c'\] are not supported together \(ABC was "
        r"not checked without C\)\. Use allow_unsupported=True",
    ):
        fam.with_options(["extra", "more", "no_c"])
    with pytest.raises(UnsupportedCombinationError):
        cats["Fam[extra,more,no_c]"]
    assert "Fam[extra,more,no_c]" not in cats

    with pytest.warns(UnsupportedCombinationWarning):
        cat = fam.with_options(["extra", "more", "no_c"], allow_unsupported=True)
    assert cat.name == "Fam[extra,more,no_c]"
    assert children(cat, "ABC") == []
    # unsupported combinations are not cached
    assert "Fam[extra,more,no_c]" not in dict(cats)
    with pytest.warns(UnsupportedCombinationWarning):
        assert (
            fam.with_options(["extra", "more", "no_c"], allow_unsupported=True)
            is not cat
        )


def test_alias(cats, fam):
    full = cats["FAM_FULL"]
    assert full.name == "FAM_FULL"
    assert full.canonical_name == "Fam[extra,more]"
    assert full.family == "Fam"
    assert full.enabled_options == ("extra", "more")
    assert "ABC" in full
    assert cats["FAM_FULL"] is full
    # the alias is a separate object with its own name, but its categories are equal
    # to the categories of the categorization with the same options
    assert full is not cats["Fam[extra,more]"]
    assert full["ABC"] == cats["Fam[extra,more]"]["ABC"]


def test_registry(cats):
    assert "Fam" in cats
    assert "Fam[extra]" in cats
    assert "Fam[more,extra]" in cats
    assert "FAM_FULL" in cats
    assert "Fam[nope]" not in cats
    assert "Fam[more]" not in cats
    assert "Other" not in cats
    assert "Other[extra]" not in cats
    assert 1 not in cats

    assert cats.get("Other") is None
    assert cats.get("Fam[extra]") is cats["Fam[extra]"]
    with pytest.raises(KeyError):
        cats["Other[extra]"]
    with pytest.raises(ValueError, match="Unknown options"):
        cats["Fam[nope]"]

    # non-canonical spellings give the canonical categorization
    assert cats["Fam[more,extra]"] is cats["Fam[extra,more]"]
    assert cats["Fam[]"] is cats["Fam"]


def test_registry_duplicate_family(cats):
    with pytest.raises(ValueError, match="already registered"):
        cats.register_family(cats.families["Fam"])


def test_category_equality(fam):
    cat = fam.with_options(["extra"])
    assert cat["A"] == fam["A"]
    assert hash(cat["A"]) == hash(fam["A"])
    assert cat["A"] in {fam["A"]}
    assert fam.with_options(["c_in_b"])["T"] == fam["T"]
    # but not with other families
    other = climate_categories.ISO3
    assert other["ABW"] != fam["A"]


def test_categorization_without_options():
    ipcc = climate_categories.IPCC2006
    assert ipcc.available_options == {}
    assert ipcc.supported_combinations == [()]
    assert ipcc.with_options([]) is ipcc
    assert ipcc.canonical_name == "IPCC2006"
    with pytest.raises(ValueError, match="has no options"):
        ipcc.with_options(["foo"])


def test_round_trip(tmp_path, cats):
    family = cats.families["Fam"]
    for option in family.options.values():
        option.to_yaml(tmp_path / "option.yaml")
        assert CategorizationOption.from_yaml(tmp_path / "option.yaml") == option
        option.to_python(tmp_path / "option.py")
        assert CategorizationOption.from_python(tmp_path / "option.py") == option

    family.manifest.to_yaml(tmp_path / "manifest.yaml")
    assert OptionManifest.from_yaml(tmp_path / "manifest.yaml") == family.manifest
    family.manifest.to_python(tmp_path / "manifest.py")
    assert OptionManifest.from_python(tmp_path / "manifest.py") == family.manifest


def test_round_trip_built(tmp_path, fam):
    cat = fam.with_options(["extra", "no_c"])
    cat.to_yaml(tmp_path / "cat.yaml")
    read = climate_categories.from_yaml(tmp_path / "cat.yaml")
    assert read.name == "Fam[extra,no_c]"
    assert read.family == "Fam"
    assert read.enabled_options == ("extra", "no_c")
    assert read == cat
    assert read["A"] == fam["A"]


def make_family(fam, **manifest_kwargs) -> OptionFamily:
    family = fam._option_family
    kwargs = {"base": "Fam", "options": tuple(family.options)} | manifest_kwargs
    return OptionFamily(
        base=fam, manifest=OptionManifest(**kwargs), options=family.options
    )


def test_invalid_manifests(fam):
    unsupported = climate_categories.UnsupportedCombination
    with pytest.raises(ValueError, match="Unknown options"):
        make_family(fam, unsupported=(unsupported(options=("nope",)),))
    with pytest.raises(ValueError, match="at least one option"):
        make_family(fam, unsupported=(unsupported(options=()),))
    with pytest.raises(ValueError, match="not a supported combination"):
        make_family(
            fam,
            unsupported=(unsupported(options=("more",)),),
            aliases={"ALIAS": ("extra", "more")},
        )
    with pytest.raises(ValueError, match="requires"):
        make_family(fam, aliases={"ALIAS": ("more",)})
    with pytest.raises(ValueError, match="invalid alias name"):
        make_family(fam, aliases={"Fam[x]": ("extra",)})
    with pytest.raises(ValueError, match="do not match"):
        make_family(fam, options=("extra", "more"))
    with pytest.raises(ValueError, match="Manifest is for"):
        make_family(fam, base="Other")
    with pytest.raises(ValueError, match="at least two"):
        make_family(
            fam,
            combinations=(climate_categories.OptionCombination(options=("extra",)),),
        )


def test_invalid_option_name():
    with pytest.raises(ValueError, match="Invalid option name"):
        CategorizationOption(
            name="a,b", title="x", last_update=datetime.date(2026, 1, 1)
        )
    with pytest.raises(ValueError, match="Invalid option name"):
        CategorizationOption(
            name="options", title="x", last_update=datetime.date(2026, 1, 1)
        )


@pytest.mark.parametrize(
    ("option_kwargs", "match"),
    [
        ({"add_categories": {"A": {"title": "A again"}}}, "already exist"),
        ({"add_categories": {"Z": {"title": "Z", "alternative_codes": ["a"]}}}, None),
        ({"add_alternative_codes": {"B": "A"}}, "already exists"),
        ({"add_alternative_codes": {"x": "Z"}}, "not a primary code"),
        ({"add_children": {"Z": [["A"]]}}, "not a primary code"),
        ({"add_children": {"A": [["Z"]]}}, "don't exist"),
        ({"update_categories": {"Z": {"title": "y"}}}, "not a primary code"),
        (
            {"remove_categories": climate_categories.CategoryRemoval(codes=("Z",))},
            "not a primary code",
        ),
        (
            {"remove_categories": climate_categories.CategoryRemoval(codes=("T",))},
            "canonical top level",
        ),
        ({"merge_into": {"Z": "B"}}, "not a primary code"),
        ({"merge_into": {"C": "Z"}}, "not a primary code"),
        ({"merge_into": {"C": "C"}}, "removed itself"),
        ({"merge_into": {"C": "B", "B": "A"}}, "removed itself"),
        (
            {
                "merge_into": {"C": "B"},
                "remove_categories": climate_categories.CategoryRemoval(codes=("B",)),
            },
            "removed itself",
        ),
        (
            {
                "merge_into": {"C": "B"},
                "remove_categories": climate_categories.CategoryRemoval(codes=("C",)),
            },
            "also merges it",
        ),
        ({"merge_into": {"T": "A"}}, "canonical top level"),
        ({"split_from": {"Z": "B"}}, "not a primary code"),
        ({"split_from": {"C": "Z"}}, "not a primary code"),
        ({"split_from": {"C": "C"}}, "from itself"),
        ({"split_from": {"C": "B"}, "merge_into": {"B": "A"}}, "is removed"),
        (
            {
                "split_from": {"C": "B"},
                "remove_categories": climate_categories.CategoryRemoval(codes=("C",)),
            },
            "is removed",
        ),
        ({"split_from": {"T": "A"}}, "canonical top level"),
        ({"join_parents": {"C": ["T"]}}, "not split by split_from"),
        ({"remove_alternative_codes": {"x": "Z"}}, "not a primary code"),
        ({"remove_alternative_codes": {"x": "A"}}, "not an alternative code"),
        ({"remove_children": {"Z": [["A"]]}}, "not a primary code"),
        ({"remove_children": {"T": [["A", "B"]]}}, "no such child set"),
        ({"remove_children": {"A": [["B"]]}}, "no such child set"),
    ],
)
def test_invalid_patches(fam, option_kwargs, match):
    option = CategorizationOption(
        name="broken",
        title="broken",
        last_update=datetime.date(2026, 1, 1),
        **option_kwargs,
    )
    family = OptionFamily(
        base=fam,
        manifest=OptionManifest(base="Fam", options=("broken",)),
        options={"broken": option},
    )
    if match is None:
        family.build(["broken"])
    else:
        with pytest.raises(ValueError, match=match):
            family.build(["broken"])


def test_removal_non_total_sum():
    # without total_sum, removed categories are just dropped from child sets, and
    # emptied child sets are dropped
    hier = climate_categories.from_yaml(DATA_DIR / "hierarchical_categorization.yaml")
    assert not hier.total_sum
    option = CategorizationOption(
        name="no_3",
        title="without 3",
        last_update=datetime.date(2026, 1, 1),
        remove_categories=climate_categories.CategoryRemoval(codes=("3",)),
    )
    family = OptionFamily(
        base=hier,
        manifest=OptionManifest(base="HierCat", options=("no_3",)),
        options={"no_3": option},
    )
    cat = family.build(["no_3"])
    assert children(cat, "0") == [{"1", "2"}, {"0X3"}, {"1A", "1B", "2"}]
    assert children(hier, "0") == [
        {"1", "2", "3"},
        {"0X3", "3"},
        {"1A", "1B", "2", "3"},
    ]


def test_merge_into_set_without_target(fam):
    # with total_sum, child sets which contain the merged category, but not the
    # category it is merged into, don't add up any more and are dropped
    c_in_a = CategorizationOption(
        name="c_in_a",
        title="C included in A",
        last_update=datetime.date(2026, 1, 1),
        add_children={"T": [["B", "C", "A"]]},
        merge_into={"C": "A"},
    )
    b_set = CategorizationOption(
        name="b_set",
        title="A and C as a child set of B",
        last_update=datetime.date(2026, 1, 1),
        add_categories={"BC": {"title": "B and C", "children": [["B", "C"]]}},
    )
    family = OptionFamily(
        base=fam,
        manifest=OptionManifest(base="Fam", options=("b_set", "c_in_a")),
        options={"b_set": b_set, "c_in_a": c_in_a},
    )
    cat = family.build(["b_set", "c_in_a"])
    assert children(cat, "T") == [{"A", "B"}]
    assert "BC" in cat
    assert not cat["BC"].children
    assert cat["A"].info == {"size": "big", "includes": ["C"]}


def test_merge_into_non_total_sum():
    # without total_sum, merged categories are just dropped from child sets
    hier = climate_categories.from_yaml(DATA_DIR / "hierarchical_categorization.yaml")
    option = CategorizationOption(
        name="3_in_1",
        title="3 included in 1",
        last_update=datetime.date(2026, 1, 1),
        merge_into={"3": "1"},
    )
    family = OptionFamily(
        base=hier,
        manifest=OptionManifest(base="HierCat", options=("3_in_1",)),
        options={"3_in_1": option},
    )
    cat = family.build(["3_in_1"])
    assert children(cat, "0") == [{"1", "2"}, {"0X3"}, {"1A", "1B", "2"}]
    assert cat["1"].info["includes"] == ["3"]


def test_merge_into_transitive(fam):
    # categories merged into a category which is merged itself are included in the
    # final target, too
    a_in_b = CategorizationOption(
        name="a_in_b",
        title="A included in B",
        last_update=datetime.date(2026, 1, 1),
        merge_into={"A": "B"},
    )
    c_in_b = fam.available_options["c_in_b"]
    b_in_x = CategorizationOption(
        name="b_in_x",
        title="B included in X",
        last_update=datetime.date(2026, 1, 1),
        add_categories={"X": {"title": "Category X"}},
        add_children={"T": [["X"]]},
        merge_into={"B": "X"},
    )
    family = OptionFamily(
        base=fam,
        manifest=OptionManifest(base="Fam", options=("a_in_b", "c_in_b", "b_in_x")),
        options={"a_in_b": a_in_b, "c_in_b": c_in_b, "b_in_x": b_in_x},
    )
    cat = family.build(["a_in_b", "c_in_b", "b_in_x"])
    assert set(cat.keys()) == {"T", "X"}
    assert cat["X"].info == {"includes": ["A", "B", "C"]}
    assert children(cat, "T") == [{"X"}]


def test_merge_into_added_category(fam):
    # a data source which only reports the sum of B and C
    bc = CategorizationOption(
        name="bc",
        title="B and C together",
        last_update=datetime.date(2026, 1, 1),
        add_categories={"BC": {"title": "Categories B and C"}},
        add_children={"T": [["A", "BC"]]},
        merge_into={"B": "BC", "C": "BC"},
    )
    family = OptionFamily(
        base=fam,
        manifest=OptionManifest(base="Fam", options=("bc",)),
        options={"bc": bc},
    )
    cat = family.build(["bc"])
    assert set(cat.keys()) == {"T", "A", "BC"}
    assert cat["BC"].info == {"includes": ["B", "C"]}
    assert children(cat, "T") == [{"A", "BC"}]
    assert cat.total_sum


def build_option(base, **kwargs):
    """Build the base with an option with the given patch."""
    option = CategorizationOption(
        name="opt", title="opt", last_update=datetime.date(2026, 1, 1), **kwargs
    )
    family = OptionFamily(
        base=base,
        manifest=OptionManifest(base=base.name, options=("opt",)),
        options={"opt": option},
    )
    return family.build(["opt"])


def test_update_categories(fam):
    cat = build_option(
        fam,
        update_categories={
            "A": {"title": "New A", "comment": "Changed.", "info": {"colour": "red"}},
            "B": {"comment": "Only the comment."},
        },
    )
    assert cat["A"].title == "New A"
    assert cat["A"].comment == "Changed."
    assert cat["A"].info == {"size": "big", "colour": "red"}
    assert cat["B"].title == "Category B"
    assert cat["B"].comment == "Only the comment."
    assert cat["A"] == fam["A"]
    assert fam["A"].title == "Category A"


def test_remove_alternative_codes(fam):
    with_ab = build_option(
        fam,
        add_categories={
            "AB": {"title": "A and B", "alternative_codes": ["A+B", "AplusB"]}
        },
        add_children={"T": [["A+B", "C"]]},
    )
    cat = with_ab.apply(
        CategorizationOption(
            name="no_plus",
            title="no plus",
            last_update=datetime.date(2026, 1, 1),
            remove_alternative_codes={"A+B": "AB"},
        )
    )
    assert "A+B" not in cat
    assert cat["AB"].codes == ("AB", "AplusB")
    # child sets use the primary code instead of the removed alternative code
    assert children(cat, "T") == [{"A", "B", "C"}, {"AB", "C"}]

    # alternative codes can be moved to another category
    moved = build_option(
        fam,
        add_alternative_codes={"a": "A", "x": "B"},
    ).apply(
        CategorizationOption(
            name="move",
            title="move",
            last_update=datetime.date(2026, 1, 1),
            remove_alternative_codes={"x": "B"},
            add_alternative_codes={"x": "C"},
        )
    )
    assert moved["x"] == moved["C"]
    assert moved["B"].codes == ("B",)


def test_remove_children(fam):
    # replace a child set, matched regardless of order and with alternative codes
    cat = build_option(
        fam,
        add_alternative_codes={"c": "C"},
        remove_children={"T": [["c", "A", "B"]]},
        add_children={"T": [["A", "BC"]]},
        add_categories={"BC": {"title": "B and C", "children": [["B", "C"]]}},
    )
    assert children(cat, "T") == [{"A", "BC"}]
    # removing the last child set removes the children
    cat = build_option(fam, remove_children={"T": [["A", "B", "C"]]})
    assert not cat["T"].children
    assert cat.level("T") == 1


def test_remove_children_combination(fam):
    # combinations can remove child sets which options added
    family = make_family(
        fam,
        combinations=(
            OptionCombination(
                options=("extra", "more"),
                remove_children={"T": [["AB", "C"]]},
            ),
        ),
    )
    assert children(family.build(["extra"]), "T") == [{"A", "B", "C"}, {"AB", "C"}]
    assert children(family.build(["extra", "more"]), "T") == [{"A", "B", "C"}]


def test_round_trip_new_patch_keys(tmp_path):
    option = CategorizationOption(
        name="all",
        title="all keys",
        last_update=datetime.date(2026, 1, 1),
        update_categories={"A": {"title": "x", "comment": "y", "info": {"z": "1"}}},
        remove_alternative_codes={"a": "A"},
        remove_children={"T": [["A", "B"]]},
        split_from={"D": "B"},
        join_parents={"D": ["T"]},
    )
    assert CategorizationOption.from_spec(option.to_spec()) == option
    option.to_yaml(tmp_path / "all.yaml")
    assert CategorizationOption.from_yaml(tmp_path / "all.yaml") == option


def test_merge_into_new_category(fam):
    # a receiving category which is not a member of any child set yet takes over the
    # memberships of the categories merged into it, if all of them are members
    cat = build_option(
        fam,
        add_categories={"BC": {"title": "B and C"}},
        merge_into={"B": "BC", "C": "BC"},
    )
    assert children(cat, "T") == [{"A", "BC"}]
    assert cat["BC"].info == {"includes": ["B", "C"]}
    assert cat.total_sum

    # child sets which only contain some of the merged categories don't add up
    extra = fam.with_options(["extra"])
    cat = build_option(
        extra,
        add_categories={"BC": {"title": "B and C"}},
        merge_into={"B": "BC", "C": "BC"},
    )
    assert children(cat, "T") == [{"A", "BC"}]
    assert not cat["AB"].children


def test_merge_into_new_category_non_total_sum():
    hier = climate_categories.from_yaml(DATA_DIR / "hierarchical_categorization.yaml")
    cat = build_option(
        hier,
        add_categories={"12": {"title": "Categories 1 and 2"}},
        merge_into={"1": "12", "2": "12"},
    )
    assert children(cat, "0") == [{"12", "3"}, {"0X3", "3"}, {"1A", "1B", "3"}]


def test_join_parents():
    # without total_sum, split categories only join the given parents
    hier = climate_categories.from_yaml(DATA_DIR / "hierarchical_categorization.yaml")
    option = {
        "add_categories": {"4": {"title": "Category 4"}},
        "split_from": {"4": "1"},
    }
    assert children(build_option(hier, **option), "0") == children(hier, "0")
    cat = build_option(hier, **option, join_parents={"4": ["TOTAL", "missing"]})
    assert children(cat, "0") == [
        {"1", "2", "3", "4"},
        {"0X3", "3"},
        {"1A", "1B", "2", "3"},
    ]
    assert "4 (Category 4) is split from 1 (Category 1)." in cat["0"].comment
    assert cat["1"].info["excludes"] == ["4"]


def split_d_from_b() -> CategorizationOption:
    return CategorizationOption(
        name="d_from_b",
        title="D split from B",
        last_update=datetime.date(2026, 1, 1),
        add_categories={"D": {"title": "Category D"}},
        split_from={"D": "B"},
    )


def test_split_from(fam):
    option = split_d_from_b()
    assert CategorizationOption.from_spec(option.to_spec()) == option
    family = OptionFamily(
        base=fam,
        manifest=OptionManifest(base="Fam", options=("d_from_b",)),
        options={"d_from_b": option},
    )
    cat = family.build(["d_from_b"])
    assert children(cat, "T") == [{"A", "B", "C", "D"}]
    assert cat["B"].info == {"excludes": ["D"]}
    assert cat["B"].comment == "Excludes D (Category D)."
    assert cat["T"].comment == "D (Category D) is split from B (Category B)."
    assert cat.total_sum
    assert "excludes" not in fam["B"].info


def test_split_from_ancestors(fam):
    # child sets which only contain an ancestor of the category D is split from still
    # add up, because the ancestor gets D, too
    family = OptionFamily(
        base=fam,
        manifest=OptionManifest(base="Fam", options=("extra", "d_from_b")),
        options={
            "extra": fam.available_options["extra"],
            "d_from_b": split_d_from_b(),
        },
    )
    cat = family.build(["extra", "d_from_b"])
    assert children(cat, "T") == [{"A", "B", "C", "D"}, {"AB", "C"}]
    assert children(cat, "AB") == [{"A", "B", "D"}]


def test_split_from_non_total_sum():
    # without total_sum, child sets are memberships and are not changed
    hier = climate_categories.from_yaml(DATA_DIR / "hierarchical_categorization.yaml")
    option = CategorizationOption(
        name="4_from_1",
        title="4 split from 1",
        last_update=datetime.date(2026, 1, 1),
        add_categories={"4": {"title": "Category 4"}},
        split_from={"4": "1"},
    )
    family = OptionFamily(
        base=hier,
        manifest=OptionManifest(base="HierCat", options=("4_from_1",)),
        options={"4_from_1": option},
    )
    cat = family.build(["4_from_1"])
    assert children(cat, "0") == children(hier, "0")
    assert cat["1"].info["excludes"] == ["4"]


def test_split_then_merge_cancels(fam):
    # merging a category back into the category it was split from cancels the split
    d_in_b = CategorizationOption(
        name="d_in_b",
        title="D included in B",
        last_update=datetime.date(2026, 1, 1),
        merge_into={"D": "B"},
    )
    family = OptionFamily(
        base=fam,
        manifest=OptionManifest(base="Fam", options=("d_from_b", "d_in_b")),
        options={"d_from_b": split_d_from_b(), "d_in_b": d_in_b},
    )
    cat = family.build(["d_from_b", "d_in_b"])
    assert "D" not in cat
    assert cat["B"].info == {}
    assert children(cat, "T") == [{"A", "B", "C"}]


def shipped_combinations() -> list:
    return [
        pytest.param(family, options, id=f"{family.name}{list(options)}")
        for family in climate_categories.cats.families.values()
        for options in family.supported_combinations
    ]


@pytest.mark.parametrize(("family", "options"), shipped_combinations())
def test_shipped_supported_combinations(family, options):
    """Every supported combination of the included categorizations can be built and
    is consistent."""
    cat = family.get(options)
    assert cat.canonical_name == climate_categories.canonical_name(family.name, options)
    assert cat.family == family.name
    if cat.hierarchical and family.base.canonical_top_level_category is not None:
        assert cat.canonical_top_level_category is not None
        assert cat.level(cat.canonical_top_level_category) == 1
    # every category of the base is still there, unless an option removes it
    removed = {
        code
        for option in options
        if family.options[option].remove_categories is not None
        for code in family.options[option].remove_categories.codes
    } | {code for option in options for code in family.options[option].merge_into}
    assert set(family.base.keys()) - removed <= set(cat.keys())


def test_shipped_aliases():
    for family in climate_categories.cats.families.values():
        for alias, options in family.aliases.items():
            assert family.is_supported(options)
            cat = climate_categories.cats[alias]
            assert cat.name == alias
            assert cat.enabled_options == options


def test_yaml_without_trailing_whitespace(tmp_path, fam):
    # long comments are folded, which must not leave trailing whitespace
    cat = fam.with_options(["extra", "no_c"])
    cat.comment = "A long comment which has to be folded. " * 10
    cat.to_yaml(tmp_path / "cat.yaml")
    option = climate_categories.ISO3.available_options["pse_in_isr"]
    option.to_yaml(tmp_path / "option.yaml")
    for path in (tmp_path / "cat.yaml", tmp_path / "option.yaml"):
        lines = path.read_text().splitlines()
        assert len(lines) > 5
        assert all(line == line.rstrip() for line in lines)
    assert climate_categories.from_yaml(tmp_path / "cat.yaml").comment == cat.comment
    assert CategorizationOption.from_yaml(tmp_path / "option.yaml") == option


EXTENSION = """\
option: mygroups
base: {base}
title: my groups
comment: Groups used in my dataset.
references: doi:00000/00002
last_update: 2026-10-01
add_categories:
  MYGROUP:
    title: My group
    children:
      - - {child1}
        - {child2}
"""


def test_apply(fam):
    option = CategorizationOption(
        name="ext",
        title="my extension",
        references="doi:00000/00002",
        last_update=datetime.date(2026, 10, 1),
        add_categories={"BC": {"title": "B and C", "children": [["B", "C"]]}},
    )
    cat = fam.apply(option)
    assert cat.name == "Fam_ext"
    assert cat.canonical_name == "Fam_ext"
    assert cat.family == "Fam"
    assert cat.enabled_options == ("ext",)
    assert children(cat, "BC") == [{"B", "C"}]
    assert cat.title == "Family with my extension"
    assert cat.references == "doi:00000/00000;\ndoi:00000/00002"
    assert cat.last_update == datetime.date(2026, 10, 1)
    assert "BC" not in fam
    # categories are comparable to the categories of the original categorization
    assert cat["A"] == fam["A"]
    assert hash(cat["A"]) == hash(fam["A"])
    assert cat["A"] in {fam["A"]}

    assert fam.apply(option, name="Mine").name == "Mine"


def test_apply_file(tmp_path, fam):
    path = tmp_path / "ext.yaml"
    path.write_text(EXTENSION.format(base="Fam", child1="A", child2="C"))
    for option in (path, str(path)):
        cat = fam.apply(option)
        assert cat.name == "Fam_mygroups"
        assert children(cat, "MYGROUP") == [{"A", "C"}]

    # the base is kept when writing the option
    option = CategorizationOption.from_yaml(path)
    assert option.base == "Fam"
    option.to_yaml(tmp_path / "written.yaml")
    assert CategorizationOption.from_yaml(tmp_path / "written.yaml") == option


def test_apply_requires_conflicts(fam):
    needs_extra = CategorizationOption(
        name="ext",
        title="x",
        last_update=datetime.date(2026, 1, 1),
        requires=("extra",),
        add_categories={"ABx": {"title": "AB again", "children": [["AB"]]}},
    )
    with pytest.raises(ValueError, match="requires the options \\['extra'\\]"):
        fam.apply(needs_extra)
    cat = fam.with_options(["extra"]).apply(needs_extra)
    assert cat.name == "Fam[extra]_ext"
    assert cat["AB"] == fam.with_options(["extra"])["AB"]

    no_no_c = CategorizationOption(
        name="ext",
        title="x",
        last_update=datetime.date(2026, 1, 1),
        conflicts=("no_c",),
    )
    with pytest.raises(ValueError, match="conflicts with the options \\['no_c'\\]"):
        fam.with_options(["no_c"]).apply(no_no_c)


def test_apply_chain(fam):
    # applied options count as enabled for options applied later
    ext1 = CategorizationOption(
        name="ext1",
        title="x",
        last_update=datetime.date(2026, 1, 1),
        add_categories={"X": {"title": "X"}},
    )
    ext2 = CategorizationOption(
        name="ext2",
        title="y",
        last_update=datetime.date(2026, 1, 1),
        requires=("extra", "ext1"),
        add_categories={"Y": {"title": "Y", "children": [["X", "AB"]]}},
    )
    cat = fam.with_options(["extra"]).apply(ext1)
    assert cat.enabled_options == ("ext1", "extra")
    chained = cat.apply(ext2)
    assert chained.name == "Fam[extra]_ext1_ext2"
    assert chained.canonical_name == "Fam[extra]_ext1_ext2"
    assert chained.enabled_options == ("ext1", "ext2", "extra")
    assert children(chained, "Y") == [{"X", "AB"}]

    no_ext1 = CategorizationOption(
        name="no_ext1",
        title="z",
        last_update=datetime.date(2026, 1, 1),
        conflicts=("ext1",),
    )
    with pytest.raises(ValueError, match="conflicts with the options \\['ext1'\\]"):
        cat.apply(no_ext1)
    with pytest.raises(ValueError, match="already enabled"):
        cat.apply(ext1)
    with pytest.raises(ValueError, match="already enabled"):
        fam.with_options(["extra"]).apply(fam.available_options["extra"])


def test_apply_removal(fam):
    cat = fam.with_options(["extra"]).apply(fam.available_options["c_in_b"])
    assert "C" not in cat
    assert children(cat, "T") == [{"A", "B"}, {"AB"}]
    assert cat.total_sum


def test_load_extension(tmp_path, cats):
    path = tmp_path / "ext.yaml"
    path.write_text(EXTENSION.format(base="FAM_FULL", child1="ABC", child2="A"))
    cat = climate_categories.load_extension(path, cats)
    assert cat.name == "FAM_FULL_mygroups"
    assert cat.canonical_name == "FAM_FULL_mygroups"
    assert cat.family == "Fam"
    assert children(cat, "MYGROUP") == [{"ABC", "A"}]
    # comparable with the whole family, not only with the alias it was applied to
    assert cat["A"] == cats["Fam"]["A"]
    assert cat["A"] == cats["Fam[extra]"]["A"]
    # extensions are not registered
    assert "FAM_FULL_mygroups" not in cats
    assert climate_categories.load_extension(path, cats, name="Mine").name == "Mine"


def test_load_extension_without_base(tmp_path, cats):
    path = tmp_path / "ext.yaml"
    path.write_text(
        EXTENSION.format(base="Fam", child1="A", child2="B").replace("base: Fam\n", "")
    )
    with pytest.raises(ValueError, match="'base' field"):
        climate_categories.load_extension(path, cats)


SECOND_EXTENSION = """\
option: second
base: {base}
title: my second groups
last_update: 2026-10-02
requires:
  - extra
  - mygroups
add_categories:
  MYSECONDGROUP:
    title: My second group
    children:
      - - MYGROUP
        - AB
"""


def test_load_extension_multiple(tmp_path, cats):
    first = tmp_path / "first.yaml"
    first.write_text(EXTENSION.format(base="FAM_FULL", child1="ABC", child2="A"))
    second = tmp_path / "second.yaml"
    second.write_text(SECOND_EXTENSION.format(base="FAM_FULL"))

    # the second extension requires the first
    with pytest.raises(ValueError, match="requires the options \\['mygroups'\\]"):
        climate_categories.load_extension(second, cats)

    cat = climate_categories.load_extension([first, second], cats)
    assert cat.name == "FAM_FULL_mygroups_second"
    assert cat.enabled_options == ("extra", "more", "mygroups", "second")
    assert children(cat, "MYSECONDGROUP") == [{"MYGROUP", "AB"}]
    assert cat["A"] == cats["Fam"]["A"]

    named = climate_categories.load_extension((first, second), cats, name="Mine")
    assert named.name == "Mine"

    other = tmp_path / "other.yaml"
    other.write_text(SECOND_EXTENSION.format(base="Fam[extra]"))
    with pytest.raises(ValueError, match="same 'base'"):
        climate_categories.load_extension([first, other], cats)
    with pytest.raises(ValueError, match="No option files"):
        climate_categories.load_extension([], cats)


def test_load_extension_included(tmp_path):
    # applying an extension to a categorization included in climate_categories
    path = tmp_path / "ext.yaml"
    path.write_text(EXTENSION.format(base="ISO3_PRIMAP", child1="DEU", child2="EU"))
    cat = climate_categories.load_extension(path)
    assert cat.name == "ISO3_PRIMAP_mygroups"
    assert cat["MYGROUP"].children == [
        {climate_categories.ISO3["DEU"], climate_categories.ISO3_PRIMAP["EU"]}
    ]
    assert "PSE" not in cat
    assert cat["DEU"] == climate_categories.ISO3["DEU"]
    assert hash(cat["DEU"]) == hash(climate_categories.ISO3["DEU"])
    assert "ISO3_PRIMAP_mygroups" not in climate_categories.cats


def test_extended_categories_hash():
    # categories of extended categorizations are equal and have the same hash
    ipcc = climate_categories.IPCC2006
    primap = climate_categories.IPCC2006_PRIMAP
    assert primap["1.A"] == ipcc["1.A"]
    assert hash(primap["1.A"]) == hash(ipcc["1.A"])
