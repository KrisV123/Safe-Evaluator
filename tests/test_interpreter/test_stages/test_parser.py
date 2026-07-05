import pytest

from evaluator.interpreter.stages.lexer import Lexer
from evaluator.interpreter.stages.parser import Parser
from evaluator.types import (
    Lexer_type, nodes, Parser_tok,
    Lexer_tok, BinaryOp, UnaryOp, Value, Collection, CompareNode, Constant
)

@pytest.mark.parametrize(
    "expr, expect",
    [
        (
            'True or False',
            BinaryOp(
                token=Parser_tok.Or,
                left_child=Value(
                    Parser_tok.Bool,
                    True,
                    Lexer_tok(Lexer_type.BOOL, 'True', 0)
                ),
                right_child=Value(
                    Parser_tok.Bool,
                    False,
                    Lexer_tok(Lexer_type.BOOL, 'False', 8)
                ),
                lexer_tok=Lexer_tok(Lexer_type.OR, 'or', 5)
            )
        ),
        (
            'True or False or True',
            BinaryOp(
                token=Parser_tok.Or,
                left_child=BinaryOp(
                    token=Parser_tok.Or,
                    left_child=Value(
                        Parser_tok.Bool,
                        True,
                        Lexer_tok(Lexer_type.BOOL, 'True', 0)
                    ),
                    right_child=Value(
                        Parser_tok.Bool,
                        False,
                        Lexer_tok(Lexer_type.BOOL, 'False', 8)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.OR, 'or', 5)
                ),
                right_child=Value(
                    Parser_tok.Bool,
                    True,
                    lexer_tok=Lexer_tok(Lexer_type.BOOL, 'True', 17)
                ),
                lexer_tok=Lexer_tok(Lexer_type.OR, 'or', 14)
            )
        )
    ],
    ids = ['sanity', 'consecutive']
)
def test_disjunction(expr: str, expect: nodes):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    assert Parser(tokens).parse() == expect

@pytest.mark.parametrize(
    "expr, expect",
    [
        (
            'True and False',
            BinaryOp(
                token=Parser_tok.And,
                left_child=Value(
                    Parser_tok.Bool,
                    True,
                    Lexer_tok(Lexer_type.BOOL, 'True', 0)
                ),
                right_child=Value(
                    Parser_tok.Bool,
                    False,
                    Lexer_tok(Lexer_type.BOOL, 'False', 9)
                ),
                lexer_tok=Lexer_tok(Lexer_type.AND, 'and', 5)
            )
        ),
        (
            'True and False and True',
            BinaryOp(
                token=Parser_tok.And,
                left_child=BinaryOp(
                    token=Parser_tok.And,
                    left_child=Value(
                        Parser_tok.Bool,
                        True,
                        Lexer_tok(Lexer_type.BOOL, 'True', 0)
                    ),
                    right_child=Value(
                        Parser_tok.Bool,
                        False,
                        Lexer_tok(Lexer_type.BOOL, 'False', 9)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.AND, 'and', 5)
                ),
                right_child=Value(
                    Parser_tok.Bool,
                    True,
                    Lexer_tok(Lexer_type.BOOL, 'True', 19)
                ),
                lexer_tok=Lexer_tok(Lexer_type.AND, 'and', 15)
            )
        )
    ],
    ids=['sanity', 'consecutive']
)
def test_conjunction(expr: str, expect: nodes):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    assert Parser(tokens).parse() == expect

