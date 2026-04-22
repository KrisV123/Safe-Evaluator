import pytest #type:ignore[import-not-found]
from types import NoneType
from evaluator.literal_parser import Lexer, Parser, TypeChecker, ConstantFolder, evaluate
from evaluator.constants import (
    op_table, op_type_table,
    atom_types, Lexer_type, nodes, Parser_tok,
    Lexer_tok, BinaryOp, UnaryOp, Value, Collection, CompareNode, Constant
) 

from evaluator.constants import nodes

class Test_Lexer:

    @pytest.mark.parametrize(
        'op, expect',
        [
            ('==', [Lexer_tok(Lexer_type.EQ, '==', 0), Lexer_tok(Lexer_type.EOF, '$', 2)]),
            ('!=', [Lexer_tok(Lexer_type.NE, '!=', 0), Lexer_tok(Lexer_type.EOF, '$', 2)]),
            ('<=', [Lexer_tok(Lexer_type.LE, '<=', 0), Lexer_tok(Lexer_type.EOF, '$', 2)]),
            ('<',  [Lexer_tok(Lexer_type.LT, '<', 0),  Lexer_tok(Lexer_type.EOF, '$', 1)]),
            ('>=', [Lexer_tok(Lexer_type.GE, '>=', 0), Lexer_tok(Lexer_type.EOF, '$', 2)]),
            ('>',  [Lexer_tok(Lexer_type.GT, '>', 0),  Lexer_tok(Lexer_type.EOF, '$', 1)]),
            ('+',  [Lexer_tok(Lexer_type.PLUS, '+', 0),  Lexer_tok(Lexer_type.EOF, '$', 1)]),
            ('-',  [Lexer_tok(Lexer_type.MINUS, '-', 0),  Lexer_tok(Lexer_type.EOF, '$', 1)]),
            ('**', [Lexer_tok(Lexer_type.DSTAR, '**', 0), Lexer_tok(Lexer_type.EOF, '$', 2)]),
            ('*',  [Lexer_tok(Lexer_type.STAR, '*', 0),  Lexer_tok(Lexer_type.EOF, '$', 1)]),
            ('/',  [Lexer_tok(Lexer_type.SLASH, '/', 0),  Lexer_tok(Lexer_type.EOF, '$', 1)]),
            ('//', [Lexer_tok(Lexer_type.DSLASH, '//', 0), Lexer_tok(Lexer_type.EOF, '$', 2)]),
            ('%',  [Lexer_tok(Lexer_type.PERCENT, '%', 0),  Lexer_tok(Lexer_type.EOF, '$', 1)]),
        ],
        ids = ['==', '!=', '<=', '<', '>=', '>', '+', '-', '**', '*', '/', '//', '%']
    )
    def test_all_ops(self, op: str, expect: list[Lexer_tok]):
        assert Lexer(op).tokenize() == expect

    @pytest.mark.parametrize(
        'string, expect',
        [
            ("'ahoj'", [Lexer_tok(Lexer_type.STR, "'ahoj'", 0), Lexer_tok(Lexer_type.EOF, '$', 6)]),
            ('"ahoj"', [Lexer_tok(Lexer_type.STR, '"ahoj"', 0), Lexer_tok(Lexer_type.EOF, '$', 6)]),
            ("''",     [Lexer_tok(Lexer_type.STR, "''", 0),     Lexer_tok(Lexer_type.EOF, '$', 2)]),
            ('""',     [Lexer_tok(Lexer_type.STR, '""', 0),     Lexer_tok(Lexer_type.EOF, '$', 2)]),
            ("'and or + -'", [Lexer_tok(Lexer_type.STR, "'and or + -'", 0), Lexer_tok(Lexer_type.EOF, '$', 12)]),
        ],
        ids = [
            'single_quote', 'double_quote',
            'empty_string_1', 'empty_string_2',
            'operators in str'
        ]
    )
    def test_strings(self, string: str, expect: list[Lexer_tok]):
        assert Lexer(string).tokenize() == expect

    @pytest.mark.parametrize(
        "string, error",
        [
            ("'awd", 'operator does not exist. POS: 0'),
            ("awd'", 'operator does not exist. POS: 3'),
            ('"awd', 'operator does not exist. POS: 0'),
            ('awd"', 'operator does not exist. POS: 3')
        ],
        ids=['prefix_single', 'suffix_single', 'prefix_double', 'suffix_double']
    )
    def test_wrong_string(self, string: str, error: str):
        with pytest.raises(SyntaxError, match=error):
            Lexer(string).tokenize()

    @pytest.mark.parametrize(
        'bracket, expect',
        [
            ('(', [Lexer_tok(Lexer_type.LPAR, '(', 0),  Lexer_tok(Lexer_type.EOF, '$', 1)]),
            (')', [Lexer_tok(Lexer_type.RPAR, ')', 0), Lexer_tok(Lexer_type.EOF, '$', 1)]),
            ('[', [Lexer_tok(Lexer_type.LSQB, '[', 0),   Lexer_tok(Lexer_type.EOF, '$', 1)]),
            (']', [Lexer_tok(Lexer_type.RSQB, ']', 0),  Lexer_tok(Lexer_type.EOF, '$', 1)]),
            (',', [Lexer_tok(Lexer_type.COMMA, ',', 0),       Lexer_tok(Lexer_type.EOF, '$', 1)]),
        ],
        ids=['(', ')', '[', ']', ',']
    )
    def test_brackets(self, bracket: str, expect: list[Lexer_tok]):
        assert Lexer(bracket).tokenize() == expect

    @pytest.mark.parametrize(
        'number, expect',
        [
            ('0',  [Lexer_tok(Lexer_type.INT, '0', 0),  Lexer_tok(Lexer_type.EOF, '$', 1)]),
            ('1',  [Lexer_tok(Lexer_type.INT, '1', 0),  Lexer_tok(Lexer_type.EOF, '$', 1)]),
            ('10', [Lexer_tok(Lexer_type.INT, '10', 0), Lexer_tok(Lexer_type.EOF, '$', 2)]),
            ('123456789', [Lexer_tok(Lexer_type.INT, '123456789', 0), Lexer_tok(Lexer_type.EOF, '$', 9)]),
            ('0 1', [
                Lexer_tok(Lexer_type.INT, '0', 0),
                Lexer_tok(Lexer_type.INT, '1', 2),
                Lexer_tok(Lexer_type.EOF, '$', 3)
            ]),

            ('0.1',    [Lexer_tok(Lexer_type.FLOAT, '0.1', 0),    Lexer_tok(Lexer_type.EOF, '$', 3)]),
            ('6.7',    [Lexer_tok(Lexer_type.FLOAT, '6.7', 0),    Lexer_tok(Lexer_type.EOF, '$', 3)]),
            ('0.1234', [Lexer_tok(Lexer_type.FLOAT, '0.1234', 0), Lexer_tok(Lexer_type.EOF, '$', 6)]),
            ('123.45', [Lexer_tok(Lexer_type.FLOAT, '123.45', 0), Lexer_tok(Lexer_type.EOF, '$', 6)]),
            ('.1',     [Lexer_tok(Lexer_type.FLOAT, '.1', 0),     Lexer_tok(Lexer_type.EOF, '$', 2)]),
            ('.123',   [Lexer_tok(Lexer_type.FLOAT, '.123', 0),   Lexer_tok(Lexer_type.EOF, '$', 4)]),
            ('0.1.2', [
                Lexer_tok(Lexer_type.FLOAT, '0.1', 0),
                Lexer_tok(Lexer_type.FLOAT, '.2', 3),
                Lexer_tok(Lexer_type.EOF, '$', 5)
            ])
        ],
        ids=[
            '0', '1', '10', '123456789', '0 1', '0.1', '6.7', '0.1234', '123.45', '.1', '.123', '0.1.2'
        ]
    )
    def test_numbers(self, number: str, expect: list[Lexer_tok]):
        assert Lexer(number).tokenize() == expect

    @pytest.mark.parametrize(
        'number, error',
        [
            ('01', "Numbers can't start with unnecessary zeroes. POS: 0"),
            ('01.2', "Numbers can't start with unnecessary zeroes. POS: 0"),
            ('.', 'operator does not exist. POS: 0')
        ],
        ids=['01', '01.2', '.']
    )
    def test_wrong_num(self, number: str, error: str):
        with pytest.raises(SyntaxError, match=error):
            Lexer(number).tokenize()

    @pytest.mark.parametrize(
        'ident, expect',
        [
            ('vars',    [Lexer_tok(Lexer_type.IDENT, 'vars', 0),    Lexer_tok(Lexer_type.EOF, '$', 4)]),
            ('var_1',   [Lexer_tok(Lexer_type.IDENT, 'var_1', 0),   Lexer_tok(Lexer_type.EOF, '$', 5)]),
            ('var_and', [Lexer_tok(Lexer_type.IDENT, 'var_and', 0), Lexer_tok(Lexer_type.EOF, '$', 7)]),
            ('and_var', [Lexer_tok(Lexer_type.IDENT, 'and_var', 0), Lexer_tok(Lexer_type.EOF, '$', 7)])
        ],
        ids=['sanity', 'with_num', 'operator_suffix', 'operator_prefix']
    )
    def test_identificator(self, ident: str, expect: list[Lexer_tok]):
        assert Lexer(ident).tokenize() == expect

    @pytest.mark.parametrize(
        'ident',
        [('=var')],
        ids=['equivalency_prefix']
    )
    def test_wrong_identificators(self, ident: str):
        with pytest.raises(SyntaxError, match='operator does not exist. POS: 0'):
            Lexer(ident).tokenize()

    @pytest.mark.parametrize(
        "string, expect",
        [
            ('None', [Lexer_tok(Lexer_type.NONE, 'None', 0), Lexer_tok(Lexer_type.EOF, '$', 4)]),
            (',', [Lexer_tok(Lexer_type.COMMA, ',', 0), Lexer_tok(Lexer_type.EOF, '$', 1)])
        ],
        ids=['None', ',']
    )
    def test_extra(self, string: str, expect: list[Lexer_tok]):
        assert Lexer(string).tokenize() == expect

    @pytest.mark.parametrize(
        "string, expect",
        [
            (
                "5 == 5 None or awdawdaw==, 'awdaw' [dawda not 69.8 <[]('awdawd') True False",
                [
                    Lexer_tok(Lexer_type.INT, '5', 0),
                    Lexer_tok(Lexer_type.EQ, '==', 2),
                    Lexer_tok(Lexer_type.INT, '5', 5),
                    Lexer_tok(Lexer_type.NONE, 'None', 7),
                    Lexer_tok(Lexer_type.OR, 'or', 12),
                    Lexer_tok(Lexer_type.IDENT, 'awdawdaw', 15),
                    Lexer_tok(Lexer_type.EQ, '==', 23),
                    Lexer_tok(Lexer_type.COMMA, ',', 25),
                    Lexer_tok(Lexer_type.STR, "'awdaw'", 27),
                    Lexer_tok(Lexer_type.LSQB, '[', 35),
                    Lexer_tok(Lexer_type.IDENT, 'dawda', 36),
                    Lexer_tok(Lexer_type.NOT, 'not', 42),
                    Lexer_tok(Lexer_type.FLOAT, '69.8', 46),
                    Lexer_tok(Lexer_type.LT, '<', 51),
                    Lexer_tok(Lexer_type.LSQB, '[', 52),
                    Lexer_tok(Lexer_type.RSQB, ']', 53),
                    Lexer_tok(Lexer_type.LPAR, '(', 54),
                    Lexer_tok(Lexer_type.STR, "'awdawd'", 55),
                    Lexer_tok(Lexer_type.RPAR, ')', 63),
                    Lexer_tok(Lexer_type.BOOL, 'True', 65),
                    Lexer_tok(Lexer_type.BOOL, 'False', 70),
                    Lexer_tok(Lexer_type.EOF, '$', 75)
                ]
            ),
            (
                '< <= > >= == not',
                [   
                    Lexer_tok(Lexer_type.LT, '<', 0),
                    Lexer_tok(Lexer_type.LE, '<=', 2),
                    Lexer_tok(Lexer_type.GT, '>', 5),
                    Lexer_tok(Lexer_type.GE, '>=', 7),
                    Lexer_tok(Lexer_type.EQ, '==', 10),
                    Lexer_tok(Lexer_type.NOT, 'not', 13),
                    Lexer_tok(Lexer_type.EOF, '$', 16)
                ]
            ),
            (
                '[1,(5 and 6),True,]',
                [
                    Lexer_tok(Lexer_type.LSQB, '[', 0),
                    Lexer_tok(Lexer_type.INT, '1', 1),
                    Lexer_tok(Lexer_type.COMMA, ',', 2),
                    Lexer_tok(Lexer_type.LPAR, '(', 3),
                    Lexer_tok(Lexer_type.INT, '5', 4),
                    Lexer_tok(Lexer_type.AND, 'and', 6),
                    Lexer_tok(Lexer_type.INT, '6', 10),
                    Lexer_tok(Lexer_type.RPAR, ')', 11),
                    Lexer_tok(Lexer_type.COMMA, ',', 12),
                    Lexer_tok(Lexer_type.BOOL, 'True', 13),
                    Lexer_tok(Lexer_type.COMMA, ',', 17),
                    Lexer_tok(Lexer_type.RSQB, ']', 18),
                    Lexer_tok(Lexer_type.EOF, '$', 19)
                ]
            ),
            (
                '5**(not 1)*0<=5--6+6 in (8,(4%2),)',
                [
                    Lexer_tok(Lexer_type.INT, '5', 0),
                    Lexer_tok(Lexer_type.DSTAR, '**', 1),
                    Lexer_tok(Lexer_type.LPAR, '(', 3),
                    Lexer_tok(Lexer_type.NOT, 'not', 4),
                    Lexer_tok(Lexer_type.INT, '1', 8),
                    Lexer_tok(Lexer_type.RPAR, ')', 9),
                    Lexer_tok(Lexer_type.STAR, '*', 10),
                    Lexer_tok(Lexer_type.INT, '0', 11),
                    Lexer_tok(Lexer_type.LE, '<=', 12),
                    Lexer_tok(Lexer_type.INT, '5', 14),
                    Lexer_tok(Lexer_type.MINUS, '-', 15),
                    Lexer_tok(Lexer_type.MINUS, '-', 16),
                    Lexer_tok(Lexer_type.INT, '6', 17),
                    Lexer_tok(Lexer_type.PLUS, '+', 18),
                    Lexer_tok(Lexer_type.INT, '6', 19),
                    Lexer_tok(Lexer_type.IN, 'in', 21),
                    Lexer_tok(Lexer_type.LPAR, '(', 24),
                    Lexer_tok(Lexer_type.INT, '8', 25),
                    Lexer_tok(Lexer_type.COMMA, ',', 26),
                    Lexer_tok(Lexer_type.LPAR, '(', 27),
                    Lexer_tok(Lexer_type.INT, '4', 28),
                    Lexer_tok(Lexer_type.PERCENT, '%', 29),
                    Lexer_tok(Lexer_type.INT, '2', 30),
                    Lexer_tok(Lexer_type.RPAR, ')', 31),
                    Lexer_tok(Lexer_type.COMMA, ',', 32),
                    Lexer_tok(Lexer_type.RPAR, ')', 33),
                    Lexer_tok(Lexer_type.EOF, '$', 34)
                ]
            )
        ],
        ids=[
            'sanity',
            'sanity_2',
            'list',
            'without_spaces'
        ]
    )
    def test_combinations(self, string: str, expect: list[Lexer_tok]):
        assert Lexer(string).tokenize() == expect


