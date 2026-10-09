"""Tests for categorizations with options."""

import datetime
import pathlib

import pytest

import climate_categories
import climate_categories.tests.data
from climate_categories import (
    CategorizationOption,
    CategorizationRegistry,
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


def test_removal_keep_total_sum(fam):
    cat = fam.with_options(["c_in_b"])
    assert "C" not in cat
    assert children(cat, "T") == [{"A", "B"}]
    assert cat["T"].comment == "C is included in B."
    assert cat.total_sum


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
        ({"update_info": {"Z": {"x": "y"}}}, "not a primary code"),
        (
            {"remove_categories": climate_categories.CategoryRemoval(codes=("Z",))},
            "not a primary code",
        ),
        (
            {"remove_categories": climate_categories.CategoryRemoval(codes=("T",))},
            "canonical top level",
        ),
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
    }
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
