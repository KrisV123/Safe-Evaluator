"""

Module for diagnosing Failure objects.

Runtime Error can occure in multiple components.
If new component can raise Runtime Error, always add in brackets
next to it, from which component it comes from.

for example:
RUNTIME EVALUATOR (with TypeChecker)
"""

from __future__ import annotations
from textwrap import dedent
from typing import assert_never
from abc import ABC, abstractmethod
from enum import Enum

from evaluator.interpreter.stages.lexer import Lexer
from evaluator.interpreter.stages.parser import Parser
from evaluator.interpreter.stages.typechecker import TypeChecker
from evaluator.interpreter.stages.constantfolder import ConstantFolder
from evaluator.interpreter.stages.evaluator import Evaluator
from evaluator.interpreter.stages.base import ExecutionBase

from evaluator.types import (
    BinaryOp, UnaryOp, Value, Collection, CompareNode, Constant, nodes
)

ACCEPTED_ERRORS = (
    Lexer.Failure | Parser.Failure | TypeChecker.Failure | ExecutionBase.Failure
)

def diagnose(expr: str, error: ACCEPTED_ERRORS) -> str:
    """
    Orchestrator function, that takes expression, Failure object
    and correctly choose correct tool to diagnose Failure object.
    Returns string with error message.
    """

    tool = DIAGNOSTICS_REGISTER[type(error)]
    return tool(expr, error).build_fail_msg()

class DiagnosticsBase(ABC):
    __slots__ = ['expr', 'error']

    def __init__(self, expr: str, error: ACCEPTED_ERRORS):
        self.expr = expr
        self.error = error

    @abstractmethod
    def build_fail_msg(self) -> str:
        pass

    class Side(Enum):
        """Input object for method find_edge_expr_pos"""

        left = 'l'
        right = 'r'


    def find_edge_expr_pos(self, node: nodes, edge: Side) -> int:
        Side = self.Side
        if isinstance(node, UnaryOp):
            return self.find_edge_expr_pos(node.child, edge)

        elif isinstance(node, BinaryOp):
            if edge == Side.left:
                return self.find_edge_expr_pos(node.left_child, edge)
            elif edge == Side.right:
                return self.find_edge_expr_pos(node.right_child, edge)
            else:
                assert_never(edge)

        elif isinstance(node, CompareNode):
            if edge == Side.left:
                return self.find_edge_expr_pos(node.operands[0], edge)
            elif edge == Side.right:
                last_pos = len(node.operands) - 1
                return self.find_edge_expr_pos(node.operands[last_pos], edge)
            else:
                raise RuntimeError("Edge wasn't recognized")

        elif isinstance(node, Constant):
            return self.find_edge_expr_pos(node.source, edge)

        elif isinstance(node, Collection):
            left, right = node.brackets
            if edge == Side.left:
                return left.position
            elif edge == Side.right:
                return right.position
            else:
                assert_never(edge)

        elif isinstance(node, Value):
            lexer_tok = node.lexer_tok
            if edge == Side.left:
                return lexer_tok.position
            elif edge == Side.right:
                return lexer_tok.position + len(node.lexer_tok.lexem)
            else:
                assert_never(edge)

        else:
            assert_never(node)


class LexerDiagnostics(DiagnosticsBase):
    def build_fail_msg(self) -> str:
        assert isinstance(self.error, Lexer.Failure)

        arrow_line = (
            ' ' * self.error.pos +
            '^' +
            '-' * (self.error.end_pos - self.error.pos - 1)
        )

        error_msg = dedent(f"""
        LEXICAL ERROR
        Here:

        {self.expr}
        {arrow_line}
        don't understand word "{self.expr[self.error.pos: self.error.end_pos]}"
        """)

        hint = self.build_hint(self.error.pos)

        return error_msg + hint

    def build_hint(self, pos: int) -> str:
        fst_char = self.expr[pos]

        if fst_char == '=':
            hint = """
                Hint:
                Mabye you fought '=='
            """
        elif fst_char == '!':
            hint = """
                Hint:
                Mabye you fought '!='
            """
        elif fst_char in ('"', "'"):
            hint = """
                Hint:
                Mabye you forgot to open or close string
            """
        elif fst_char == '0':
            hint = """
                Hint:
                Mabye you try to write number with leading zero
            """
        else:
            hint = ""

        return dedent(hint)


