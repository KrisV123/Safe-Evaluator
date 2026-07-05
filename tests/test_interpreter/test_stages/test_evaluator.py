import pytest

from evaluator.pipelines import evaluate
from evaluator.types import atom_types

@pytest.mark.parametrize(
    "expr, vars",
    [
        # binary
        pytest.param("variable + other", {"variable": 5, "other": 2}, id="add"),
        pytest.param("5 + 2", {}, id="add_without_vars"),
        pytest.param("variable - other", {"variable": 5, "other": 2}, id="sub"),
        pytest.param("variable * other", {"variable": 5, "other": 2}, id="mul"),
        pytest.param("variable / other", {"variable": 5, "other": 2}, id="truediv"),
        pytest.param("variable // other", {"variable": 5, "other": 2}, id="floordiv"),
        pytest.param("variable % other", {"variable": 5, "other": 2}, id="mod"),
        pytest.param("variable ** other", {"variable": 5, "other": 2}, id="pow"),

        pytest.param("variable and other", {"variable": 0, "other": 7}, id="and_false_left"),
        pytest.param("variable and other", {"variable": 5, "other": 7}, id="and_true_left"),
        pytest.param("variable or other", {"variable": 0, "other": 7}, id="or_false_left"),
        pytest.param("variable or other", {"variable": 5, "other": 7}, id="or_true_left"),

        pytest.param("variable in container", {"variable": 2, "container": [1, 2, 3]}, id="in_list_true"),
        pytest.param("2 in [1, 2, 3]", {}, id="in_list_true_without_vars"),
        pytest.param("variable in container", {"variable": 4, "container": [1, 2, 3]}, id="in_list_false"),
        pytest.param("variable in container", {"variable": "a", "container": "cat"}, id="in_str_true"),
        pytest.param("variable in container", {"variable": "z", "container": "cat"}, id="in_str_false"),
        pytest.param("variable not in container", {"variable": 2, "container": [1, 2, 3]}, id="not_in_list_true"),
        pytest.param("variable not in container", {"variable": "z", "container": "cat"}, id="not_in_str_false"),

        pytest.param("a is b", {"a": None, "b": None}, id="is_none"),
        pytest.param("a is b", {"a": [], "b": []}, id="is_list_different"),
        pytest.param("a is b", {"a": (1,), "b": (1,)}, id="is_tuple_equal_but_not_same"),

        # unary
        pytest.param("+variable", {"variable": 5}, id="uplus"),
        pytest.param("-variable", {"variable": 5}, id="uminus"),
        pytest.param("not variable", {"variable": 0}, id="unot_falsey"),
        pytest.param("not variable", {"variable": 5}, id="unot_truthy"),

        # compare
        pytest.param("left < right", {"left": 1, "right": 2}, id="lt"),
        pytest.param("left > right", {"left": 2, "right": 1}, id="gt"),
        pytest.param("left <= right", {"left": 2, "right": 2}, id="lte"),
        pytest.param("left >= right", {"left": 2, "right": 2}, id="gte"),
        pytest.param("left == right", {"left": 2, "right": 2}, id="eq"),
        pytest.param("left != right", {"left": 2, "right": 3}, id="ne"),
        pytest.param("left is right", {"left": None, "right": None}, id="compare_is"),
        pytest.param("left is not right", {"left": None, "right": 1}, id="compare_is_not"),
    ]
)
def test_basic_expressions(expr: str, vars: dict[str, atom_types]):
    assert evaluate(expr, vars) == eval(expr, vars)

