import pytest

from evaluator.interpreter.stages.lexer import Lexer
from evaluator.interpreter.stages.parser import Parser
from evaluator.interpreter.stages.constantfolder import ConstantFolder

from evaluator.types import (
    Lexer_type, nodes, Parser_tok,
    Lexer_tok, BinaryOp, UnaryOp, Value, Collection, CompareNode, Constant
)
from evaluator.types import nodes

@pytest.mark.parametrize(
    "expr, expect",
    [
        pytest.param(
            "5 + 6",
            Constant(
                value=11,                                    
                source=BinaryOp(
                    token=Parser_tok.Plus,
                    left_child=Value(
                        token=Parser_tok.Int,
                        value=5,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '5', 0)
                    ),
                    right_child=Value(
                        token=Parser_tok.Int,
                        value=6,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '6', 4)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.PLUS, '+', 2)
                )
            ),
            id="add"
        ),
        pytest.param(
            "10 - 3",
            Constant(
                7,
                source=BinaryOp(
                    token=Parser_tok.Minus,
                    left_child=Value(
                        token=Parser_tok.Int,
                        value=10,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '10', 0)),
                    right_child=Value(
                        token=Parser_tok.Int,
                        value=3,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '3', 5)),
                    lexer_tok=Lexer_tok(Lexer_type.MINUS, '-', 3)
                )
            ),
            id="sub"
        ),
        pytest.param(
            "4 * 7",
            Constant(
                28,
                source=BinaryOp(
                    token=Parser_tok.Mult,
                    left_child=Value(
                        token=Parser_tok.Int,
                        value=4,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '4', 0)),
                    right_child=Value(
                        token=Parser_tok.Int,
                        value=7,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '7', 4)),
                    lexer_tok=Lexer_tok(Lexer_type.STAR, '*', 2)
                )
            ),
            id="mul"
        ),
        pytest.param(
            "8 / 2",
            Constant(
                4,
                source=BinaryOp(
                    token=Parser_tok.TrueDiv,
                    left_child=Value(
                        token=Parser_tok.Int,
                        value=8,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '8', 0)
                    ),
                    right_child=Value(
                        token=Parser_tok.Int,
                        value=2,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '2', 4)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.SLASH, '/', 2)
                )
            ),
            id="div"
        ),
        pytest.param(
            "2 ** 3",
            Constant(
                value=8,
                source=BinaryOp(
                    token=Parser_tok.Power,
                    left_child=Value(
                        token=Parser_tok.Int,
                        value=2,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '2', 0)
                    ),
                    right_child=Value(
                        token=Parser_tok.Int,
                        value=3,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '3', 5)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.DSTAR, '**', 2)
                )
            ),
            id="pow"
        ),
        pytest.param(
            "-5",
            Constant(
                value=-5,
                source=UnaryOp(
                    token=Parser_tok.UnMinus,
                    child=Value(
                        token=Parser_tok.Int,
                        value=5,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '5', 1)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.MINUS, '-', 0)
                )
            ),
            id="unary_minus"
        ),
        pytest.param(
            "+5",
            Constant(
                value=5,
                source=UnaryOp(
                    token=Parser_tok.UnPlus,
                    child=Value(
                        token=Parser_tok.Int,
                        value=5,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '5', 1)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.PLUS, '+', 0)
                )
            ),
            id="unary_plus"
        ),
        pytest.param(
            "not True",
            Constant(
                value=False,
                source=UnaryOp(
                    token=Parser_tok.Not,
                    child=Value(
                        token=Parser_tok.Bool,
                        value=True,
                        lexer_tok=Lexer_tok(Lexer_type.BOOL, 'True', 4)),
                    lexer_tok=Lexer_tok(Lexer_type.NOT, 'not', 0)
                )
            ),
            id="unary_not"
        ),
        pytest.param(
            "(2 + 3) * 4",
            Constant(
                value=20,
                source=BinaryOp(
                    token=Parser_tok.Mult,
                    left_child=BinaryOp(
                        token=Parser_tok.Plus,
                        left_child=Value(
                            token=Parser_tok.Int,
                            value=2,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '2', 1)),
                        right_child=Value(
                            token=Parser_tok.Int,
                            value=3,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '3', 5)),
                        lexer_tok=Lexer_tok(Lexer_type.PLUS, '+', 3)
                    ),
                    right_child=Value(
                        token=Parser_tok.Int,
                        value=4,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '4', 10)
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.STAR, '*', 8)
                )
            ),
            id="nested_arith"
        ),
        pytest.param(
            "[1, 2, 3]",
            Constant(
                value=[1, 2, 3],
                source=Collection(
                    token=Parser_tok.List,
                    collection=[
                        Value(
                            token=Parser_tok.Int,
                            value=1,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '1', 1)
                        ),
                        Value(
                            token=Parser_tok.Int,
                            value=2,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '2', 4)
                        ),
                        Value(
                            token=Parser_tok.Int,
                            value=3,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '3', 7)
                        )
                    ],
                    brackets=(
                        Lexer_tok(Lexer_type.LSQB, '[', 0),
                        Lexer_tok(Lexer_type.RSQB, ']', 8)
                    )
                )
            ),
            id="list"
        ),
        pytest.param(
            "(1, 2, 3)",
            Constant(
                value=(1, 2, 3),
                source=Collection(
                    token=Parser_tok.Tuple,
                    collection=[
                        Value(
                            token=Parser_tok.Int,
                            value=1,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '1', 1)),
                        Value(
                            token=Parser_tok.Int,
                            value=2,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '2', 4)),
                        Value(
                            token=Parser_tok.Int,
                            value=3,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '3', 7)
                        )
                    ],
                    brackets=(
                        Lexer_tok(Lexer_type.LPAR, '(', 0),
                        Lexer_tok(Lexer_type.RPAR, ')', 8)
                    )
                )
            ),
            id="tuple"
        ),
        pytest.param(
            "[1 + 2, 3 * 4]",
            Constant(
                value=[3, 12],
                source=Collection(
                    token=Parser_tok.List,
                    collection=[
                        BinaryOp(
                            token=Parser_tok.Plus,
                            left_child=Value(
                                token=Parser_tok.Int,
                                value=1,
                                lexer_tok=Lexer_tok(Lexer_type.INT, '1', 1)
                            ),
                            right_child=Value(
                                token=Parser_tok.Int,
                                value=2,
                                lexer_tok=Lexer_tok(Lexer_type.INT, '2', 5)
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.PLUS, '+', 3)),
                        BinaryOp(
                            token=Parser_tok.Mult,
                            left_child=Value(
                                token=Parser_tok.Int,
                                value=3,
                                lexer_tok=Lexer_tok(Lexer_type.INT, '3', 8)
                            ),
                            right_child=Value(
                                token=Parser_tok.Int,
                                value=4,
                                lexer_tok=Lexer_tok(Lexer_type.INT, '4', 12)
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.STAR, '*', 10)
                        )
                    ],
                    brackets=(
                        Lexer_tok(Lexer_type.LSQB, '[', 0),
                        Lexer_tok(Lexer_type.RSQB, ']', 13)
                    )
                )
            ),
            id="list_folded_items"
        ),
        pytest.param(
            "1 < 2",
            Constant(
                value=True,
                source=CompareNode(
                    operators=[(Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, '<', 2)])],
                    operands=[
                        Value(
                            token=Parser_tok.Int,
                            value=1,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '1', 0)
                        ),
                        Value(
                            token=Parser_tok.Int,
                            value=2,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '2', 4)
                        )
                    ]
                )
            ),
            id="compare_lt"
        ),
        pytest.param(
            "1 < 2 < 3",
            Constant(
                value=True,
                source=CompareNode(
                    operators=[
                        (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, '<', 2)]),
                        (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, '<', 6)])
                    ],
                    operands=[
                        Value(
                            token=Parser_tok.Int,
                            value=1,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '1', 0)
                        ),
                        Value(
                            token=Parser_tok.Int,
                            value=2,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '2', 4)
                        ),
                        Value(
                            token=Parser_tok.Int,
                            value=3,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '3', 8)
                        )
                    ]
                )
            ),
            id="chained_compare_true"
        ),
        pytest.param(
            "1 < 2 > 3",
            Constant(
                value=False,
                source=CompareNode(
                    operators=[
                        (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, '<', 2)]),
                        (Parser_tok.Gt, [Lexer_tok(Lexer_type.GT, '>', 6)])
                    ],
                    operands=[
                        Value(
                            token=Parser_tok.Int,
                            value=1,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '1', 0)
                        ),
                        Value(
                            token=Parser_tok.Int,
                            value=2,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '2', 4)
                        ),
                        Value(
                            token=Parser_tok.Int,
                            value=3,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '3', 8)
                        )
                    ]
                )
            ),
            id="chained_compare_false"
        ),
        pytest.param(
            "1 == 1",
            Constant(
                value=True,
                source=CompareNode(
                    operators=[(Parser_tok.Eq, [Lexer_tok(Lexer_type.EQ, '==', 2)])],
                    operands=[
                        Value(
                            token=Parser_tok.Int,
                            value=1,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '1', 0)),
                        Value(
                            token=Parser_tok.Int,
                            value=1,
                            lexer_tok=Lexer_tok(Lexer_type.INT, '1', 5)
                        )
                    ]
                )
            ),
            id="compare_eq"
        )
    ]
)
def test_basic_ConstantFolder(expr: str, expect: nodes):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    assert ConstantFolder().fold(ast) == expect