@pytest.mark.parametrize(
    "expr, expect",
    [
        (
            '5 in [5, 6]',
            CompareNode(
                operators=[
                    (Parser_tok.In, [Lexer_tok(Lexer_type.IN, 'in', 2)])
                ],
                operands=[
                    Value(
                        Parser_tok.Int,
                        5,
                        Lexer_tok(Lexer_type.INT, '5', 0)
                    ),
                    Collection(
                        Parser_tok.List,
                        collection=[
                            Value(
                                Parser_tok.Int,
                                5,
                                Lexer_tok(Lexer_type.INT, '5', 6)
                            ),
                            Value(
                                Parser_tok.Int,
                                6,
                                Lexer_tok(Lexer_type.INT, '6', 9)
                            ),
                        ],
                        brackets=(
                            Lexer_tok(Lexer_type.LSQB, '[', 5),
                            Lexer_tok(Lexer_type.RSQB, ']', 10)
                        )
                    )
                ]
            )
        ),
        (
            '5 not in [5, 6]',
            CompareNode(
                operators=[
                    (Parser_tok.NotIn, [
                        Lexer_tok(Lexer_type.NOT, 'not', 2),
                        Lexer_tok(Lexer_type.IN, 'in', 6)
                    ])
                ],
                operands=[
                    Value(
                        Parser_tok.Int,
                        5,
                        Lexer_tok(Lexer_type.INT, '5', 0)
                    ),
                    Collection(
                        token=Parser_tok.List,
                        collection=[
                            Value(
                                Parser_tok.Int,
                                5,
                                Lexer_tok(Lexer_type.INT, '5', 10)
                            ),
                            Value(
                                Parser_tok.Int,
                                6,
                                Lexer_tok(Lexer_type.INT, '6', 13)
                            )
                        ],
                        brackets=(
                            Lexer_tok(Lexer_type.LSQB, '[', 9),
                            Lexer_tok(Lexer_type.RSQB, ']', 14)
                        )
                    )
                ]
            )
        ),
        (
            '6 == 7',
            CompareNode(
                operators=[
                    (Parser_tok.Eq, [Lexer_tok(Lexer_type.EQ, '==', 2)])],
                operands=[
                    Value(
                        Parser_tok.Int,
                        6,
                        Lexer_tok(Lexer_type.INT, '6', 0)
                    ),
                    Value(
                        Parser_tok.Int,
                        7,
                        Lexer_tok(Lexer_type.INT, '7', 5)
                    )
                ]
            )
        ),
        (
            '6 != 7',
            CompareNode(
                operators=[
                    (Parser_tok.Ne, [Lexer_tok(Lexer_type.NE, '!=', 2)])],
                operands=[
                    Value(
                        Parser_tok.Int,
                        6,
                        Lexer_tok(Lexer_type.INT, '6', 0)
                    ),
                    Value(
                        Parser_tok.Int,
                        7,
                        Lexer_tok(Lexer_type.INT, '7', 5)
                    )
                ]
            )
        ),
        (
            '6 >= 7',
            CompareNode(
                operators=[
                    (Parser_tok.Ge, [Lexer_tok(Lexer_type.GE, '>=', 2)])],
                operands=[
                    Value(
                        Parser_tok.Int,
                        6,
                        Lexer_tok(Lexer_type.INT, '6', 0)
                    ),
                    Value(
                        Parser_tok.Int,
                        7,
                        Lexer_tok(Lexer_type.INT, '7', 5)
                    )
                ]
            )
        ),
        (
            '6 <= 7',
            CompareNode(
                operators=[
                    (Parser_tok.Le, [Lexer_tok(Lexer_type.LE, '<=', 2)])],
                operands=[
                    Value(
                        Parser_tok.Int,
                        6,
                        Lexer_tok(Lexer_type.INT, '6', 0)
                    ),
                    Value(
                        Parser_tok.Int,
                        7,
                        Lexer_tok(Lexer_type.INT, '7', 5)
                    )
                ]
            )
        ),
        (
            '6 > 7',
            CompareNode(
                operators=[
                    (Parser_tok.Gt, [Lexer_tok(Lexer_type.GT, '>', 2)])],
                operands=[
                    Value(
                        Parser_tok.Int,
                        6,
                        Lexer_tok(Lexer_type.INT, '6', 0)
                    ),
                    Value(
                        Parser_tok.Int,
                        7,
                        Lexer_tok(Lexer_type.INT, '7', 4)
                    )
                ]
            )
        ),
        (
            '6 < 7',
            CompareNode(
                operators=[
                    (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, '<', 2)])],
                operands=[
                    Value(
                        Parser_tok.Int,
                        6,
                        Lexer_tok(Lexer_type.INT, '6', 0)
                    ),
                    Value(
                        Parser_tok.Int,
                        7,
                        Lexer_tok(Lexer_type.INT, '7', 4)
                    )
                ]
            )
        ),
        (
            '6 is 7',
            CompareNode(
                operators=[
                    (Parser_tok.Is, [Lexer_tok(Lexer_type.IS, 'is', 2)])],
                operands=[
                    Value(
                        Parser_tok.Int,
                        6,
                        Lexer_tok(Lexer_type.INT, '6', 0)
                    ),
                    Value(
                        Parser_tok.Int,
                        7,
                        Lexer_tok(Lexer_type.INT, '7', 5)
                    )
                ]
            )
        ),
        (
            '6 is not 7',
            CompareNode(
                operators=[
                    (Parser_tok.IsNot, [Lexer_tok(Lexer_type.IS, 'is', 2),
                                        Lexer_tok(Lexer_type.NOT, 'not', 5)])],
                operands=[
                    Value(
                        Parser_tok.Int,
                        6,
                        Lexer_tok(Lexer_type.INT, '6', 0)
                    ),
                    Value(
                        Parser_tok.Int,
                        7,
                        Lexer_tok(Lexer_type.INT, '7', 9)
                    )
                ]
            )
        ),
    ],
    ids=['in', 'not_in', 'equal', 'not_equal', 'large_equal', 'low_equal', 'large', 'low', 'is', 'is_not']
)
def test_compare_operator(expr: str, expect: nodes):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    assert Parser(tokens).parse() == expect

