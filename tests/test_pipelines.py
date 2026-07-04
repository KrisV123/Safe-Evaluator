import pytest
import json

from evaluator.pipelines import build_isolated, evaluate_isolated
from evaluator.types import (
    nodes, Parser_tok, Constant, atom_types,
    BinaryOp, UnaryOp, Value, Collection, CompareNode, Lexer_tok, Lexer_type
)

class Test_build_isolated:

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
    def test_build_isolated_basic(self, expr: str, expect: nodes):
        ast = build_isolated(expr, r'{}')
        assert ast == expect

    @pytest.mark.parametrize(
        "expr, types, expect",
        [
            pytest.param(
                "x",
                '{"x": "int"}',
                Value(Parser_tok.Ident, "x", Lexer_tok(Lexer_type.IDENT, 'x', 0)),
                id="ident"
            ),
            pytest.param(
                "x + 6",
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
                '{"x": "int"}',
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
    def test_build_isolated_complex(self, expr: str, types: str, expect: nodes):
        ast = build_isolated(expr, types)
        assert ast == expect


class Test_evaluate_isolated:

    @pytest.mark.parametrize(
        "expr, vvars",
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
    def test_evaluate_isolated_basic(self, expr: str, vvars: dict[str, atom_types]):
        ans = evaluate_isolated(expr, json.dumps(vvars))
        expect = eval(expr, vvars)
        assert ans == expect

    @pytest.mark.parametrize(
        "expr, vvars",
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
    def test_evaluate_isolated_complex_expression(self, expr: str, vvars: dict[str, atom_types]):
        ans = evaluate_isolated(expr, json.dumps(vvars))
        expect = eval(expr, vvars)
        assert ans == expect
