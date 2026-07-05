import pytest

from evaluator.interpreter.stages.lexer import Lexer
from evaluator.interpreter.stages.parser import Parser
from evaluator.interpreter.stages.constantfolder import ConstantFolder
from evaluator.interpreter.stages.evaluator import Evaluator

from evaluator.types import (
    atom_types, Lexer_type, Parser_tok, Lexer_tok, Value
)

@pytest.mark.parametrize(
    "expr, vvars, expect_fail",
    [
        (
            "5 + x",
            {'x': 's'},
            Evaluator.Failure(
                component='Evaluator',
                operator=[Lexer_tok(Lexer_type.PLUS, '+', 2)],
                operands=(
                    Value(
                        token=Parser_tok.Int,
                        value=5,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '5', 0)
                    ),
                    Value(
                        token=Parser_tok.Ident,
                        value='x',
                        lexer_tok=Lexer_tok(Lexer_type.IDENT, 'x', 4)
                    )
                ),
                exception=TypeError("unsupported operand type(s) for +: 'int' and 'str'")
            )
        ),
        (
            "5 + 's'",
            {},
            Evaluator.Failure(
                component='Evaluator',
                operator=[Lexer_tok(Lexer_type.PLUS, '+', 2)],
                operands=(
                    Value(
                        token=Parser_tok.Int,
                        value=5,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '5', 0)
                    ),
                    Value(
                        token=Parser_tok.Str,
                        value='s',
                        lexer_tok=Lexer_tok(Lexer_type.STR, "'s'", 4)
                    )
                ),
                exception=TypeError("unsupported operand type(s) for +: 'int' and 'str'")
            )
        ),
        (
            "5 + x",
            {},
            Evaluator.Failure(
                component='Evaluator',
                operator=[],
                operands=(
                    Value(
                        token=Parser_tok.Ident,
                        value='x',
                        lexer_tok=Lexer_tok(Lexer_type.IDENT, 'x', 4)
                    ),
                ),
                exception=KeyError('x'))
        )
    ]
)
def test_Evaluator_failure(expr: str, vvars: dict[str, atom_types], expect_fail: Evaluator.Failure):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    fail = Evaluator(vvars).eval(ast)

    assert isinstance(fail, Evaluator.Failure)
    assert fail.component == expect_fail.component
    assert fail.operator == expect_fail.operator
    assert fail.operands == expect_fail.operands
    assert fail.exception.args == expect_fail.exception.args

@pytest.mark.parametrize(
    "expr, expect_fail",
    [
        (
            "5 + 's'",
            ConstantFolder.Failure(
                component='ConstantFolder',
                operator=[Lexer_tok(Lexer_type.PLUS, '+', 2)],
                operands=(
                    Value(
                        token=Parser_tok.Int,
                        value=5,
                        lexer_tok=Lexer_tok(Lexer_type.INT, '5', 0)
                    ),
                    Value(
                        token=Parser_tok.Str,
                        value='s',
                        lexer_tok=Lexer_tok(Lexer_type.STR, "'s'", 4)
                    )
                ),
                exception=TypeError("unsupported operand type(s) for +: 'int' and 'str'")
            )
        )
    ]
)
def test_ConstantFolder_failure(expr: str, expect_fail: ConstantFolder.Failure):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    fail = ConstantFolder().fold(ast)

    assert isinstance(fail, ConstantFolder.Failure)
    assert fail.component == expect_fail.component
    assert fail.operator == expect_fail.operator
    assert fail.operands == expect_fail.operands
    assert fail.exception.args == expect_fail.exception.args