@pytest.mark.parametrize(
    "expr, expect",
    [
        (
            'not True',
            UnaryOp(
                token=Parser_tok.Not,
                child=Value(
                    Parser_tok.Bool,
                    True,
                    Lexer_tok(
                        Lexer_type.BOOL,
                        'True',
                        4
                    )
                ),
                lexer_tok=Lexer_tok(Lexer_type.NOT, 'not', 0)
            )
        ),
        (
            'not not True',
            UnaryOp(
                token=Parser_tok.Not,
                child=UnaryOp(
                    token=Parser_tok.Not,
                    child=Value(
                        Parser_tok.Bool,
                        True,
                        Lexer_tok(
                            Lexer_type.BOOL,
                            'True',
                            8
                        )
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.NOT, 'not', 4)
                ),
                lexer_tok=Lexer_tok(Lexer_type.NOT, 'not', 0)
            )
        )
    ],
    ids=['sanity', 'consecutive']
)
def test_negation(expr: str, expect: nodes):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    assert Parser(tokens).parse() == expect

@pytest.mark.parametrize(
    "expr, expect",
    [
        (
            "4 + 5",
            BinaryOp(
                token=Parser_tok.Plus,
                left_child=Value(
                    Parser_tok.Int,
                    4,
                    Lexer_tok(Lexer_type.INT, '4', 0)
                ),
                right_child=Value(
                    Parser_tok.Int,
                    5,
                    Lexer_tok(Lexer_type.INT, '5', 4)
                ),
                lexer_tok=Lexer_tok(Lexer_type.PLUS, '+', 2)
            )
        ),
        (
            "4 - 5",
            BinaryOp(
                token=Parser_tok.Minus,
                left_child=Value(
                    Parser_tok.Int,
                    4,
                    Lexer_tok(Lexer_type.INT, '4', 0)
                ),
                right_child=Value(
                    Parser_tok.Int,
                    5,
                    Lexer_tok(Lexer_type.INT, '5', 4)
                ),
                lexer_tok=Lexer_tok(Lexer_type.MINUS, '-', 2)
            )
        ),
        (
            "6 + 7 - 9",
            BinaryOp(
                token=Parser_tok.Minus,
                left_child=BinaryOp(
                    token=Parser_tok.Plus,
                    left_child=Value(
                        Parser_tok.Int,
                        6,
                        Lexer_tok(Lexer_type.INT, '6', 0)
                    ),
                    right_child=Value(
                        Parser_tok.Int,
                        7,
                        Lexer_tok(Lexer_type.INT, '7', 4)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.PLUS, '+', 2)
                ),
                right_child=Value(
                    Parser_tok.Int,
                    9,
                    Lexer_tok(Lexer_type.INT, '9', 8)
                ),
                lexer_tok=Lexer_tok(Lexer_type.MINUS, '-', 6)
            )
        )
    ],
    ids=['+', '-', 'consecutive']
)
def test_low_ord_operator(expr: str, expect: nodes):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    assert Parser(tokens).parse() == expect

@pytest.mark.parametrize(
    "expr, expect",
    [
        (
            "6 // 7",
            BinaryOp(
                token=Parser_tok.FloorDiv,
                left_child=Value(
                    Parser_tok.Int,
                    6,
                    Lexer_tok(Lexer_type.INT, '6', 0)
                ),
                right_child=Value(
                    Parser_tok.Int,
                    7,
                    Lexer_tok(Lexer_type.INT, '7', 5)
                ),
                lexer_tok=Lexer_tok(Lexer_type.DSLASH, '//', 2)
            )
        ),
        (
            "6 / 7",
            BinaryOp(
                token=Parser_tok.TrueDiv,
                left_child=Value(
                    Parser_tok.Int,
                    6,
                    Lexer_tok(Lexer_type.INT, '6', 0)
                ),
                right_child=Value(
                    Parser_tok.Int,
                    7,
                    Lexer_tok(Lexer_type.INT, '7', 4)
                ),
                lexer_tok=Lexer_tok(Lexer_type.SLASH, '/', 2)
            )
        ),
        (
            "6 % 7",
            BinaryOp(
                token=Parser_tok.Mod,
                left_child=Value(
                    Parser_tok.Int,
                    6,
                    Lexer_tok(Lexer_type.INT, '6', 0)
                ),
                right_child=Value(
                    Parser_tok.Int,
                    7,
                    Lexer_tok(Lexer_type.INT, '7', 4)
                ),
                lexer_tok=Lexer_tok(Lexer_type.PERCENT, '%', 2)
            )
        ),
        (
            "6 * 7",
            BinaryOp(
                token=Parser_tok.Mult,
                left_child=Value(
                    Parser_tok.Int,
                    6,
                    Lexer_tok(Lexer_type.INT, '6', 0)
                ),
                right_child=Value(
                    Parser_tok.Int,
                    7,
                    Lexer_tok(Lexer_type.INT, '7', 4)
                ),
                lexer_tok=Lexer_tok(Lexer_type.STAR, '*', 2)
            )
        )
    ],
    ids=['floor_div', 'true_div', 'modulo', 'multiplication']
)
def test_high_ord_operator(expr: str, expect: nodes):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    assert Parser(tokens).parse() == expect

