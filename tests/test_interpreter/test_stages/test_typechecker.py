import pytest
from types import NoneType

from evaluator.interpreter.stages.lexer import Lexer
from evaluator.interpreter.stages.parser import Parser
from evaluator.interpreter.stages.typechecker import TypeChecker

from evaluator.types import (
    Lexer_type, Parser_tok, Lexer_tok, Value, Collection
)

@pytest.mark.parametrize(
    "expr, typ",
    [
        pytest.param("'awd'", {str}, id="str"),
        pytest.param("5", {int}, id="int"),
        pytest.param("True", {int}, id="bool_True"),
        pytest.param("False", {int}, id="bool_False"),
        pytest.param("5.4", {float}, id="float"),
        pytest.param("None", {NoneType}, id="NonType")
    ]
)
def test_check_value(expr: str, typ: object):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    assert TypeChecker({}).check(ast) == typ

@pytest.mark.parametrize(
    "expr, vars, typ",
    [
        pytest.param("var", {'var': str}, {str}, id="str"),
        pytest.param("var", {'var': int}, {int}, id="int"),
        pytest.param("var", {'var': bool}, {int}, id="bool_True"),
        pytest.param("var", {'var': bool}, {int}, id="bool_False"),
        pytest.param("var", {'var': float}, {float}, id="float"),
        pytest.param("var", {'var': None}, {None}, id="None"),
        pytest.param("var", {'var': type(None)}, {NoneType}, id="NonType")
    ]
)
def test_check_value_identificators(expr: str,
                                    vars: dict[str, type],
                                    typ: object):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    assert TypeChecker(vars).check(ast) == typ

@pytest.mark.parametrize(
    "expr, typ",
    [
        pytest.param("+1", {int}, id="plus_int"),
        pytest.param("+1.0", {float}, id="plus_float"),

        pytest.param("-1", {int}, id="minus_int"),
        pytest.param("-1.0", {float}, id="minus_float"),

        pytest.param("not 1", {int}, id="not_int"),
        pytest.param("not 1.0", {int}, id="not_float"),
        pytest.param("not True", {int}, id="not_bool"),
        pytest.param('not "x"', {int}, id="not_str"),
        pytest.param("not None", {int}, id="not_none"),
        pytest.param("not []", {int}, id="not_list"),
        pytest.param("not (1,)", {int}, id="not_tuple"),
    ],
)
def test_check_unaryop(expr: str, typ: object):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    assert TypeChecker({}).check(ast) == typ