@pytest.mark.parametrize(
    "expr, expect",
    [
        pytest.param(
            "x",
            Value(Parser_tok.Ident, "x", Lexer_tok(Lexer_type.IDENT, 'x', 0)),
            id="ident"
        ),
        pytest.param(
            "x + 6",
            BinaryOp(
                token=Parser_tok.Plus,
                left_child=Value(
                    token=Parser_tok.Ident,
                    value="x",
                    lexer_tok=Lexer_tok(Lexer_type.IDENT, "x", 0),
                ),
                right_child=Constant(
                    value=6,
                    source=Value(
                        token=Parser_tok.Int,
                        value=6,
                        lexer_tok=Lexer_tok(Lexer_type.INT, "6", 4),
                    ),
                ),
                lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 2),
            ),
            id="mixed_add"
        ),
        pytest.param(
            "-x",
            UnaryOp(
                token=Parser_tok.UnMinus,
                child=Value(
                    token=Parser_tok.Ident,
                    value="x",
                    lexer_tok=Lexer_tok(Lexer_type.IDENT, "x", 1),
                ),
                lexer_tok=Lexer_tok(Lexer_type.MINUS, "-", 0),
            ),
            id="unary_ident"
        ),
        pytest.param(
            "[1, x, 3]",
            Collection(
                token=Parser_tok.List,
                collection=[
                    Constant(
                        value=1,
                        source=Value(
                            token=Parser_tok.Int,
                            value=1,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "1", 1),
                        ),
                    ),
                    Value(
                        token=Parser_tok.Ident,
                        value="x",
                        lexer_tok=Lexer_tok(Lexer_type.IDENT, "x", 4),
                    ),
                    Constant(
                        value=3,
                        source=Value(
                            token=Parser_tok.Int,
                            value=3,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "3", 7),
                        ),
                    ),
                ],
                brackets=(
                    Lexer_tok(Lexer_type.LSQB, '[', 0),
                    Lexer_tok(Lexer_type.RSQB, ']', 8)
                )
            ),
            id="list_mixed"
        ),
        pytest.param(
            "(1, x, 3)",
            Collection(
                token=Parser_tok.Tuple,
                collection=[
                    Constant(
                        value=1,
                        source=Value(
                            token=Parser_tok.Int,
                            value=1,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "1", 1),
                        ),
                    ),
                    Value(
                        token=Parser_tok.Ident,
                        value="x",
                        lexer_tok=Lexer_tok(Lexer_type.IDENT, "x", 4),
                    ),
                    Constant(
                        value=3,
                        source=Value(
                            token=Parser_tok.Int,
                            value=3,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "3", 7),
                        ),
                    ),
                ],
                brackets=(
                    Lexer_tok(Lexer_type.LPAR, '(', 0),
                    Lexer_tok(Lexer_type.RPAR, ')', 8)
                )
            ),
            id="tuple_mixed"
        ),
        pytest.param(
            "1 < x < 3",
            CompareNode(
                operators=[
                    (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, "<", 2)]),
                    (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, "<", 6)]),
                ],
                operands=[
                    Constant(
                        value=1,
                        source=Value(
                            token=Parser_tok.Int,
                            value=1,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "1", 0),
                        ),
                    ),
                    Value(
                        token=Parser_tok.Ident,
                        value="x",
                        lexer_tok=Lexer_tok(Lexer_type.IDENT, "x", 4),
                    ),
                    Constant(
                        value=3,
                        source=Value(
                            token=Parser_tok.Int,
                            value=3,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "3", 8),
                        ),
                    ),
                ],
            ),
            id="compare_mixed"
        ),
        pytest.param(
            "(1 + 2) < (2 + 3)",
            Constant(
                value=True,
                source=CompareNode(
                    operators=[
                        (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, "<", 8)]),
                    ],
                    operands=[
                        BinaryOp(
                            token=Parser_tok.Plus,
                            left_child=Value(
                                token=Parser_tok.Int,
                                value=1,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "1", 1),
                            ),
                            right_child=Value(
                                token=Parser_tok.Int,
                                value=2,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "2", 5),
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 3),
                        ),
                        BinaryOp(
                            token=Parser_tok.Plus,
                            left_child=Value(
                                token=Parser_tok.Int,
                                value=2,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "2", 11),
                            ),
                            right_child=Value(
                                token=Parser_tok.Int,
                                value=3,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "3", 15),
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 13),
                        ),
                    ],
                ),
            ),
            id="compare_folded"
        ),
        pytest.param(
            "5 + 6 * 2",
            Constant(
                value=17,
                source=BinaryOp(
                    token=Parser_tok.Plus,
                    left_child=Value(
                        token=Parser_tok.Int,
                        value=5,
                        lexer_tok=Lexer_tok(Lexer_type.INT, "5", 0),
                    ),
                    right_child=BinaryOp(
                        token=Parser_tok.Mult,
                        left_child=Value(
                            token=Parser_tok.Int,
                            value=6,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "6", 4),
                        ),
                        right_child=Value(
                            token=Parser_tok.Int,
                            value=2,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "2", 8),
                        ),
                        lexer_tok=Lexer_tok(Lexer_type.STAR, "*", 6),
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 2),
                ),
            ),
            id="arith_precedence"
        ),
        pytest.param(
            "(5 + 6) * 2",
            Constant(
                value=22,
                source=BinaryOp(
                    token=Parser_tok.Mult,
                    left_child=BinaryOp(
                        token=Parser_tok.Plus,
                        left_child=Value(
                            token=Parser_tok.Int,
                            value=5,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "5", 1),
                        ),
                        right_child=Value(
                            token=Parser_tok.Int,
                            value=6,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "6", 5),
                        ),
                        lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 3),
                    ),
                    right_child=Value(
                        token=Parser_tok.Int,
                        value=2,
                        lexer_tok=Lexer_tok(Lexer_type.INT, "2", 10),
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.STAR, "*", 8),
                ),
            ),
            id="arith_parentheses"
        ),
        pytest.param(
            "-(3 + 4)",
            Constant(
                value=-7,
                source=UnaryOp(
                    token=Parser_tok.UnMinus,
                    child=BinaryOp(
                        token=Parser_tok.Plus,
                        left_child=Value(
                            token=Parser_tok.Int,
                            value=3,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "3", 2),
                        ),
                        right_child=Value(
                            token=Parser_tok.Int,
                            value=4,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "4", 6),
                        ),
                        lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 4),
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.MINUS, "-", 0),
                ),
            ),
            id="unary_minus_nested"
        ),
        pytest.param(
            "+(2 * 3 + 4)",
            Constant(
                value=10,
                source=UnaryOp(
                    token=Parser_tok.UnPlus,
                    child=BinaryOp(
                        token=Parser_tok.Plus,
                        left_child=BinaryOp(
                            token=Parser_tok.Mult,
                            left_child=Value(
                                token=Parser_tok.Int,
                                value=2,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "2", 2),
                            ),
                            right_child=Value(
                                token=Parser_tok.Int,
                                value=3,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "3", 6),
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.STAR, "*", 4),
                        ),
                        right_child=Value(
                            token=Parser_tok.Int,
                            value=4,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "4", 10),
                        ),
                        lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 8),
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 0),
                ),
            ),
            id="unary_plus_nested"
        ),
        pytest.param(
            "not (1 < 2)",
            Constant(
                value=False,
                source=UnaryOp(
                    token=Parser_tok.Not,
                    child=CompareNode(
                        operands=[
                            Value(
                                token=Parser_tok.Int,
                                value=1,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "1", 5),
                            ),
                            Value(
                                token=Parser_tok.Int,
                                value=2,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "2", 9),
                            ),
                        ],
                        operators=[
                            (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, "<", 7)]),
                        ],
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.NOT, "not", 0),
                ),
            ),
            id="unary_not_compare"
        ),
        pytest.param(
            "[1 + 2, 3 * 4, -(5 - 7)]",
            Constant(
                value=[3, 12, 2],
                source=Collection(
                    token=Parser_tok.List,
                    collection=[
                        BinaryOp(
                            token=Parser_tok.Plus,
                            left_child=Value(
                                token=Parser_tok.Int,
                                value=1,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "1", 1),
                            ),
                            right_child=Value(
                                token=Parser_tok.Int,
                                value=2,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "2", 5),
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 3),
                        ),
                        BinaryOp(
                            token=Parser_tok.Mult,
                            left_child=Value(
                                token=Parser_tok.Int,
                                value=3,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "3", 8),
                            ),
                            right_child=Value(
                                token=Parser_tok.Int,
                                value=4,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "4", 12),
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.STAR, "*", 10),
                        ),
                        UnaryOp(
                            token=Parser_tok.UnMinus,
                            child=BinaryOp(
                                token=Parser_tok.Minus,
                                left_child=Value(
                                    token=Parser_tok.Int,
                                    value=5,
                                    lexer_tok=Lexer_tok(Lexer_type.INT, "5", 17),
                                ),
                                right_child=Value(
                                    token=Parser_tok.Int,
                                    value=7,
                                    lexer_tok=Lexer_tok(Lexer_type.INT, "7", 21),
                                ),
                                lexer_tok=Lexer_tok(Lexer_type.MINUS, "-", 19),
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.MINUS, "-", 15),
                        ),
                    ],
                    brackets=(
                        Lexer_tok(Lexer_type.LSQB, '[', 0),
                        Lexer_tok(Lexer_type.RSQB, ']', 23)
                    )
                ),
            ),
            id="list_all_folded_complex"
        ),
        pytest.param(
            "([1 + 2, 3], (4 * 5, 6 + 7))",
            Constant(
                value=([3, 3], (20, 13)),
                source=Collection(
                    token=Parser_tok.Tuple,
                    collection=[
                        Collection(
                            token=Parser_tok.List,
                            collection=[
                                BinaryOp(
                                    token=Parser_tok.Plus,
                                    left_child=Value(
                                        token=Parser_tok.Int,
                                        value=1,
                                        lexer_tok=Lexer_tok(Lexer_type.INT, "1", 2),
                                    ),
                                    right_child=Value(
                                        token=Parser_tok.Int,
                                        value=2,
                                        lexer_tok=Lexer_tok(Lexer_type.INT, "2", 6),
                                    ),
                                    lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 4),
                                ),
                                Value(
                                    token=Parser_tok.Int,
                                    value=3,
                                    lexer_tok=Lexer_tok(Lexer_type.INT, "3", 9),
                                ),
                            ],
                            brackets=(
                                Lexer_tok(Lexer_type.LSQB, '[', 1),
                                Lexer_tok(Lexer_type.RSQB, ']', 10)
                            )
                        ),
                        Collection(
                            token=Parser_tok.Tuple,
                            collection=[
                                BinaryOp(
                                    token=Parser_tok.Mult,
                                    left_child=Value(
                                        token=Parser_tok.Int,
                                        value=4,
                                        lexer_tok=Lexer_tok(Lexer_type.INT, "4", 14),
                                    ),
                                    right_child=Value(
                                        token=Parser_tok.Int,
                                        value=5,
                                        lexer_tok=Lexer_tok(Lexer_type.INT, "5", 18),
                                    ),
                                    lexer_tok=Lexer_tok(Lexer_type.STAR, "*", 16),
                                ),
                                BinaryOp(
                                    token=Parser_tok.Plus,
                                    left_child=Value(
                                        token=Parser_tok.Int,
                                        value=6,
                                        lexer_tok=Lexer_tok(Lexer_type.INT, "6", 21),
                                    ),
                                    right_child=Value(
                                        token=Parser_tok.Int,
                                        value=7,
                                        lexer_tok=Lexer_tok(Lexer_type.INT, "7", 25),
                                    ),
                                    lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 23),
                                ),
                            ],
                            brackets=(
                                Lexer_tok(Lexer_type.LPAR, '(', 13),
                                Lexer_tok(Lexer_type.RPAR, ')', 26)
                            )
                        ),
                    ],
                    brackets=(
                        Lexer_tok(Lexer_type.LPAR, '(', 0),
                        Lexer_tok(Lexer_type.RPAR, ')', 27)
                    )
                ),
            ),
            id="nested_collections"
        ),
        pytest.param(
            "1 < 2 < 3 < 4",
            Constant(
                value=True,
                source=CompareNode(
                    operators=[
                        (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, "<", 2)]),
                        (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, "<", 6)]),
                        (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, "<", 10)]),
                    ],
                    operands=[
                        Value(
                            token=Parser_tok.Int,
                            value=1,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "1", 0),
                        ),
                        Value(
                            token=Parser_tok.Int,
                            value=2,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "2", 4),
                        ),
                        Value(
                            token=Parser_tok.Int,
                            value=3,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "3", 8),
                        ),
                        Value(
                            token=Parser_tok.Int,
                            value=4,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "4", 12),
                        ),
                    ],
                ),
            ),
            id="chained_compare_long_true"
        ),
        pytest.param(
            "(1 + 2) < (3 * 2) <= (8 - 2)",
            Constant(
                value=True,
                source=CompareNode(
                    operands=[
                        BinaryOp(
                            token=Parser_tok.Plus,
                            left_child=Value(
                                token=Parser_tok.Int,
                                value=1,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "1", 1),
                            ),
                            right_child=Value(
                                token=Parser_tok.Int,
                                value=2,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "2", 5),
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 3),
                        ),
                        BinaryOp(
                            token=Parser_tok.Mult,
                            left_child=Value(
                                token=Parser_tok.Int,
                                value=3,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "3", 11),
                            ),
                            right_child=Value(
                                token=Parser_tok.Int,
                                value=2,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "2", 15),
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.STAR, "*", 13),
                        ),
                        BinaryOp(
                            token=Parser_tok.Minus,
                            left_child=Value(
                                token=Parser_tok.Int,
                                value=8,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "8", 22),
                            ),
                            right_child=Value(
                                token=Parser_tok.Int,
                                value=2,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "2", 26),
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.MINUS, "-", 24),
                        ),
                    ],
                    operators=[
                        (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, "<", 8)]),
                        (Parser_tok.Le, [Lexer_tok(Lexer_type.LE, "<=", 18)]),
                    ],
                ),
            ),
            id="mixed_compare_folded"
        ),
        pytest.param(
            "x + (2 * 3)",
            BinaryOp(
                token=Parser_tok.Plus,
                left_child=Value(
                    token=Parser_tok.Ident,
                    value="x",
                    lexer_tok=Lexer_tok(Lexer_type.IDENT, "x", 0),
                ),
                right_child=Constant(
                    value=6,
                    source=BinaryOp(
                        token=Parser_tok.Mult,
                        left_child=Value(
                            token=Parser_tok.Int,
                            value=2,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "2", 5),
                        ),
                        right_child=Value(
                            token=Parser_tok.Int,
                            value=3,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "3", 9),
                        ),
                        lexer_tok=Lexer_tok(Lexer_type.STAR, "*", 7),
                    ),
                ),
                lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 2),
            ),
            id="mixed_binary_right_folded",
        ),
        pytest.param(
            "-(x + 2)",
            UnaryOp(
                token=Parser_tok.UnMinus,
                child=BinaryOp(
                    token=Parser_tok.Plus,
                    left_child=Value(
                        token=Parser_tok.Ident,
                        value="x",
                        lexer_tok=Lexer_tok(Lexer_type.IDENT, "x", 2),
                    ),
                    right_child=Constant(
                        value=2,
                        source=Value(
                            token=Parser_tok.Int,
                            value=2,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "2", 6),
                        ),
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 4),
                ),
                lexer_tok=Lexer_tok(Lexer_type.MINUS, "-", 0),
            ),
            id="unary_mixed_inner"
        ),
        pytest.param(
            "[1, x + 2, 3 * 4]",
            Collection(
                token=Parser_tok.List,
                collection=[
                    Constant(
                        value=1,
                        source=Value(
                            token=Parser_tok.Int,
                            value=1,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "1", 1),
                        ),
                    ),
                    BinaryOp(
                        token=Parser_tok.Plus,
                        left_child=Value(
                            token=Parser_tok.Ident,
                            value="x",
                            lexer_tok=Lexer_tok(Lexer_type.IDENT, "x", 4),
                        ),
                        right_child=Constant(
                            value=2,
                            source=Value(
                                token=Parser_tok.Int,
                                value=2,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "2", 8),
                            ),
                        ),
                        lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 6),
                    ),
                    Constant(
                        value=12,
                        source=BinaryOp(
                            token=Parser_tok.Mult,
                            left_child=Value(
                                token=Parser_tok.Int,
                                value=3,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "3", 11),
                            ),
                            right_child=Value(
                                token=Parser_tok.Int,
                                value=4,
                                lexer_tok=Lexer_tok(Lexer_type.INT, "4", 15),
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.STAR, "*", 13),
                        ),
                    ),
                ],
                brackets=(
                    Lexer_tok(Lexer_type.LSQB, '[', 0),
                    Lexer_tok(Lexer_type.RSQB, ']', 16)
                )
            ),
            id="list_partial_folded_complex"
        ),
        pytest.param(
            "1 < x < 3 <= 4",
            CompareNode(
                operators=[
                    (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, "<", 2)]),
                    (Parser_tok.Lt, [Lexer_tok(Lexer_type.LT, "<", 6)]),
                    (Parser_tok.Le, [Lexer_tok(Lexer_type.LE, "<=", 10)]),
                ],
                operands=[
                    Constant(
                        value=1,
                        source=Value(
                            token=Parser_tok.Int,
                            value=1,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "1", 0),
                        ),
                    ),
                    Value(
                        token=Parser_tok.Ident,
                        value="x",
                        lexer_tok=Lexer_tok(Lexer_type.IDENT, "x", 4),
                    ),
                    Constant(
                        value=3,
                        source=Value(
                            token=Parser_tok.Int,
                            value=3,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "3", 8),
                        ),
                    ),
                    Constant(
                        value=4,
                        source=Value(
                            token=Parser_tok.Int,
                            value=4,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "4", 13),
                        ),
                    ),
                ],
            ),
            id="compare_mixed_complex",
        ),
        pytest.param(
            "((1 + 2) * (3 + 4)) == (21)",
            Constant(
                value=True,
                source=CompareNode(
                    operands=[
                        BinaryOp(
                            token=Parser_tok.Mult,
                            left_child=BinaryOp(
                                token=Parser_tok.Plus,
                                left_child=Value(
                                    token=Parser_tok.Int,
                                    value=1,
                                    lexer_tok=Lexer_tok(Lexer_type.INT, "1", 2),
                                ),
                                right_child=Value(
                                    token=Parser_tok.Int,
                                    value=2,
                                    lexer_tok=Lexer_tok(Lexer_type.INT, "2", 6),
                                ),
                                lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 4),
                            ),
                            right_child=BinaryOp(
                                token=Parser_tok.Plus,
                                left_child=Value(
                                    token=Parser_tok.Int,
                                    value=3,
                                    lexer_tok=Lexer_tok(Lexer_type.INT, "3", 12),
                                ),
                                right_child=Value(
                                    token=Parser_tok.Int,
                                    value=4,
                                    lexer_tok=Lexer_tok(Lexer_type.INT, "4", 16),
                                ),
                                lexer_tok=Lexer_tok(Lexer_type.PLUS, "+", 14),
                            ),
                            lexer_tok=Lexer_tok(Lexer_type.STAR, "*", 9),
                        ),
                        Value(
                            token=Parser_tok.Int,
                            value=21,
                            lexer_tok=Lexer_tok(Lexer_type.INT, "21", 24),
                        ),
                    ],
                    operators=[
                        (Parser_tok.Eq, [Lexer_tok(Lexer_type.EQ, "==", 20)]),
                    ],
                ),
            ),
            id="compare_full_arith_eq"
        ),
        pytest.param(
            "True or x",
            Constant(
                value=True,
                source=BinaryOp(
                    token=Parser_tok.Or,
                    left_child=Value(
                        token=Parser_tok.Bool,
                        value=True,
                        lexer_tok=Lexer_tok(Lexer_type.BOOL, "True", 0),
                    ),
                    right_child=Value(
                        token=Parser_tok.Ident,
                        value="x",
                        lexer_tok=Lexer_tok(Lexer_type.IDENT, "x", 8),
                    ),
                    lexer_tok=Lexer_tok(Lexer_type.OR, "or", 5),
                ),
            ),
            id="binary_short_circuit"
        )
    ]
)
def test_complex_ConstantFolder(expr: str, expect: nodes):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    assert ConstantFolder().fold(ast) == expect