@pytest.mark.parametrize(
    "expr, expect",
    [
        (
            "+6",
            UnaryOp(
                token=Parser_tok.UnPlus,
                child=Value(
                    Parser_tok.Int,
                    6,
                    Lexer_tok(Lexer_type.INT, '6', 1)
                ),
                lexer_tok=Lexer_tok(Lexer_type.PLUS, '+', 0)
            ),
        ),
        (
            "-6",
            UnaryOp(
                token=Parser_tok.UnMinus,
                child=Value(
                    Parser_tok.Int,
                    6,
                    Lexer_tok(Lexer_type.INT, '6', 1)
                ),
                lexer_tok=Lexer_tok(Lexer_type.MINUS, '-', 0)
            ),
        ),
        (
            "+-6",
            UnaryOp(
                token=Parser_tok.UnPlus,
                child=UnaryOp(
                    token=Parser_tok.UnMinus,
                    child=Value(
                        Parser_tok.Int,
                        6,
                        Lexer_tok(Lexer_type.INT, '6', 2)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.MINUS, '-', 1)
                ),
                lexer_tok=Lexer_tok(Lexer_type.PLUS, '+', 0)
            )
        )
    ],
    ids=['+', '-', 'consecutive']
)
def test_factor(expr: str, expect: nodes):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    assert Parser(tokens).parse() == expect

@pytest.mark.parametrize(
    "expr, expect",
    [
        (
            "6 ** 7",
            BinaryOp(
                token=Parser_tok.Power,
                left_child=Value(
                    Parser_tok.Int,
                    6,
                    Lexer_tok(Lexer_type.INT, '6', 0)
                ),
                right_child=Value(
                    Parser_tok.Int,
                    7,
                    Lexer_tok(Lexer_type.INT, '7', 5)
                ),
                lexer_tok=Lexer_tok(Lexer_type.DSTAR, '**', 2)
            )
        ),
        (
            "6 ** 7 ** 9",
            BinaryOp(
                token=Parser_tok.Power,
                left_child=Value(
                    Parser_tok.Int,
                    6,
                    Lexer_tok(Lexer_type.INT, '6', 0)
                ),
                right_child=BinaryOp(
                    token=Parser_tok.Power,
                    left_child=Value(
                        Parser_tok.Int,
                        7,
                        Lexer_tok(Lexer_type.INT, '7', 5)
                    ),
                    right_child=Value(
                        Parser_tok.Int,
                        9,
                        Lexer_tok(Lexer_type.INT, '9', 10)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.DSTAR, '**', 7)
                ),
                lexer_tok=Lexer_tok(Lexer_type.DSTAR, '**', 2)
            )
        )
    ],
    ids=['sanity', 'consecutive']
)
def test_power(expr: str, expect: nodes):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    assert Parser(tokens).parse() == expect


