from dataclasses import dataclass

from evaluator.types import (
    atom_types, nodes,
    Parser_tok, Lexer_tok, BinaryOp, UnaryOp
)
from evaluator.interpreter.tables import op_table

@dataclass(slots=True, frozen=True)
class BaseFailure:
    """
    Base for Failure objects in interpreter components
    for identification in testing.
    """


class ExecutionBase:
    """
    Abstract base class for every component, that execute parts of AST.
    Contains own Failure and endpoints for calculating with
    optional result <atom_types, Failure>
    """

    @dataclass(slots=True, frozen=True)
    class Failure(BaseFailure):
        component: str
        operator: list[Lexer_tok]
        operands: tuple[nodes,...]
        exception: Exception


    def _create_failiure(self, operator: list[Lexer_tok], operands: tuple[nodes,...], exception: Exception) -> Failure:
        return self.Failure(
            type(self).__name__,
            operator,
            operands,
            exception
        )

    def _try_exec_unaryop(self, node: UnaryOp, val: atom_types) -> atom_types | Failure:
        try:
            return op_table['unary'][node.token](val)
        except Exception as e:
            return self._create_failiure([node.lexer_tok], (node.child,), e)

    def _try_exec_binaryop(self,
                           node: BinaryOp,
                           left_val: atom_types,
                           right_val: atom_types) -> atom_types | Failure:
        try:
            return op_table['binary'][node.token](left_val, right_val)
        except Exception as e:
            return self._create_failiure(
                [node.lexer_tok], (node.left_child, node.right_child), e
            )

    def _try_exec_comparenode(self,
                              operator: tuple[Parser_tok, list[Lexer_tok]],
                              left: tuple[atom_types, nodes],
                              right: tuple[atom_types, nodes]) -> bool | Failure:
        parser_tok, lexer_toks = operator
        left_val, left_node = left
        right_val, right_node = right
        try:
            return op_table['compare'][parser_tok](left_val, right_val)
        except Exception as e:
            return self._create_failiure(lexer_toks, (left_node, right_node), e)

    def short_circuit_skip(self, left: atom_types, token: Parser_tok) -> bool:
        """Check if short-circuit operation can be skipped"""

        if token == Parser_tok.And and not left:
            return True
        elif token == Parser_tok.Or and left:
            return True
        return False

