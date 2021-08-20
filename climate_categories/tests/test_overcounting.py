import pytest

import climate_categories
import climate_categories._conversions as conversions
import climate_categories.tests
import climate_categories.tests.data


@pytest.fixture
def simple_conversion_specs():
    cat_a = {
        "name": "A",
        "title": "Categorization A",
        "canonical_top_level_category": "0",
        "hierarchical": True,
        "last_update": "2021-07-29",
        "comment": "The first categorization",
        "references": "ask mika",
        "institution": "PIK",
        "total_sum": True,
        "categories": {
            "0": {"title": "total", "children": [["1", "2"]]},
            "1": {"title": "one", "children": [["1.A", "1.B"]]},
            "2": {"title": "two", "children": [["2.A", "2.B"]]},
            "1.A": {"title": "one-A"},
            "1.B": {"title": "one-B"},
            "2.A": {"title": "two-A", "children": [["2.A.1"]]},
            "2.B": {"title": "two-B"},
            "2.A.1": {"title": "two-A-one"},
        },
    }
    cat_b = {
        "name": "B",
        "title": "Categorization B",
        "canonical_top_level_category": "0",
        "hierarchical": True,
        "last_update": "2021-07-29",
        "comment": "The second categorization",
        "references": "ask mika",
        "institution": "PIK",
        "total_sum": True,
        "categories": {
            "0": {"title": "total", "children": [["1", "2"]]},
            "1": {"title": "one", "children": [["1.A", "1.B"]]},
            "2": {"title": "two", "children": [["2.A"]]},
            "1.A": {"title": "one-A"},
            "1.B": {"title": "one-B"},
            "2.A": {"title": "two-A", "children": [["2.A.1", "2.A.2"]]},
            "2.A.1": {"title": "two-A-one", "children": [["2.A.1.a"]]},
            "2.A.2": {"title": "two-A-two"},
            "2.A.1.a": {"title": "two-A-one-a"},
        },
    }
    convs = [
        ["0", "0", "total"],
        ["1", "1"],
        ["1.A", "1.A"],
        ["1.B", "1.B"],
        ["2", "2"],
        ["2.A + 2.B", "2.A"],
        ["2.A", "2.A.1"],
        ["2.A.1", "2.A.1.a"],
        ["2.B", "2.A.2"],
    ]
    return cat_a, cat_b, convs


def specs_to_conversion(cat_a_spec, cat_b_spec, convs_spec) -> conversions.Conversion:
    cat_a = climate_categories.HierarchicalCategorization.from_spec(cat_a_spec)
    cat_b = climate_categories.HierarchicalCategorization.from_spec(cat_b_spec)
    return conversions.Conversion(
        categorization_a=cat_a,
        categorization_b=cat_b,
        rules=[
            conversions.ConversionRuleSpec.from_csv_row(
                iter(row), aux_names=[]
            ).hydrate(
                categorization_a=cat_a,
                categorization_b=cat_b,
                cats=climate_categories.cats,
            )
            for row in convs_spec
        ],
    )


def test_no_over_counting(simple_conversion_specs):
    conv = specs_to_conversion(*simple_conversion_specs)
    assert not conv.find_over_counting_problems()
    assert not conv.reversed().find_over_counting_problems()


def test_simple_over_counting(simple_conversion_specs):
    cat_a, cat_b, convs = simple_conversion_specs
    convs.append(["2", "1"])
    conv = specs_to_conversion(cat_a, cat_b, convs)
    problems = conv.find_over_counting_problems()
    problematic_categories = [problem.category for problem in problems]
    assert conv.categorization_a["2"] in problematic_categories
    assert conv.categorization_a["2.A"] in problematic_categories
    assert conv.categorization_a["2.A.1"] in problematic_categories
    assert conv.categorization_a["2.B"] in problematic_categories

    assert conv.categorization_b["1"] in problematic_categories
    assert conv.categorization_b["1.A"] in problematic_categories
    assert conv.categorization_b["1.B"] in problematic_categories
    assert len(problems) == 7