@pytest.mark.parametrize(
    ("expr", "typ"),
    [
        # +
        pytest.param("1 + 1", {int}, id="add_int_int"),
        pytest.param("1 + 1.0", {float}, id="add_int_float"),
        pytest.param("1.0 + 1", {float}, id="add_float_int"),
        pytest.param("1.0 + 1.0", {float}, id="add_float_float"),
        pytest.param('"a" + "b"', {str}, id="add_str_str"),
        pytest.param("[1] + [2]", {list}, id="add_list_list"),

        # -
        pytest.param("1 - 1", {int}, id="sub_int_int"),
        pytest.param("1 - 1.0", {float}, id="sub_int_float"),
        pytest.param("1.0 - 1", {float}, id="sub_float_int"),
        pytest.param("1.0 - 1.0", {float}, id="sub_float_float"),

        # *
        pytest.param("1 * 1", {int}, id="mul_int_int"),
        pytest.param("1 * 1.0", {float}, id="mul_int_float"),
        pytest.param("1.0 * 1", {float}, id="mul_float_int"),
        pytest.param("1.0 * 1.0", {float}, id="mul_float_float"),
        pytest.param('"a" * 3', {str}, id="mul_str_int"),
        pytest.param("[1] * 3", {list}, id="mul_list_int"),

        # /
        pytest.param("1 / 1", {float}, id="div_int_int"),
        pytest.param("1 / 1.0", {float}, id="div_int_float"),
        pytest.param("1.0 / 1", {float}, id="div_float_int"),
        pytest.param("1.0 / 1.0", {float}, id="div_float_float"),

        # //
        pytest.param("1 // 1", {int}, id="floordiv_int_int"),
        pytest.param("1 // 1.0", {float}, id="floordiv_int_float"),
        pytest.param("1.0 // 1", {float}, id="floordiv_float_int"),
        pytest.param("1.0 // 1.0", {float}, id="floordiv_float_float"),

        # %
        pytest.param("1 % 1", {int}, id="mod_int_int"),
        pytest.param("1 % 1.0", {float}, id="mod_int_float"),
        pytest.param("1.0 % 1", {float}, id="mod_float_int"),
        pytest.param("1.0 % 1.0", {float}, id="mod_float_float"),

        # **
        pytest.param("1 ** 1", {int}, id="pow_int_int"),
        pytest.param("1 ** 1.0", {float}, id="pow_int_float"),
        pytest.param("1.0 ** 1", {float}, id="pow_float_int"),
        pytest.param("1.0 ** 1.0", {float}, id="pow_float_float"),

        # and / or
        pytest.param("1 and 2", {int}, id="and-int-int"),
        pytest.param("1 or 2", {int}, id="or-int-int"),

        pytest.param('"a" and "b"', {str}, id="and-str-str"),
        pytest.param('"a" or "b"', {str}, id="or-str-str"),

        pytest.param("None and None", {NoneType}, id="and-none-none"),
        pytest.param("None or None", {NoneType}, id="or-none-none"),

        pytest.param("[1] and [2]", {list}, id="and-list-list"),
        pytest.param("[1] or [2]", {list}, id="or-list-list"),

        pytest.param("(1,) and (2,)", {tuple}, id="and-tuple-tuple"),
        pytest.param("(1,) or (2,)", {tuple}, id="or-tuple-tuple"),

        pytest.param("1 and 1.0", {int, float}, id="and-int-float"),
        pytest.param("1 or 1.0", {int, float}, id="or-int-float"),

        pytest.param("1 and None", {int, NoneType}, id="and-int-none"),
        pytest.param("1 or None", {int, NoneType}, id="or-int-none"),

        pytest.param("None and 1", {int, NoneType}, id="and-none-int"),
        pytest.param("None or 1", {int, NoneType}, id="or-none-int"),

        pytest.param('1 and "a"', {int, str}, id="and-int-str"),
        pytest.param('1 or "a"', {int, str}, id="or-int-str"),

        pytest.param('"a" and 1', {int, str}, id="and-str-int"),
        pytest.param('"a" or 1', {int, str}, id="or-str-int"),

        pytest.param("[1] and 1", {list, int}, id="and-list-int"),
        pytest.param("[1] or 1", {list, int}, id="or-list-int"),

        pytest.param("(1,) and None", {tuple, NoneType}, id="and-tuple-none"),
        pytest.param("(1,) or None", {tuple, NoneType}, id="or-tuple-none"),

        # in
        pytest.param("1 in [1,2]", {int}, id="in_list"),
        pytest.param("1 in (1,2)", {int}, id="in_tuple"),
        pytest.param('"a" in ["a","b"]', {int}, id="in_str_list"),
        pytest.param("[1] in [[1], [2], [3]]", {int}, id="in_list_list"),

        # is
        pytest.param("1 is 1", {int}, id="is_int_int"),
        pytest.param("1 is 1.0", {int}, id="is_int_float"),
        pytest.param("None is None", {int}, id="is_none_none"),
        pytest.param('"a" is "a"', {int}, id="is_str_str"),

        # is not
        pytest.param("1 is not 1", {int}, id="isnot-int-int"),
        pytest.param("1 is not 1.0", {int}, id="isnot-int-float"),
        pytest.param("None is not None", {int}, id="isnot-none-none"),
        pytest.param('"a" is not "a"', {int}, id="isnot-str-str"),
        pytest.param("[1] is not [1]", {int}, id="isnot-list-list"),

        # compare
        pytest.param("1 < 2", {int}, id="compare_int_int"),
        pytest.param("1 < 2.0", {int}, id="compare_int_float"),
        pytest.param("2.0 > 1", {int}, id="compare_float_int"),
        pytest.param("2.0 < 3.0", {int}, id="compare_float_float"),
        pytest.param('"a" < "b"', {int}, id="compare_str_lt"),
        pytest.param('"a" == "b"', {int}, id="compare_str_eq"),
        pytest.param("[1] < [2]", {int}, id="compare_list_simple"),
        pytest.param("[1,2] < [1,3]", {int}, id="compare_list_lexicographic"),
    ]
)
def test_check_binaryop(expr: str, typ: object):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    assert TypeChecker({}).check(ast) == typ

@pytest.mark.parametrize(
    "expr, typ",
    [
        pytest.param("[1,(True and False),[]]", {list}, id="list_sanity"),
        pytest.param("[]", {list}, id="empty_list"),
        pytest.param("(1,(True and False),())", {tuple}, id="tuple_sanity"),
        pytest.param("()", {tuple}, id="empty_tuple")
    ]
)
def test_check_collection(expr: str, typ: object):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    assert TypeChecker({}).check(ast) == typ

