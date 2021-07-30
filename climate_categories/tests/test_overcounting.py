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
            "2.A": {"title": "two-A"},
            "2.B": {"title": "two-B"},
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
            "2": {"title": "two", "children": [["2.A", "2.B"]]},
            "1.A": {"title": "one-A"},
            "1.B": {"title": "one-B"},
            "2.A": {"title": "two-A"},
            "2.B": {"title": "two-B"},
        },
    }
    convs = [
        ["0", "0", "total"],
        ["1", "1"],
        ["1.A", "1.A"],
        ["1.B", "1.B"],
        ["2", "2"],
        ["2.A + 2.B", "2.A"],
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


def test_no_overcounting(simple_conversion_specs):
    conv = specs_to_conversion(*simple_conversion_specs)
    assert not conv.find_over_counting_problems()


def test_simple_overcounting(simple_conversion_specs):
    cat_a, cat_b, convs = simple_conversion_specs
    convs.append(["2", "1"])
    conv = specs_to_conversion(cat_a, cat_b, convs)
    problems = conv.find_over_counting_problems()
    for problem in problems:
        print(problem)
    assert not problems
