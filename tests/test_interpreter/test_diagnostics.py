import pytest
from textwrap import dedent

from evaluator.interpreter.stages.lexer import Lexer
from evaluator.interpreter.stages.parser import Parser
from evaluator.interpreter.stages.typechecker import TypeChecker
from evaluator.interpreter.stages.constantfolder import ConstantFolder
from evaluator.interpreter.stages.evaluator import Evaluator

from evaluator.interpreter.diagnostics import diagnose
from evaluator.types import atom_types

@pytest.mark.parametrize(
    "expr, expect_error_msg",
    [
        (
            "1 ! 2",
            dedent(
                """
                LEXICAL ERROR
                Here:

                1 ! 2
                  ^
                don't understand word "!"

                Hint:
                Mabye you fought '!='
                """
            )
        ),
        (
            "1 = 2",
            dedent(
                """
                LEXICAL ERROR
                Here:

                1 = 2
                  ^
                don't understand word "="

                Hint:
                Mabye you fought '=='
                """
            )
        ),
        (
            "'s' + 'awd",
            dedent(
                """
                LEXICAL ERROR
                Here:

                's' + 'awd
                      ^---
                don't understand word "'awd"

                Hint:
                Mabye you forgot to open or close string
                """
            )
        ),
        (
            "'s' + .",
            dedent(
                """
                LEXICAL ERROR
                Here:

                's' + .
                      ^
                don't understand word "."
                """
            )
        ),
        (
            "1 + 025",
            dedent(
                """
                LEXICAL ERROR
                Here:

                1 + 025
                    ^--
                don't understand word "025"

                Hint:
                Mabye you try to write number with leading zero
                """
            )
        )
    ]
)
def test_LexerDiagnostics(expr: str, expect_error_msg: str):
    error = Lexer(expr).tokenize()
    assert isinstance(error, Lexer.Failure)
    error_msg = diagnose(expr, error)

    assert error_msg == expect_error_msg

@pytest.mark.parametrize(
    "expr, expect_error_msg",
    [
        (
            "1 + ",
            dedent(
                """
                SYNTAX ERROR
                Here:

                1 + 
                    ^
                is end of expression but exepect int, float, bool, ident, str, container, expr

                Hint:
                Interpreter is expecting to continue but found anything.
                Maybe you end up with unfinished operation
                """
            )
        ),
        (
            "1 * * 1",
            dedent(
                """
                SYNTAX ERROR
                Here:

                1 * * 1
                    ^
                is * but exepect int, float, bool, ident, str, container, expr
                """
            )
        ),
        (
            "[1, 2, 3",
            dedent(
                """
                SYNTAX ERROR
                Here:

                [1, 2, 3
                        ^
                is end of expression but exepect ]

                Hint:
                Maybe you forgot to close list
                """
            )
        ),
        (
            "1 2",
            dedent(
                """
                SYNTAX ERROR
                Here:

                1 2
                  ^
                is 2 but exepect end of expression

                Hint:
                Interpreter didn't expect to continue.
                Maybe you forgot to add operator
                """
            )
        ),
        (
            "(1, 2 3)",
            dedent(
                """
                SYNTAX ERROR
                Here:

                (1, 2 3)
                      ^
                is 3 but exepect )

                Hint:
                Maybe you forgot to add comma in brackets before current symbol
                """
            )
        ),
        (
            "[1 2]",
            dedent(
                """
                SYNTAX ERROR
                Here:

                [1 2]
                   ^
                is 2 but exepect ]

                Hint:
                Maybe you forgot to add comma in square brackets before current symbol
                """
            )
        )
    ]
)
def test_ParserDiagnostics(expr: str, expect_error_msg: str):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    error = Parser(tokens).parse()
    assert isinstance(error, Parser.Failure)

    error_msg = diagnose(expr, error)
    assert error_msg == expect_error_msg
    