@pytest.mark.parametrize(
    "expr, vars",
    [
        pytest.param(
            "(a + b) * c",
            {"a": 2, "b": 3, "c": 4},
            id="arith_nested_add_mul",
        ),
        pytest.param(
            "a + b * c",
            {"a": 2, "b": 3, "c": 4},
            id="arith_precedence_mul_before_add",
        ),
        pytest.param(
            "-(a + b) ** c",
            {"a": 2, "b": 3, "c": 2},
            id="unary_pow_nested",
        ),
        pytest.param(
            "(a + b) / (c - d)",
            {"a": 10, "b": 2, "c": 8, "d": 2},
            id="div_nested_parens",
        ),
        pytest.param(
            "(a > b) and (c < d)",
            {"a": 5, "b": 2, "c": 1, "d": 3},
            id="logic_compare_and_compare",
        ),
        pytest.param(
            "(a > b) or (c < d)",
            {"a": 1, "b": 2, "c": 1, "d": 3},
            id="logic_compare_or_compare",
        ),
        pytest.param(
            "not (a in b)",
            {"a": 4, "b": [1, 2, 3]},
            id="not_membership",
        ),
        pytest.param(
            "(a in b) and (c is d)",
            {"a": 2, "b": [1, 2, 3], "c": None, "d": None},
            id="membership_and_identity",
        ),
        pytest.param(
            "(a + b) < (c * d)",
            {"a": 1, "b": 2, "c": 2, "d": 2},
            id="compare_arith_both_sides",
        ),
        pytest.param(
            "a < b < c",
            {"a": 1, "b": 2, "c": 3},
            id="chained_compare_increasing",
        ),
        pytest.param(
            "a < b > c",
            {"a": 1, "b": 3, "c": 2},
            id="chained_compare_mixed",
        ),
        pytest.param(
            "(a and b) + c",
            {"a": 5, "b": 7, "c": 2},
            id="logic_then_arith",
        ),
        pytest.param(
            "(a or b) * c",
            {"a": 0, "b": 6, "c": 3},
            id="logic_or_then_mul",
        ),
        pytest.param(
            "((a + b) % c) == d",
            {"a": 10, "b": 5, "c": 4, "d": 3},
            id="arith_mod_compare",
        ),
        pytest.param(
            "((10 + 5) % 4) == 3",
            {},
            id="arith_mod_compare_without_vars",
        ),
        pytest.param(
            "(x is y) and (a + b == c)",
            {"x": None, "y": None, "a": 2, "b": 3, "c": 5},
            id="identity_and_eq",
        ),
        pytest.param(
            "((a + b) * c > d) and (e in f or g is h)",
            {"a": 2, "b": 3, "c": 4, "d": 10, "e": 2, "f": [1,2,3], "g": None, "h": None},
            id="deep_logic_mix_1",
        ),
        pytest.param(
            "not ((a * b) < (c + d) or (e and f))",
            {"a": 2, "b": 3, "c": 10, "d": 1, "e": 0, "f": 5},
            id="not_over_complex_or",
        ),
        pytest.param(
            "((a or b) + (c and d)) * e",
            {"a": 0, "b": 5, "c": 3, "d": 4, "e": 2},
            id="logic_inside_arith",
        ),
        pytest.param(
            "(a < b < c) and (d < e > f)",
            {"a": 1, "b": 2, "c": 3, "d": 1, "e": 5, "f": 2},
            id="double_chained_compare",
        ),
        pytest.param(
            "((a + b) ** c % d) == (e * f - g)",
            {"a": 2, "b": 1, "c": 3, "d": 5, "e": 2, "f": 4, "g": 3},
            id="heavy_arith_compare",
        ),
        pytest.param(
            "((2 + 1) ** 3 % 5) == (2 * 4 - 3)",
            {},
            id="heavy_arith_compare_without_vars",
        ),
        pytest.param(
            "(a in b) and not (c in d) or (e is not f)",
            {"a": 1, "b": [1,2], "c": 3, "d": [1,2], "e": None, "f": 1},
            id="membership_not_identity_mix",
        ),
        pytest.param(
            "(((a + b) * c) // d > e) or ((f % g) == h and i)",
            {"a": 2, "b": 3, "c": 4, "d": 2, "e": 5, "f": 10, "g": 3, "h": 1, "i": 7},
            id="very_deep_mixed_1",
        ),
        pytest.param(
            "(not a and b) or (c and not (d or e))",
            {"a": 0, "b": 5, "c": 3, "d": 0, "e": 0},
            id="nested_not_logic",
        ),
        pytest.param(
            "((a < b) and (c < d)) or ((e < f) and (g < h))",
            {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8},
            id="multiple_and_or_blocks",
        ),
        pytest.param(
            "((a + (b * c)) > (d - e)) and ((f in g) or (h is i))",
            {"a": 1, "b": 2, "c": 3, "d": 10, "e": 5, "f": 2, "g": [1,2,3], "h": None, "i": None},
            id="deep_nested_everything",
        )
    ]
)
def test_complex_expressions(expr: str, vars: dict[str, atom_types]):
    assert evaluate(expr, vars) == eval(expr, vars)