class Test_Parser:

    @pytest.mark.parametrize(
        "expr, expect",
        [
            (
                'True or False',
                BinaryOp(
                    token=Parser_tok.Or,
                    left_child=Value(Parser_tok.Bool, True),
                    right_child=Value(Parser_tok.Bool, False)
                )
            ),
            (
                'True or False or True',
                BinaryOp(
                    token=Parser_tok.Or,
                    left_child=BinaryOp(
                        token=Parser_tok.Or,
                        left_child=Value(Parser_tok.Bool, True),
                        right_child=Value(Parser_tok.Bool, False)
                    ),
                    right_child=Value(Parser_tok.Bool, True)
                )
            )
        ],
        ids = ['sanity', 'consecutive']
    )
    def test_disjunction(self, expr: str, expect: nodes):
        tokens = Lexer(expr).tokenize()
        assert Parser(tokens).parse() == expect

    @pytest.mark.parametrize(
        "expr, expect",
        [
            (
                'True and False',
                BinaryOp(
                    token=Parser_tok.And,
                    left_child=Value(Parser_tok.Bool, True),
                    right_child=Value(Parser_tok.Bool, False)
                )
            ),
            (
                'True and False and True',
                BinaryOp(
                    token=Parser_tok.And,
                    left_child=BinaryOp(
                        token=Parser_tok.And,
                        left_child=Value(Parser_tok.Bool, True),
                        right_child=Value(Parser_tok.Bool, False)),
                    right_child=Value(Parser_tok.Bool, True)
                )
            )
        ],
        ids=['sanity', 'consecutive']
    )
    def test_conjunction(self, expr: str, expect: nodes):
        tokens = Lexer(expr).tokenize()
        assert Parser(tokens).parse() == expect

    @pytest.mark.parametrize(
        "expr, expect",
        [
            (
                '5 in [5, 6]',
                CompareNode(
                    operators=[Parser_tok.In],
                    operands=[
                        Value(Parser_tok.Int, 5),
                        Collection(
                            typ = list,
                            collection=[
                                Value(Parser_tok.Int, 5),
                                Value(Parser_tok.Int, 6)
                            ]
                        )
                    ]
                )
            ),
            (
                '5 not in [5, 6]',
                CompareNode(
                    operators=[Parser_tok.NotIn],
                    operands=[
                        Value(Parser_tok.Int, 5),
                        Collection(
                            typ = list,
                            collection=[
                                Value(Parser_tok.Int, 5),
                                Value(Parser_tok.Int, 6)
                            ]
                        )
                    ]
                )
            ),
            (
                '6 == 7',
                CompareNode(
                    operators=[Parser_tok.Eq],
                    operands=[
                        Value(Parser_tok.Int, 6),
                        Value(Parser_tok.Int, 7)
                    ]
                )
            ),
            (
                '6 != 7',
                CompareNode(
                    operators=[Parser_tok.Ne],
                    operands=[
                        Value(Parser_tok.Int, 6),
                        Value(Parser_tok.Int, 7)
                    ]
                )
            ),
            (
                '6 >= 7',
                CompareNode(
                    operators=[Parser_tok.Ge],
                    operands=[
                        Value(Parser_tok.Int, 6),
                        Value(Parser_tok.Int, 7)
                    ]
                )
            ),
            (
                '6 <= 7',
                CompareNode(
                    operators=[Parser_tok.Le],
                    operands=[
                        Value(Parser_tok.Int, 6),
                        Value(Parser_tok.Int, 7)
                    ]
                )
            ),
            (
                '6 > 7',
                CompareNode(
                    operators=[Parser_tok.Gt],
                    operands=[
                        Value(Parser_tok.Int, 6),
                        Value(Parser_tok.Int, 7)
                    ]
                )
            ),
            (
                '6 < 7',
                CompareNode(
                    operators=[Parser_tok.Lt],
                    operands=[
                        Value(Parser_tok.Int, 6),
                        Value(Parser_tok.Int, 7)
                    ]
                )
            ),
            (
                '6 is 7',
                CompareNode(
                    operators=[Parser_tok.Is],
                    operands=[
                        Value(Parser_tok.Int, 6),
                        Value(Parser_tok.Int, 7)
                    ]
                )
            ),
            (
                '6 is not 7',
                CompareNode(
                    operators=[Parser_tok.IsNot],
                    operands=[
                        Value(Parser_tok.Int, 6),
                        Value(Parser_tok.Int, 7)
                    ]
                )
            ),
        ],
        ids=['in', 'not_in', 'equal', 'not_equal', 'large_equal', 'low_equal', 'large', 'low', 'is', 'is_not']
    )
    def test_compare_operator(self, expr: str, expect: nodes):
        tokens = Lexer(expr).tokenize()
        assert Parser(tokens).parse() == expect

    @pytest.mark.parametrize(
        "expr, expect",
        [
            (
                'not True',
                UnaryOp(
                    token=Parser_tok.Not,
                    child=Value(Parser_tok.Bool, True)
                )
            ),
            (
                'not not True',
                UnaryOp(
                    token=Parser_tok.Not,
                    child=UnaryOp(
                        token=Parser_tok.Not,
                        child=Value(Parser_tok.Bool, True)
                    )
                )
            )
        ],
        ids=['sanity', 'consecutive']
    )
    def test_negation(self, expr: str, expect: nodes):
        tokens = Lexer(expr).tokenize()
        assert Parser(tokens).parse() == expect

    @pytest.mark.parametrize(
        "expr, expect",
        [
            (
                "4 + 5",
                BinaryOp(
                    token=Parser_tok.Plus,
                    left_child=Value(Parser_tok.Int, 4),
                    right_child=Value(Parser_tok.Int, 5)
                )
            ),
            (
                "4 - 5",
                BinaryOp(
                    token=Parser_tok.Minus,
                    left_child=Value(Parser_tok.Int, 4),
                    right_child=Value(Parser_tok.Int, 5)
                )
            ),
            (
                "6 + 7 - 9",
                BinaryOp(
                    token=Parser_tok.Minus,
                    left_child=BinaryOp(
                        token=Parser_tok.Plus,
                        left_child=Value(Parser_tok.Int, 6),
                        right_child=Value(Parser_tok.Int, 7)),
                    right_child=Value(Parser_tok.Int, 9))
            )
        ],
        ids=['+', '-', 'consecutive']
    )
    def test_low_ord_operator(self, expr: str, expect: nodes):
        tokens = Lexer(expr).tokenize()
        assert Parser(tokens).parse() == expect

    @pytest.mark.parametrize(
        "expr, expect",
        [
            (
                "6 // 7",
                BinaryOp(
                    token=Parser_tok.FloorDiv,
                    left_child=Value(Parser_tok.Int, 6),
                    right_child=Value(Parser_tok.Int, 7)
                )
            ),
            (
                "6 / 7",
                BinaryOp(
                    token=Parser_tok.TrueDiv,
                    left_child=Value(Parser_tok.Int, 6),
                    right_child=Value(Parser_tok.Int, 7)
                )
            ),
            (
                "6 % 7",
                BinaryOp(
                    token=Parser_tok.Mod,
                    left_child=Value(Parser_tok.Int, 6),
                    right_child=Value(Parser_tok.Int, 7)
                )
            ),
            (
                "6 * 7",
                BinaryOp(
                    token=Parser_tok.Mult,
                    left_child=Value(Parser_tok.Int, 6),
                    right_child=Value(Parser_tok.Int, 7)
                )
            )
        ],
        ids=['floor_div', 'true_div', 'modulo', 'multiplication']
    )
    def test_high_ord_operator(self, expr: str, expect: nodes):
        tokens = Lexer(expr).tokenize()
        assert Parser(tokens).parse() == expect

    @pytest.mark.parametrize(
        "expr, expect",
        [
            (
                "+6",
                UnaryOp(
                    token=Parser_tok.UnPlus,
                    child=Value(Parser_tok.Int, 6)
                )
            ),
            (
                "-6",
                UnaryOp(
                    token=Parser_tok.UnMinus,
                    child=Value(Parser_tok.Int, 6)
                ),
            ),
            (
                "+-6",
                UnaryOp(
                    token=Parser_tok.UnPlus,
                    child=UnaryOp(
                        token=Parser_tok.UnMinus,
                        child=Value(Parser_tok.Int, 6)
                    )
                )
            )
        ],
        ids=['+', '-', 'consecutive']
    )
    def test_factor(self, expr: str, expect: nodes):
        tokens = Lexer(expr).tokenize()
        assert Parser(tokens).parse() == expect

    @pytest.mark.parametrize(
        "expr, expect",
        [
            (
                "6 ** 7",
                BinaryOp(
                    token=Parser_tok.Power,
                    left_child=Value(Parser_tok.Int, 6),
                    right_child=Value(Parser_tok.Int, 7)
                )
            ),
            (
                "6 ** 7 ** 9",
                BinaryOp(
                    token=Parser_tok.Power,
                    left_child=Value(Parser_tok.Int, 6),
                    right_child=BinaryOp(
                        token=Parser_tok.Power,
                        left_child=Value(Parser_tok.Int, 7),
                        right_child=Value(Parser_tok.Int, 9)
                    )
                )
            )
        ],
        ids=['sanity', 'consecutive']
    )
    def test_power(self, expr: str, expect: nodes):
        tokens = Lexer(expr).tokenize()
        assert Parser(tokens).parse() == expect

    @pytest.mark.parametrize(
        "expr, expect",
        [
            ("[]", Collection(typ=list, collection=[])),
            (
                "[1]",
                Collection(
                    typ=list,
                    collection=[
                        Value(Parser_tok.Int, 1)
                    ]
                )
            ),
            (
                "[1,]",
                Collection(
                    typ=list,
                    collection=[
                        Value(Parser_tok.Int, 1)
                    ]
                )
            ),
            (
                "[1,2]",
                Collection(
                    typ=list,
                    collection=[
                        Value(Parser_tok.Int, 1),
                        Value(Parser_tok.Int, 2)
                    ]
                )
            ),
            (
                "[[]]",
                Collection(
                    typ=list,    
                    collection=[
                        Collection(typ=list, collection=[])
                    ]
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
            ("()", Collection(typ=tuple, collection=[])),
            (
                "(1,)",
                Collection(
                    typ=tuple,
                    collection=[
                        Value(Parser_tok.Int, 1)
                    ]
                )
            ),
            (
                "(1,2)",
                Collection(
                    typ=tuple,
                    collection=[
                        Value(Parser_tok.Int, 1),
                        Value(Parser_tok.Int, 2)
                    ]
                )
            ),
            (
                "(1,2,)",
                Collection(
                    typ=tuple,
                    collection=[
                        Value(Parser_tok.Int, 1),
                        Value(Parser_tok.Int, 2)
                    ]
                )
            ),
            (
                "((),)",
                Collection(
                    typ=tuple,    
                    collection=[
                        Collection(typ=tuple, collection=[])
                    ]
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
    def test_container(self, expr: str, expect: nodes | Parser.Failure):
        tokens = Lexer(expr).tokenize()
        assert Parser(tokens).parse() == expect
   
    @pytest.mark.parametrize(
        "expr, expect",
        [
            (
                "(6)",
                Value(Parser_tok.Int, 6)
            ),
            (
                "((6))",
                Value(Parser_tok.Int, 6)
            ),
            (
                "6 ** (1 + 2)",
                BinaryOp(
                    token=Parser_tok.Power,
                    left_child=Value(Parser_tok.Int, 6),
                    right_child=BinaryOp(
                        token=Parser_tok.Plus,
                        left_child=Value(Parser_tok.Int, 1),
                        right_child=Value(Parser_tok.Int, 2)
                    )
                )
            )
        ],
        ids=['sanity', 'double_brackets', 'priority_test']
    )
    def test_brackets(self, expr: str, expect: nodes):
        tokens = Lexer(expr).tokenize()
        assert Parser(tokens).parse() == expect

    @pytest.mark.parametrize(
        "expr, expect",
        [
            ("6",    Value(Parser_tok.Int, 6)),
            ("6.7",  Value(Parser_tok.Float, 6.7)),
            ("True", Value(Parser_tok.Bool, True)),
            ("wasd", Value(Parser_tok.Ident, 'wasd')),
            ("'wa'", Value(Parser_tok.Str, 'wa')),
            ("None", Value(Parser_tok.None_, None)),
            ("[]", Collection(typ=list, collection=[]))
        ],
        ids=['int', 'float', 'bool', 'ident', 'string', 'None', 'list']
    )
    def test_atom(self, expr: str, expect: nodes):
        tokens = Lexer(expr).tokenize()
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
                            child=Value(Parser_tok.Bool, True)
                        ),
                        right_child=Value(Parser_tok.Bool, False)
                    ),
                    right_child=BinaryOp(
                        token=Parser_tok.And,
                        left_child=BinaryOp(
                            token=Parser_tok.Power,
                            left_child=Value(Parser_tok.Int, 6),
                            right_child=Value(Parser_tok.Ident, 'tvoja_mama')
                        ),
                        right_child=UnaryOp(
                            token=Parser_tok.UnMinus,
                            child=Value(Parser_tok.Int, 7)
                        )
                    )
                )
            ),
            (
                "6 and (7 or 6) and 9",
                BinaryOp(
                    token=Parser_tok.And,
                    left_child=BinaryOp(
                        token=Parser_tok.And,
                        left_child=Value(Parser_tok.Int, 6),
                        right_child=BinaryOp(
                            token=Parser_tok.Or,
                            left_child=Value(Parser_tok.Int, 7),
                            right_child=Value(Parser_tok.Int, 6)
                        )
                    ),
                    right_child=Value(Parser_tok.Int, 9)
                )
            ),
            (
                "tvoja_mama in (6 * 2, -7, 6 <= 2)",
                CompareNode(operators=[Parser_tok.In],
                    operands=[
                        Value(Parser_tok.Ident, 'tvoja_mama'),
                        Collection(
                            typ=tuple,
                            collection=[
                                BinaryOp(
                                    token=Parser_tok.Mult,
                                    left_child=Value(Parser_tok.Int, 6),
                                    right_child=Value(Parser_tok.Int, 2)
                                ),
                                UnaryOp(
                                    token=Parser_tok.UnMinus,
                                    child=Value(Parser_tok.Int, 7)
                                ),
                                CompareNode(
                                    operators=[Parser_tok.Le],
                                    operands=[
                                        Value(Parser_tok.Int, 6),
                                        Value(Parser_tok.Int, 2)
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ),
            (
                "5 <= 6 and 6 == tvoja_mama",
                BinaryOp(
                    token=Parser_tok.And,
                    left_child=CompareNode(
                        operators=[Parser_tok.Le],
                        operands=[
                            Value(Parser_tok.Int, 5),
                            Value(Parser_tok.Int, 6)
                        ]
                    ),
                    right_child=CompareNode(
                        operators=[Parser_tok.Eq],
                        operands=[
                            Value(Parser_tok.Int, 6),
                            Value(Parser_tok.Ident, 'tvoja_mama')
                        ]
                    )
                )
            ),
            (
                "True and not not True",
                BinaryOp(
                    token=Parser_tok.And,
                    left_child=Value(Parser_tok.Bool, True),
                    right_child=UnaryOp(
                        token=Parser_tok.Not,
                        child=UnaryOp(
                            token=Parser_tok.Not,
                            child=Value(Parser_tok.Bool, True)
                        )
                    )
                )
            ),
            (
                "(True or False) + 5 ** 6.8 ** (not 6.9)",
                BinaryOp(
                    token=Parser_tok.Plus,
                    left_child=BinaryOp(
                        token=Parser_tok.Or,
                        left_child=Value(Parser_tok.Bool, True),
                        right_child=Value(Parser_tok.Bool, False)),
                    right_child=BinaryOp(
                        token=Parser_tok.Power,
                        left_child=Value(Parser_tok.Int, 5),
                        right_child=BinaryOp(
                            token=Parser_tok.Power,
                            left_child=Value(Parser_tok.Float, 6.8),
                            right_child=UnaryOp(
                                token=Parser_tok.Not,
                                child=Value(Parser_tok.Float, 6.9)
                            )
                        )
                    )
                )
            ),
            (
                "6 not in (7,)",
                CompareNode(
                    operators=[Parser_tok.NotIn],
                    operands=[
                        Value(Parser_tok.Int, 6),
                        Collection(
                            typ=tuple,
                            collection=[Value(Parser_tok.Int, 7)]
                        )
                    ]
                )
            ),
            (
                "6 not in (7,) == 6",
                CompareNode(
                    operators=[Parser_tok.NotIn, Parser_tok.Eq],
                    operands=[
                        Value(Parser_tok.Int, 6),
                        Collection(
                            typ=tuple,
                            collection=[Value(Parser_tok.Int, 7)]
                        ),
                        Value(Parser_tok.Int, 6)
                    ]
                )
            ),
            (
                "tvoja_mamka is None",
                CompareNode(
                    operators=[Parser_tok.Is],
                    operands=[
                        Value(Parser_tok.Ident, 'tvoja_mamka'),
                        Value(Parser_tok.None_, None)
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
                            operators=[Parser_tok.Le],
                            operands=[
                                Value(Parser_tok.Int, 5),
                                Value(Parser_tok.Int, 5)
                            ]
                        ),
                        right_child=BinaryOp(
                            token=Parser_tok.Mod,
                            left_child=Value(Parser_tok.Int, 5),
                            right_child=Value(Parser_tok.Int, 5)
                        )
                    ),
                    right_child=CompareNode(
                        operators=[Parser_tok.In],
                        operands=[
                            Value(Parser_tok.Int, 5),
                            Collection(
                                typ=tuple,
                                collection=[
                                    Value(Parser_tok.Int, 1),
                                    Value(Parser_tok.Int, 2)
                                ]
                            )
                        ]
                    )
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
    def test_expressions(self, expr: str, expect: nodes):
        tokens = Lexer(expr).tokenize()
        assert Parser(tokens).parse() == expect


class Test_TypeChecker:

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
    def test_check_value(self, expr: str, typ: object):
        tokens = Lexer(expr).tokenize()
        ast = Parser(tokens).parse()
        assert not isinstance(ast, Parser.Failure)
        assert TypeChecker({}).check(ast) == typ

    @pytest.mark.parametrize(
        "expr, vars, typ",
        [
            pytest.param("var", {'var': 'asd'}, {str}, id="str"),
            pytest.param("var", {'var': 5}, {int}, id="int"),
            pytest.param("var", {'var': True}, {int}, id="bool_True"),
            pytest.param("var", {'var': False}, {int}, id="bool_False"),
            pytest.param("var", {'var': 5.2}, {float}, id="float"),
            pytest.param("var", {'var': None}, {NoneType}, id="NonType")
        ]
    )
    def test_check_value_identificators(self,
                                        expr: str,
                                        vars: dict[str, atom_types],
                                        typ: object):
        tokens = Lexer(expr).tokenize()
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
    def test_check_unaryop(self, expr: str, typ: object):
        tokens = Lexer(expr).tokenize()
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
    def test_check_binaryop(self, expr: str, typ: object):
        tokens = Lexer(expr).tokenize()
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
    def test_check_collection(self, expr: str, typ: object):
        tokens = Lexer(expr).tokenize()
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
    def test_comparenode(self, expr: str, typ: object):
        tokens = Lexer(expr).tokenize()
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
            ("('hello' + ('world' + '!')) or 8.5", {str, float}),
            (
                "1 + 'string'",
                TypeChecker.TypeFail(
                    failed_node=BinaryOp(
                        token=Parser_tok.Plus,
                        left_child=Value(Parser_tok.Int, 1),
                        right_child=Value(Parser_tok.Str, 'string')),
                    types=(int, str)
                )
            ),
            (
                "7 and ([1] + (2,3))",
                TypeChecker.TypeFail(
                    failed_node=BinaryOp(
                        token=Parser_tok.Plus,
                        left_child=Collection(
                            typ=list,
                            collection=[Value(Parser_tok.Int, 1)]
                        ),
                        right_child=Collection(
                            typ=tuple,
                            collection=[
                                Value(Parser_tok.Int, 2),
                                Value(Parser_tok.Int, 3)
                            ]
                        )
                    ),
                    types=(list, tuple)
                )
            )
        ]
    )
    def test_combinations(self, expr: str, typ: object):
        tokens = Lexer(expr).tokenize()
        ast = Parser(tokens).parse()
        assert not isinstance(ast, Parser.Failure)
        assert TypeChecker({"tvoja_mama": 5}).check(ast) == typ


class Test_Evaluator:
    
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
    def test_basic_expressions(self, expr: str, vars: dict[str, atom_types]):
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
    def test_complex_expressions(self, expr: str, vars: dict[str, atom_types]):
        assert evaluate(expr, vars) == eval(expr, vars)


class Test_ConstantFolder:

    @pytest.mark.parametrize(
        "expr, expect",
        [
            pytest.param("5 + 6", Constant(11), id="add"),
            pytest.param("10 - 3", Constant(7), id="sub"),
            pytest.param("4 * 7", Constant(28), id="mul"),
            pytest.param("8 / 2", Constant(4.0), id="div"),
            pytest.param("2 ** 3", Constant(8), id="pow"),
            pytest.param("-5", Constant(-5), id="unary_minus"),
            pytest.param("+5", Constant(5), id="unary_plus"),
            pytest.param("not True", Constant(False), id="unary_not"),
            pytest.param("(2 + 3) * 4", Constant(20), id="nested_arith"),
            pytest.param("[1, 2, 3]", Constant([1, 2, 3]), id="list"),
            pytest.param("(1, 2, 3)", Constant((1, 2, 3)), id="tuple"),
            pytest.param("[1 + 2, 3 * 4]", Constant([3, 12]), id="list_folded_items"),
            pytest.param("1 < 2", Constant(True), id="compare_lt"),
            pytest.param("1 < 2 < 3", Constant(True), id="chained_compare_true"),
            pytest.param("1 < 2 > 3", Constant(False), id="chained_compare_false"),
            pytest.param("1 == 1", Constant(True), id="compare_eq")
        ]
    )
    def test_basic_ConstantFolder(self, expr: str, expect: nodes):
        tokens = Lexer(expr).tokenize()
        ast = Parser(tokens).parse()
        assert not isinstance(ast, Parser.Failure)
        assert ConstantFolder().fold(ast) == expect
    
    @pytest.mark.parametrize(
        "expr, expect",
        [
            pytest.param(
                "x",
                Value(Parser_tok.Ident, "x"),
                id="ident"
            ),
            pytest.param(
                "x + 6",
                BinaryOp(
                    token=Parser_tok.Plus,
                    left_child=Value(Parser_tok.Ident, "x"),
                    right_child=Constant(6)
                ),
                id="mixed_add"
            ),
            pytest.param(
                "-x",
                UnaryOp(
                    token=Parser_tok.UnMinus,
                    child=Value(Parser_tok.Ident, "x")
                ),
                id="unary_ident"
            ),
            pytest.param(
                "[1, x, 3]",
                Collection(
                    typ=list,
                    collection=[
                        Constant(1),
                        Value(Parser_tok.Ident, "x"),
                        Constant(3),
                    ],
                ),
                id="list_mixed"
            ),
            pytest.param(
                "(1, x, 3)",
                Collection(
                    typ=tuple,
                    collection=[
                        Constant(1),
                        Value(Parser_tok.Ident, "x"),
                        Constant(3),
                    ],
                ),
                id="tuple_mixed"
            ),
            pytest.param(
                "1 < x < 3",
                CompareNode(
                    operands=[
                        Constant(1),
                        Value(Parser_tok.Ident, "x"),
                        Constant(3),
                    ],
                    operators=[Parser_tok.Lt, Parser_tok.Lt],
                ),
                id="compare_mixed"
            ),
            pytest.param(
                "(1 + 2) < (2 + 3)",
                Constant(True),
                id="compare_folded"
            ),
            pytest.param(
                "5 + 6 * 2",
                Constant(17),
                id="arith_precedence"
            ),
            pytest.param(
                "(5 + 6) * 2",
                Constant(22),
                id="arith_parentheses"
            ),
            pytest.param(
                "-(3 + 4)",
                Constant(-7),
                id="unary_minus_nested"
            ),
            pytest.param(
                "+(2 * 3 + 4)",
                Constant(10),
                id="unary_plus_nested"
            ),
            pytest.param(
                "not (1 < 2)",
                Constant(False),
                id="unary_not_compare"
            ),
            pytest.param(
                "[1 + 2, 3 * 4, -(5 - 7)]",
                Constant([3, 12, 2]),
                id="list_all_folded_complex"
            ),
            pytest.param(
                "([1 + 2, 3], (4 * 5, 6 + 7))",
                Constant(([3, 3], (20, 13))),
                id="nested_collections"
            ),
            pytest.param(
                "1 < 2 < 3 < 4",
                Constant(True),
                id="chained_compare_long_true"
            ),
            pytest.param(
                "(1 + 2) < (3 * 2) <= (8 - 2)",
                Constant(True),
                id="mixed_compare_folded"
            ),
            pytest.param(
                "x + (2 * 3)",
                BinaryOp(
                    token=Parser_tok.Plus,
                    left_child=Value(Parser_tok.Ident, "x"),
                    right_child=Constant(6),
                ),
                id="mixed_binary_right_folded"
            ),
            pytest.param(
                "-(x + 2)",
                UnaryOp(
                    token=Parser_tok.UnMinus,
                    child=BinaryOp(
                        token=Parser_tok.Plus,
                        left_child=Value(Parser_tok.Ident, "x"),
                        right_child=Constant(2),
                    ),
                ),
                id="unary_mixed_inner"
            ),
            pytest.param(
                "[1, x + 2, 3 * 4]",
                Collection(
                    typ=list,
                    collection=[
                        Constant(1),
                        BinaryOp(
                            token=Parser_tok.Plus,
                            left_child=Value(Parser_tok.Ident, "x"),
                            right_child=Constant(2),
                        ),
                        Constant(12),
                    ],
                ),
                id="list_partial_folded_complex"
            ),
            pytest.param(
                "1 < x < 3 <= 4",
                CompareNode(
                    operands=[
                        Constant(1),
                        Value(Parser_tok.Ident, "x"),
                        Constant(3),
                        Constant(4),
                    ],
                    operators=[
                        Parser_tok.Lt,
                        Parser_tok.Lt,
                        Parser_tok.Le,
                    ],
                ),
                id="compare_mixed_complex"
            ),
            pytest.param(
                "((1 + 2) * (3 + 4)) == (21)",
                Constant(True),
                id="compare_full_arith_eq"
            ),
            pytest.param(
                "True or x",
                Constant(True),
                id="binary_short_circuit"
            )
        ]
    )
    def test_complex_ConstantFolder(self, expr: str, expect: nodes):
        tokens = Lexer(expr).tokenize()
        ast = Parser(tokens).parse()
        assert not isinstance(ast, Parser.Failure)
        assert ConstantFolder().fold(ast) == expect