@pytest.mark.parametrize(
    "expr, expect",
    [
        (
            "[]",
            Collection(
                token=Parser_tok.List,
                collection=[],
                brackets=(
                    Lexer_tok(Lexer_type.LSQB, '[', 0),
                    Lexer_tok(Lexer_type.RSQB, ']', 1)
                )
            )
        ),
        (
            "[1]",
            Collection(
                token=Parser_tok.List,
                collection=[
                    Value(Parser_tok.Int, 1, Lexer_tok(Lexer_type.INT, '1', 1))
                ],
                brackets=(
                    Lexer_tok(Lexer_type.LSQB, '[', 0),
                    Lexer_tok(Lexer_type.RSQB, ']', 2)
                )
            )
        ),
        (
            "[1,]",
            Collection(
                token=Parser_tok.List,
                collection=[
                    Value(Parser_tok.Int, 1, Lexer_tok(Lexer_type.INT, '1', 1))
                ],
                brackets=(
                    Lexer_tok(Lexer_type.LSQB, '[', 0),
                    Lexer_tok(Lexer_type.RSQB, ']', 3)
                )
            )
        ),
        (
            "[1,2]",
            Collection(
                token=Parser_tok.List,
                collection=[
                    Value(Parser_tok.Int, 1, Lexer_tok(Lexer_type.INT, '1', 1)),
                    Value(Parser_tok.Int, 2, Lexer_tok(Lexer_type.INT, '2', 3))
                ],
                brackets=(
                    Lexer_tok(Lexer_type.LSQB, '[', 0),
                    Lexer_tok(Lexer_type.RSQB, ']', 4)
                )
            )
        ),
        (
            "[[]]",
            Collection(
                token=Parser_tok.List,
                collection=[
                    Collection(
                        Parser_tok.List,
                        collection=[],
                        brackets=(
                            Lexer_tok(Lexer_type.LSQB, '[', 1),
                            Lexer_tok(Lexer_type.RSQB, ']', 2)
                        )
                    )
                ],
                brackets=(
                    Lexer_tok(Lexer_type.LSQB, '[', 0),
                    Lexer_tok(Lexer_type.RSQB, ']', 3)
                )
            )
        ),
        (
            "[,]",
            Parser.Failure(
                pos=1,
                wrong_tok=Lexer_tok(Lexer_type.COMMA, ',', 1),
                expect=['int', 'float', 'bool', 'ident', 'str', 'container', 'expr']
            )
        ),
        (
            "()",
            Collection(
                token=Parser_tok.Tuple,
                collection=[],
                brackets=(
                    Lexer_tok(Lexer_type.LPAR, '(', 0),
                    Lexer_tok(Lexer_type.RPAR, ')', 1)
                )
            )
        ),
        (
            "(1,)",
            Collection(
                token=Parser_tok.Tuple,
                collection=[
                    Value(Parser_tok.Int, 1, Lexer_tok(Lexer_type.INT, '1', 1))
                ],
                brackets=(
                    Lexer_tok(Lexer_type.LPAR, '(', 0),
                    Lexer_tok(Lexer_type.RPAR, ')', 3)
                )
            )
        ),
        (
            "(1,2)",
            Collection(
                token=Parser_tok.Tuple,
                collection=[
                    Value(Parser_tok.Int, 1, Lexer_tok(Lexer_type.INT, '1', 1)),
                    Value(Parser_tok.Int, 2, Lexer_tok(Lexer_type.INT, '2', 3))
                ],
                brackets=(
                    Lexer_tok(Lexer_type.LPAR, '(', 0),
                    Lexer_tok(Lexer_type.RPAR, ')', 4)
                )
            )
        ),
        (
            "(1,2,)",
            Collection(
                token=Parser_tok.Tuple,
                collection=[
                    Value(Parser_tok.Int, 1, Lexer_tok(Lexer_type.INT, '1', 1)),
                    Value(Parser_tok.Int, 2, Lexer_tok(Lexer_type.INT, '2', 3))
                ],
                brackets=(
                    Lexer_tok(Lexer_type.LPAR, '(', 0),
                    Lexer_tok(Lexer_type.RPAR, ')', 5)
                )
            )
        ),
        (
            "((),)",
            Collection(
                token=Parser_tok.Tuple,
                collection=[
                    Collection(
                        token=Parser_tok.Tuple,
                        collection=[],
                        brackets=(
                            Lexer_tok(Lexer_type.LPAR, '(', 1),
                            Lexer_tok(Lexer_type.RPAR, ')', 2)
                        )
                    ),
                ],
                brackets=(
                    Lexer_tok(Lexer_type.LPAR, '(', 0),
                    Lexer_tok(Lexer_type.RPAR, ')', 4)
                )
            )
        ),
        (
            "(,)",
            Parser.Failure(
                pos=1,
                wrong_tok=Lexer_tok(Lexer_type.COMMA, ',', 1),
                expect=['int', 'float', 'bool', 'ident', 'str', 'container', 'expr']
            )
        )
    ],
    ids=[
        'empty_list', 'one_val_list', 'one_val_list_comma',
        'two_vals_list', 'nested_list', 'list_fail_single_comma',

        'empty_tuple', 'one_val_tuple', 'two_vals_tuple',
        'two_vals_comma_tuple', 'nested_tuple', 'tuple_fail_single_comma'
    ]
)
def test_container(expr: str, expect: nodes | Parser.Failure):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    assert Parser(tokens).parse() == expect

@pytest.mark.parametrize(
    "expr, expect",
    [
        (
            "(6)",
            Value(Parser_tok.Int, 6, Lexer_tok(Lexer_type.INT, '6', 1))
        ),
        (
            "((6))",
            Value(Parser_tok.Int, 6, Lexer_tok(Lexer_type.INT, '6', 2))
        ),
        (
            "6 ** (1 + 2)",
            BinaryOp(
                token=Parser_tok.Power,
                left_child=Value(
                    Parser_tok.Int,
                    6,
                    Lexer_tok(Lexer_type.INT, '6', 0)
                ),
                right_child=BinaryOp(
                    token=Parser_tok.Plus,
                    left_child=Value(
                        Parser_tok.Int,
                        1,
                        Lexer_tok(Lexer_type.INT, '1', 6)
                    ),
                    right_child=Value(
                        Parser_tok.Int,
                        2,
                        Lexer_tok(Lexer_type.INT, '2', 10)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.PLUS, '+', 8)
                ),
                lexer_tok=Lexer_tok(Lexer_type.DSTAR, '**', 2)
            )
        )
    ],
    ids=['sanity', 'double_brackets', 'priority_test']
)
def test_brackets(expr: str, expect: nodes):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    assert Parser(tokens).parse() == expect