class ParserDiagnostics(DiagnosticsBase):
    def build_fail_msg(self) -> str:
        assert isinstance(self.error, Parser.Failure)

        arrow_pos = (
            ' ' * self.error.wrong_tok.position +
            '^' +
            '-' * (len(self.error.wrong_tok.lexem) - 1)
        )
        wrong_tok_lexem = self.error.wrong_tok.lexem
        wrong_tok_msg = (
            'end of expression'
            if wrong_tok_lexem == '$'
            else wrong_tok_lexem
        )
        expect_tok_lexems = self.error.expect
        expect_tok_msg = (
            'end of expression'
            if expect_tok_lexems == ['$']
            else ', '.join(expect_tok_lexems)
        )

        error_expr = dedent(f"""
            SYNTAX ERROR
            Here:

            {self.expr}
            {arrow_pos}
            is {wrong_tok_msg} but exepect {expect_tok_msg}
        """)

        hint = self.build_hint(wrong_tok_lexem, expect_tok_lexems)

        return error_expr + hint

    def build_hint(self, wrong_tok_lexem: str, expect_tok_lexems: list[str]) -> str:
        if wrong_tok_lexem == '$' and expect_tok_lexems == [')']:
            hint = """
                Hint:
                Maybe your forgot to close tuple or brackets
            """
        elif wrong_tok_lexem == '$' and expect_tok_lexems == [']']:
            hint = """
                Hint:
                Maybe you forgot to close list
            """
        elif wrong_tok_lexem == '$':
            hint = """
                Hint:
                Interpreter is expecting to continue but found anything.
                Maybe you end up with unfinished operation
            """
        elif expect_tok_lexems == ['$']:
            hint = """
                Hint:
                Interpreter didn't expect to continue.
                Maybe you forgot to add operator
            """
        elif expect_tok_lexems == [']']:
            hint = """
                Hint:
                Maybe you forgot to add comma in square brackets before current symbol
            """
        elif expect_tok_lexems == [')']:
            hint = """
                Hint:
                Maybe you forgot to add comma in brackets before current symbol
            """
        else:
            hint = ""

        return dedent(hint)


class TypeCheckerDiagnostics(DiagnosticsBase):
    def build_fail_msg(self) -> str:
        assert isinstance(self.error, TypeChecker.Failure)

        lexer_tok_list = self.error.operator

        left_expr_pos = self.find_edge_expr_pos(
            self.error.operands[0], self.Side.left
        )
        last_operand_node = len(self.error.operands) - 1
        right_expr_pos = self.find_edge_expr_pos(
            self.error.operands[last_operand_node], self.Side.right
        )

        underscore_expr = [' '] * left_expr_pos + ['-'] * (right_expr_pos - left_expr_pos)

        lst_lexer_tok = lexer_tok_list[len(lexer_tok_list) - 1]
        fst_op_pos = lexer_tok_list[0].position
        lst_op_pos = lst_lexer_tok.position + len(lst_lexer_tok.lexem)

        arrow_line_list = underscore_expr
        for i in range(fst_op_pos, lst_op_pos):
            arrow_line_list[i] = '^'

        arrow_line = ''.join(arrow_line_list)
        op_lexems = ' '.join(tok.lexem for tok in lexer_tok_list)

        if isinstance(self.error, TypeChecker.TypeFailure):
            wrong_types_str = '(' + ', '.join(cls.__name__ for cls in self.error.types) + ')'
            error_msg = dedent(f"""
                TYPE ERROR
                Here:

                {self.expr}
                {arrow_line}
                unsupported operand types for {op_lexems} : {wrong_types_str}
            """)
        elif isinstance(self.error, TypeChecker.GenericFailure):
            error_msg = dedent(f"""
                RUNTIME ERROR (with TypeChecker)
                Here:

                {self.expr}
                {arrow_line}
                {type(self.error.exception).__name__}: {self.error.exception}
            """)
        else:
            raise RuntimeError('Any other error does not exist')

        return error_msg


class ExecutionBaseDiagnostics(DiagnosticsBase):
    def build_fail_msg(self) -> str:
        assert isinstance(self.error, ExecutionBase.Failure)

        operands = self.error.operands
        fst_operand = operands[0]
        lst_operand = operands[len(operands) - 1]

        most_left_pos = self.find_edge_expr_pos(fst_operand, self.Side.left)
        most_right_pos = self.find_edge_expr_pos(lst_operand, self.Side.right)

        arrow_line = ' ' * most_left_pos + '^' * (most_right_pos - most_left_pos)

        error_msg = dedent(f"""
            RUNTIME ERROR (with {self.error.component}):
            Here:

            {self.expr}
            {arrow_line}

            {type(self.error.exception).__name__}: {self.error.exception}
        """)

        return error_msg


DIAGNOSTICS_REGISTER: dict[type, type[DiagnosticsBase]] = {
    Lexer.Failure: LexerDiagnostics,
    Parser.Failure: ParserDiagnostics,
    TypeChecker.TypeFailure: TypeCheckerDiagnostics,
    TypeChecker.GenericFailure: TypeCheckerDiagnostics,
    ConstantFolder.Failure: ExecutionBaseDiagnostics,
    Evaluator.Failure: ExecutionBaseDiagnostics
}