def test_over_counting_aux(simple_conversion_specs):
    cat_a_spec, cat_b_spec, convs_spec = simple_conversion_specs
    convs_spec.append(["2", "1"])
    for c in convs_spec:
        c.insert(1, "")
    cat_a = climate_categories.HierarchicalCategorization.from_spec(cat_a_spec)
    cat_b = climate_categories.HierarchicalCategorization.from_spec(cat_b_spec)
    conv = conversions.Conversion(
        categorization_a=cat_a,
        categorization_b=cat_b,
        rules=[
            conversions.ConversionRuleSpec.from_csv_row(
                iter(row), aux_names=["gas"]
            ).hydrate(
                categorization_a=cat_a,
                categorization_b=cat_b,
                cats=climate_categories.cats,
            )
            for row in convs_spec
        ],
    )

    problems = conv.find_over_counting_problems()
    problematic_categories = [problem.category for problem in problems]
    assert conv.categorization_a["2"] in problematic_categories
    assert conv.categorization_a["2.A"] in problematic_categories
    assert conv.categorization_a["2.A.1"] in problematic_categories
    assert conv.categorization_a["2.B"] in problematic_categories

    assert conv.categorization_b["1"] in problematic_categories
    assert conv.categorization_b["1.A"] in problematic_categories
    assert conv.categorization_b["1.B"] in problematic_categories
    assert len(problems) == 7


def test_sum_over_counting(simple_conversion_specs):
    cat_a, cat_b, convs = simple_conversion_specs
    cat_b["categories"]["1.C"] = {"title": "one-C"}
    cat_b["categories"]["1"]["children"][0].append("1.C")
    convs.append(["1.A + 1.B", "1.C"])
    conv = specs_to_conversion(cat_a, cat_b, convs)
    problems = conv.find_over_counting_problems()
    problematic_categories = [problem.category for problem in problems]
    assert len(problems) == 2
    assert conv.categorization_a["1.A"] in problematic_categories
    assert conv.categorization_a["1.B"] in problematic_categories


def test_sum_no_over_counting(simple_conversion_specs):
    cat_a, cat_b, convs = simple_conversion_specs
    convs.append(["1.A + 1.B", "1"])
    conv = specs_to_conversion(cat_a, cat_b, convs)
    problems = conv.find_over_counting_problems()
    assert not problems


def test_not_hierarchical(simple_conversion_specs):
    cat_a_spec, cat_b_spec, convs_spec = simple_conversion_specs
    for cat in cat_a_spec["categories"].values():
        try:
            del cat["children"]
        except KeyError:
            pass
    for cat in cat_b_spec["categories"].values():
        try:
            del cat["children"]
        except KeyError:
            pass
    cat_a_spec["hierarchical"] = False
    cat_b_spec["hierarchical"] = False

    cat_a = climate_categories.Categorization.from_spec(cat_a_spec)
    cat_b = climate_categories.Categorization.from_spec(cat_b_spec)

    conv = conversions.Conversion(
        categorization_a=cat_a,
        categorization_b=cat_b,
        rules=[
            conversions.ConversionRuleSpec.from_csv_row(
                iter(row), aux_names=[]
            ).hydrate(
                categorization_a=cat_a,
                categorization_b=cat_b,
                cats=climate_categories.cats,
            )
            for row in convs_spec
        ],
    )

    with pytest.raises(ValueError, match="is not hierarchical"):
        conv.find_over_counting_problems()


def test_not_total_sum(simple_conversion_specs):
    cat_a_spec, cat_b_spec, convs_spec = simple_conversion_specs
    cat_a_spec["total_sum"] = False
    conv = specs_to_conversion(
        cat_a_spec=cat_a_spec, cat_b_spec=cat_b_spec, convs_spec=convs_spec
    )
    with pytest.raises(
        ValueError,
        match="it is not specified that the sum of a set of children equals the parent",
    ):
        conv.find_over_counting_problems()