@pytest.mark.parametrize(
    "expr, expect",
    [
        (
            "6",
            Value(Parser_tok.Int, 6, Lexer_tok(Lexer_type.INT, '6', 0))
        ),
        (
            "6.7",
            Value(Parser_tok.Float, 6.7, Lexer_tok(Lexer_type.FLOAT, '6.7', 0))
        ),
        (
            "True",
            Value(Parser_tok.Bool, True, Lexer_tok(Lexer_type.BOOL, 'True', 0))
        ),
        (
            "wasd",
            Value(Parser_tok.Ident, 'wasd', Lexer_tok(Lexer_type.IDENT, 'wasd', 0))
        ),
        (
            "'wa'",
            Value(Parser_tok.Str, 'wa', Lexer_tok(Lexer_type.STR, "'wa'", 0))
        ),
        (
            "None",
            Value(Parser_tok.None_, None, Lexer_tok(Lexer_type.NONE, 'None', 0))
        ),
        (
            "[]",
            Collection(
                token=Parser_tok.List,
                collection=[],
                brackets=(
                    Lexer_tok(Lexer_type.LSQB, '[', 0),
                    Lexer_tok(Lexer_type.RSQB, ']', 1)
                )
            )
        )
    ],
    ids=['int', 'float', 'bool', 'ident', 'string', 'None', 'list']
)
def test_atom(expr: str, expect: nodes):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    assert Parser(tokens).parse() == expect