@pytest.mark.parametrize(
    "expr, types, expect_error_msg",
    [
        (
            "+ s",
            {},
            dedent(
                """
                RUNTIME ERROR (with TypeChecker)
                Here:

                + s
                  ^
                KeyError: 's'
                """
            )
        ),
        (
            "1 + (- 's')",
            {},
            dedent(
                """ 
                TYPE ERROR
                Here:

                1 + (- 's')
                     ^ ---
                unsupported operand types for - : (str)
                """
            )
        ),
        (
            "6 - 's' + 7",
            {},
            dedent(
                """
                TYPE ERROR
                Here:

                6 - 's' + 7
                --^----
                unsupported operand types for - : (int, str)
                """
            )
        ),
        (
            "[6, 6 ** 's', 9]",
            {},
            dedent(
                """
                TYPE ERROR
                Here:

                [6, 6 ** 's', 9]
                    --^^----
                unsupported operand types for ** : (int, str)
                """
            )
        ),
        (
            "6 < 6 ** 's' > 9",
            {},
            dedent(
                """
                TYPE ERROR
                Here:

                6 < 6 ** 's' > 9
                    --^^----
                unsupported operand types for ** : (int, str)
                """
            )
        ),
        (
            "8 not in x",
            {'x': float},
            dedent(
                """
                TYPE ERROR
                Here:

                8 not in x
                --^^^^^^--
                unsupported operand types for not in : (int, float)
                """
            )
        )
    ]
)
def test_TypeCheckerDiagnostics(expr: str, types: dict[str, type], expect_error_msg: str):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    error = TypeChecker(types).check(ast)
    assert isinstance(error, TypeChecker.Failure)

    error_msg = diagnose(expr, error)
    assert expect_error_msg == error_msg

@pytest.mark.parametrize(
    "expr, vvars, expect_error_msg",
    [
        (
            "+ s",
            {},
            dedent(
                """
                RUNTIME ERROR (with Evaluator):
                Here:

                + s
                  ^

                KeyError: 's'
                """
            )
        ),
        (
            "1 + (1 // 0)",
            {},
            dedent(
                """
                RUNTIME ERROR (with Evaluator):
                Here:

                1 + (1 // 0)
                     ^^^^^^

                ZeroDivisionError: integer division or modulo by zero
                """
            )
        ),
        (
            "1 + (1 // 's')",
            {},
            dedent(
                """
                RUNTIME ERROR (with Evaluator):
                Here:

                1 + (1 // 's')
                     ^^^^^^^^

                TypeError: unsupported operand type(s) for //: 'int' and 'str'
                """
            )
        )
    ]
)
def test_evaluator(expr: str, vvars: dict[str, atom_types], expect_error_msg: str):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    error = Evaluator(vvars).eval(ast)
    assert isinstance(error, Evaluator.Failure)

    error_msg = diagnose(expr, error)
    assert error_msg == expect_error_msg

@pytest.mark.parametrize(
    "expr, expect_error_msg",
    [
        (
            "1 + (1 // 0)",
            dedent(
                """
                RUNTIME ERROR (with ConstantFolder):
                Here:

                1 + (1 // 0)
                     ^^^^^^

                ZeroDivisionError: integer division or modulo by zero
                """
            )
        ),
        (
            "1 + (1 // 's')",
            dedent(
                """
                RUNTIME ERROR (with ConstantFolder):
                Here:

                1 + (1 // 's')
                     ^^^^^^^^

                TypeError: unsupported operand type(s) for //: 'int' and 'str'
                """
            )
        )
    ]
)
def test_ConstantFolder(expr: str, expect_error_msg: str):
    tokens = Lexer(expr).tokenize()
    assert not isinstance(tokens, Lexer.Failure)
    ast = Parser(tokens).parse()
    assert not isinstance(ast, Parser.Failure)
    error = ConstantFolder().fold(ast)
    assert isinstance(error, ConstantFolder.Failure)

    error_msg = diagnose(expr, error)
    assert error_msg == expect_error_msg