@pytest.mark.parametrize(
    "expr, typ",
    [
        pytest.param("6 is 7", {int}, id="is"),
        pytest.param("6 is not 7", {int}, id="is_not"),
        pytest.param("6 < 7", {int}, id="lower"),
        pytest.param("6 <= 7", {int}, id="lower_equal"),
        pytest.param("6 > 7", {int}, id="larger"),
        pytest.param("6 >= 7", {int}, id="larger_equal"),
        pytest.param("6 == 7", {int}, id="equal"),
        pytest.param("6 != 7", {int}, id="not_equal"),
        pytest.param("6 < 7 > 9 == (True and True)", {int}, id="sequence")
    ]
)
def test_comparenode(expr: str, typ: object):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    assert TypeChecker({}).check(ast) == typ

@pytest.mark.parametrize(
    "expr, typ",
    [
        ("not True and False or 6 ** tvoja_mama and -7", {int}),
        ("6 and (7 or 6) and 9", {int}),
        ("tvoja_mama in (6 * 2, -7, 6 <= 2)", {int}),
        ("5 <= 6 and 6 == tvoja_mama", {int}),
        ("True and not not True", {int}),
        ("(True or False) + 5 ** 6.8 ** (not 6.9)", {float}),
        ("6 not in (7,)", {int}),
        ("tvoja_mama is None", {int}),
        ("5 <= 5 and 5 % 5 and 5 in (1,2,)", {int}),
        ("(5 ** 2) + 9.9", {float}),
        ("(1 < 2) and None", {int, NoneType}),
        ("None or (False and None)", {int, NoneType}),
        ("([1,2] + [6,9]) + [6,7]", {list}),
        ("('hello' + ('world' + '!')) or 8.5", {str, float})
    ]
)
def test_combinations(expr: str, typ: object):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    assert TypeChecker({"tvoja_mama": int}).check(ast) == typ

@pytest.mark.parametrize(
    "expr, expect_fail",
    [
        (
            "5 + x * 8",
            TypeChecker.GenericFailure(
                operator=[
                    Lexer_tok(Lexer_type.IDENT, 'x', 4)
                ],
                operands=(
                    Value(
                        token=Parser_tok.Ident,
                        value='x',
                        lexer_tok=Lexer_tok(Lexer_type.IDENT, 'x', 4)
                    ),
                ),
                exception=KeyError('x'))
        ),
        (
            "1 + 'string'",
            TypeChecker.TypeFailure(
                operator=[Lexer_tok(Lexer_type.PLUS, '+', 2)],
                operands=(
                    Value(
                        Parser_tok.Int,
                        value=1,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '1', 0)
                    ),
                Value(
                    Parser_tok.Str,
                    value='string',
                    lexer_tok=Lexer_tok( Lexer_type.STR, "'string'", 4)
                    )
                ),
                types=(int, str)
            )
        ),
        (
            "7 and ([1] + (2,3))",
            TypeChecker.TypeFailure(
                operator=[Lexer_tok(Lexer_type.PLUS, '+', 11)],
                operands=(
                    Collection(
                        token=Parser_tok.List,
                        collection=[
                            Value(
                                token=Parser_tok.Int,
                                value=1,
                                lexer_tok=Lexer_tok(Lexer_type.INT, '1', 8)
                            )
                        ],
                        brackets=(
                            Lexer_tok(Lexer_type.LSQB, '[', 7),
                            Lexer_tok(Lexer_type.RSQB, ']', 9)
                        )
                    ),
                    Collection(
                        token=Parser_tok.Tuple,
                        collection=[
                            Value(
                                token=Parser_tok.Int,
                                value=2,
                                lexer_tok=Lexer_tok(Lexer_type.INT, '2', 14)
                            ),
                            Value(
                                token=Parser_tok.Int,
                                value=3,
                                lexer_tok=Lexer_tok(Lexer_type.INT, '3', 16)
                            )
                        ],
                        brackets=(
                            Lexer_tok(Lexer_type.LPAR, '(', 13),
                            Lexer_tok(Lexer_type.RPAR, ')', 17)
                        )
                    )
                ),
                types=(list, tuple)
            )
        )
    ]
)
def test_Failure(expr: str, expect_fail: TypeChecker.Failure):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    fail = TypeChecker({}).check(ast)

    assert isinstance(fail, TypeChecker.Failure)
    assert fail.operator == expect_fail.operator
    assert fail.operands == expect_fail.operands

    if isinstance(fail, TypeChecker.GenericFailure) and isinstance(expect_fail, TypeChecker.GenericFailure):
        assert fail.exception.args == expect_fail.exception.args
    elif isinstance(fail, TypeChecker.TypeFailure) and isinstance(expect_fail, TypeChecker.TypeFailure):
        assert fail.types == expect_fail.types
    else:
        assert Exception("type is not a Failure object")