@pytest.mark.parametrize(
    "expr, expect",
    [
        (
            "not True and False or 6 ** tvoja_mama and -7",
            BinaryOp(
                token=Parser_tok.Or,
                left_child=BinaryOp(
                    token=Parser_tok.And,
                    left_child=UnaryOp(
                        token=Parser_tok.Not,
                        child=Value(
                            Parser_tok.Bool, True,
                            Lexer_tok(Lexer_type.BOOL, 'True', 4)
                        ),
                        lexer_tok=Lexer_tok(Lexer_type.NOT, 'not', 0)
                    ),
                    right_child=Value(
                        Parser_tok.Bool, False,
                        Lexer_tok(Lexer_type.BOOL, 'False', 13)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.AND, 'and', 9)
                ),
                right_child=BinaryOp(
                    token=Parser_tok.And,
                    left_child=BinaryOp(
                        token=Parser_tok.Power,
                        left_child=Value(
                            Parser_tok.Int, 6,
                            Lexer_tok(Lexer_type.INT, '6', 22)
                        ),
                        right_child=Value(
                            Parser_tok.Ident, 'tvoja_mama',
                            Lexer_tok(Lexer_type.IDENT, 'tvoja_mama', 27)
                        ),
                        lexer_tok=Lexer_tok(Lexer_type.DSTAR, '**', 24)
                    ),
                    right_child=UnaryOp(
                        token=Parser_tok.UnMinus,
                        child=Value(
                            Parser_tok.Int, 7,
                            Lexer_tok(Lexer_type.INT, '7', 43)
                        ),
                        lexer_tok=Lexer_tok(Lexer_type.MINUS, '-', 42)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.AND, 'and', 38)
                ),
                lexer_tok=Lexer_tok(Lexer_type.OR, 'or', 19)
            )
        ),
        (
            "6 and (7 or 6) and 9",
            BinaryOp(
                token=Parser_tok.And,
                left_child=BinaryOp(
                    token=Parser_tok.And,
                    left_child=Value(
                        Parser_tok.Int, 6,
                        Lexer_tok(Lexer_type.INT, '6', 0)
                    ),
                    right_child=BinaryOp(
                        token=Parser_tok.Or,
                        left_child=Value(
                            Parser_tok.Int, 7,
                            Lexer_tok(Lexer_type.INT, '7', 7)
                        ),
                        right_child=Value(
                            Parser_tok.Int, 6,
                            Lexer_tok(Lexer_type.INT, '6', 12)
                        ),
                        lexer_tok=Lexer_tok(Lexer_type.OR, 'or', 9)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.AND, 'and', 2)
                ),
                right_child=Value(
                    Parser_tok.Int, 9,
                    Lexer_tok(Lexer_type.INT, '9', 19)
                ),
                lexer_tok=Lexer_tok(Lexer_type.AND, 'and', 15)
            )
        ),
        (
            "tvoja_mama in (6 * 2, -7, 6 <= 2)",
            CompareNode(
                operators=[
                    (Parser_tok.In, [Lexer_tok(Lexer_type.IN, 'in', 11)])
                ],
                operands=[
                    Value(
                        Parser_tok.Ident,
                        'tvoja_mama',
                        Lexer_tok(Lexer_type.IDENT, 'tvoja_mama', 0)
                    ),
                    Collection(
                        token=Parser_tok.Tuple,
                        collection=[
                            BinaryOp(
                                token=Parser_tok.Mult,
                                left_child=Value(
                                    Parser_tok.Int,
                                    6,
                                    Lexer_tok(Lexer_type.INT, '6', 15)
                                ),
                                right_child=Value(
                                    Parser_tok.Int,
                                    2,
                                    Lexer_tok(Lexer_type.INT, '2', 19)
                                ),
                                lexer_tok=Lexer_tok(Lexer_type.STAR, '*', 17)
                            ),
                            UnaryOp(
                                token=Parser_tok.UnMinus,
                                child=Value(
                                    Parser_tok.Int,
                                    7,
                                    Lexer_tok(Lexer_type.INT, '7', 23)
                                ),
                                lexer_tok=Lexer_tok(Lexer_type.MINUS, '-', 22)
                            ),
                            CompareNode(
                                operators=[
                                    (Parser_tok.Le, [Lexer_tok(Lexer_type.LE, '<=', 28)])
                                ],
                                operands=[
                                    Value(
                                        Parser_tok.Int,
                                        6,
                                        Lexer_tok(Lexer_type.INT, '6', 26)
                                    ),
                                    Value(
                                        Parser_tok.Int,
                                        2,
                                        Lexer_tok(Lexer_type.INT, '2', 31)
                                    )
                                ]
                            )
                        ],
                        brackets=(
                            Lexer_tok(Lexer_type.LPAR, '(', 14),
                            Lexer_tok(Lexer_type.RPAR, ')', 32)
                        )
                    )
                ]
            )
        ),
        (
            "5 <= 6 and 6 == tvoja_mama",
            BinaryOp(
                token=Parser_tok.And,
                left_child=CompareNode(
                    operators=[
                        (Parser_tok.Le, [Lexer_tok(Lexer_type.LE, '<=', 2)])
                    ],
                    operands=[
                        Value(
                            Parser_tok.Int, 5,
                            Lexer_tok(Lexer_type.INT, '5', 0)
                        ),
                        Value(
                            Parser_tok.Int, 6,
                            Lexer_tok(Lexer_type.INT, '6', 5)
                        )
                    ]
                ),
                right_child=CompareNode(
                    operators=[
                        (Parser_tok.Eq, [Lexer_tok(Lexer_type.EQ, '==', 13)])
                    ],
                    operands=[
                        Value(
                            Parser_tok.Int, 6,
                            Lexer_tok(Lexer_type.INT, '6', 11)
                        ),
                        Value(
                            Parser_tok.Ident, 'tvoja_mama',
                            Lexer_tok(Lexer_type.IDENT, 'tvoja_mama', 16)
                        )
                    ]
                ),
                lexer_tok=Lexer_tok(Lexer_type.AND, 'and', 7)
            )
        ),
        (
            "True and not not True",
            BinaryOp(
                token=Parser_tok.And,
                left_child=Value(
                    Parser_tok.Bool, True,
                    Lexer_tok(Lexer_type.BOOL, 'True', 0)
                ),
                right_child=UnaryOp(
                    token=Parser_tok.Not,
                    child=UnaryOp(
                        token=Parser_tok.Not,
                        child=Value(
                            Parser_tok.Bool, True,
                            Lexer_tok(Lexer_type.BOOL, 'True', 17)
                        ),
                        lexer_tok=Lexer_tok(Lexer_type.NOT, 'not', 13)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.NOT, 'not', 9)
                ),
                lexer_tok=Lexer_tok(Lexer_type.AND, 'and', 5)
            )
        ),
        (
            "(True or False) + 5 ** 6.8 ** (not 6.9)",
            BinaryOp(
                token=Parser_tok.Plus,
                left_child=BinaryOp(
                    token=Parser_tok.Or,
                    left_child=Value(
                        Parser_tok.Bool,
                        True,
                        Lexer_tok(Lexer_type.BOOL, 'True', 1)
                    ),
                    right_child=Value(
                        Parser_tok.Bool,
                        False,
                        Lexer_tok(Lexer_type.BOOL, 'False', 9)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.OR, 'or', 6)
                ),
                right_child=BinaryOp(
                    token=Parser_tok.Power,
                    left_child=Value(
                        Parser_tok.Int,
                        5,
                        Lexer_tok(Lexer_type.INT, '5', 18)
                    ),
                    right_child=BinaryOp(
                        token=Parser_tok.Power,
                        left_child=Value(
                            Parser_tok.Float,
                            6.8,
                            Lexer_tok(Lexer_type.FLOAT, '6.8', 23)
                        ),
                        right_child=UnaryOp(
                            token=Parser_tok.Not,
                            child=Value(
                                Parser_tok.Float,
                                6.9,
                                Lexer_tok(Lexer_type.FLOAT, '6.9', 35)
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.NOT, 'not', 31)
                        ),
                        lexer_tok=Lexer_tok(Lexer_type.DSTAR, '**', 27)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.DSTAR, '**', 20)
                ),
                lexer_tok=Lexer_tok(Lexer_type.PLUS, '+', 16)
            )
        ),
        (
            "6 not in (7,)",
            CompareNode(
                operators=[
                    (Parser_tok.NotIn, [
                        Lexer_tok(Lexer_type.NOT, 'not', 2),
                        Lexer_tok(Lexer_type.IN, 'in', 6)
                    ])
                ],
                operands=[
                    Value(
                        Parser_tok.Int, 6,
                        Lexer_tok(Lexer_type.INT, '6', 0)
                    ),
                    Collection(
                        token=Parser_tok.Tuple,
                        collection=[
                            Value(
                                Parser_tok.Int, 7,
                                Lexer_tok(Lexer_type.INT, '7', 10)
                            )
                        ],
                        brackets=(
                            Lexer_tok(Lexer_type.LPAR, '(', 9),
                            Lexer_tok(Lexer_type.RPAR, ')', 12)
                        )
                    )
                ]
            )
        ),
        (
            "6 not in (7,) == 6",
            CompareNode(
                operators=[
                    (Parser_tok.NotIn, [
                        Lexer_tok(Lexer_type.NOT, 'not', 2),
                        Lexer_tok(Lexer_type.IN, 'in', 6)
                    ]),
                    (Parser_tok.Eq, [Lexer_tok(Lexer_type.EQ, '==', 14)])
                ],
                operands=[
                    Value(
                        Parser_tok.Int, 6,
                        Lexer_tok(Lexer_type.INT, '6', 0)
                    ),
                    Collection(
                        token=Parser_tok.Tuple,
                        collection=[
                            Value(
                                Parser_tok.Int, 7,
                                Lexer_tok(Lexer_type.INT, '7', 10)
                            )
                        ],
                        brackets=(
                            Lexer_tok(Lexer_type.LPAR, '(', 9),
                            Lexer_tok(Lexer_type.RPAR, ')', 12)
                        )
                    ),
                    Value(
                        Parser_tok.Int, 6,
                        Lexer_tok(Lexer_type.INT, '6', 17)
                    )
                ]
            )
        ),
        (
            "tvoja_mamka is None",
            CompareNode(
                operators=[
                    (Parser_tok.Is, [Lexer_tok(Lexer_type.IS, 'is', 12)])
                ],
                operands=[
                    Value(
                        Parser_tok.Ident, 'tvoja_mamka',
                        Lexer_tok(Lexer_type.IDENT, 'tvoja_mamka', 0)
                    ),
                    Value(
                        Parser_tok.None_, None,
                        Lexer_tok(Lexer_type.NONE, 'None', 15)
                    )
                ]
            )
        ),
        (
            "5 <= 5 and 5 % 5 and 5 in (1,2,)",
            BinaryOp(
                token=Parser_tok.And,
                left_child=BinaryOp(
                    token=Parser_tok.And,
                    left_child=CompareNode(
                        operators=[
                            (Parser_tok.Le, [Lexer_tok(Lexer_type.LE, '<=', 2)])
                        ],
                        operands=[
                            Value(
                                Parser_tok.Int, 5,
                                Lexer_tok(Lexer_type.INT, '5', 0)
                            ),
                            Value(
                                Parser_tok.Int, 5,
                                Lexer_tok(Lexer_type.INT, '5', 5)
                            )
                        ]
                    ),
                    right_child=BinaryOp(
                        token=Parser_tok.Mod,
                        left_child=Value(
                            Parser_tok.Int,
                            5,
                            Lexer_tok(Lexer_type.INT, '5', 11)
                        ),
                        right_child=Value(
                            Parser_tok.Int,
                            5,
                            Lexer_tok(Lexer_type.INT, '5', 15)
                        ),
                        lexer_tok=Lexer_tok(Lexer_type.PERCENT, '%', 13)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.AND, 'and', 7)
                ),
                right_child=CompareNode(
                    operators=[
                        (Parser_tok.In, [Lexer_tok(Lexer_type.IN, 'in', 23)])
                    ],
                    operands=[
                        Value(
                            Parser_tok.Int,
                            5,
                            Lexer_tok(Lexer_type.INT, '5', 21)
                        ),
                        Collection(
                            token=Parser_tok.Tuple,
                            collection=[
                                Value(
                                    Parser_tok.Int,
                                    1,
                                    Lexer_tok(Lexer_type.INT, '1', 27)
                                ),
                                Value(
                                    Parser_tok.Int,
                                    2,
                                    Lexer_tok(Lexer_type.INT, '2', 29)
                                )
                            ],
                            brackets=(
                                Lexer_tok(Lexer_type.LPAR, '(', 26),
                                Lexer_tok(Lexer_type.RPAR, ')', 31)
                            )
                        )
                    ]
                ),
                lexer_tok=Lexer_tok(Lexer_type.AND, 'and', 17)
            )
        ),
        (
            "6 and 7 and",
            Parser.Failure(
                pos=4,
                wrong_tok=Lexer_tok(Lexer_type.EOF, '$', 11),
                expect=['int', 'float', 'bool', 'ident', 'str', 'container', 'expr']
            )
        ),
        (
            "and",
            Parser.Failure(
                pos=0,
                wrong_tok=Lexer_tok(Lexer_type.AND, 'and', 0),
                expect=['int', 'float', 'bool', 'ident', 'str', 'container', 'expr']
            )
        )
    ]
)
def test_expressions(expr: str, expect: nodes):
    tokens = Lexer(expr).tokenize()
    if isinstance(tokens, Lexer.Failure):
        assert False
    assert Parser(tokens).parse() == expect