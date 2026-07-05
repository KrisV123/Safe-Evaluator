import pytest
from textwrap import dedent

from evaluator.interpreter.stages.lexer import Lexer
from evaluator.types import Lexer_type, Lexer_tok

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
def test_all_ops(op: str, expect: list[Lexer_tok]):
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
def test_strings(string: str, expect: list[Lexer_tok]):
    assert Lexer(string).tokenize() == expect

@pytest.mark.parametrize(
    "string, error",
    [
        ("'awd", Lexer.Failure(pos=0, end_pos=4)),
        ("awd'", Lexer.Failure(pos=3, end_pos=4)),
        ('"awd', Lexer.Failure(pos=0, end_pos=4)),
        ('awd"', Lexer.Failure(pos=3, end_pos=4))
    ],
    ids=['prefix_single', 'suffix_single', 'prefix_double', 'suffix_double']
)
def test_wrong_string(string: str, error: Lexer.Failure):
    assert Lexer(string).tokenize() == error

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
def test_brackets(bracket: str, expect: list[Lexer_tok]):
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
def test_numbers(number: str, expect: list[Lexer_tok]):
    assert Lexer(number).tokenize() == expect

@pytest.mark.parametrize(
    'number, error',
    [
        ('01', Lexer.Failure(pos=0, end_pos=2)),
        ('01.2', Lexer.Failure(pos=0, end_pos=4)),
        ('.', Lexer.Failure(pos=0, end_pos=1))
    ],
    ids=['01', '01.2', '.']
)
def test_wrong_num(number: str, error: Lexer.Failure):
    tokens = Lexer(number).tokenize()
    assert tokens == error

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
def test_identificator(ident: str, expect: list[Lexer_tok]):
    assert Lexer(ident).tokenize() == expect

@pytest.mark.parametrize(
    'ident, error',
    [('=var', Lexer.Failure(pos=0, end_pos=1))],
    ids=['equivalency_prefix']
)
def test_wrong_identificators(ident: str, error: Lexer.Failure):
    assert Lexer(ident).tokenize() == error

@pytest.mark.parametrize(
    "string, expect",
    [
        ('None', [Lexer_tok(Lexer_type.NONE, 'None', 0), Lexer_tok(Lexer_type.EOF, '$', 4)]),
        (',', [Lexer_tok(Lexer_type.COMMA, ',', 0), Lexer_tok(Lexer_type.EOF, '$', 1)])
    ],
    ids=['None', ',']
)
def test_extra(string: str, expect: list[Lexer_tok]):
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
def test_combinations(string: str, expect: list[Lexer_tok]):
    assert Lexer(string).tokenize() == expect