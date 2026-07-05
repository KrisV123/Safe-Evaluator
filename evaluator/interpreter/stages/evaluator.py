from __future__ import annotations

from collections.abc import Mapping
from typing import assert_never

from evaluator.types import (
    atom_types, nodes,
    Parser_tok, BinaryOp, UnaryOp, Value, Collection, CompareNode, Constant
)
from evaluator.protocols.serialization import VarsDictCodec
from evaluator.interpreter.stages.base import ExecutionBase

class Evaluator(ExecutionBase):
    """
    Evaluator, that execute AST tree with dictionary prefilled with variables.
    Evaluator can accept as variables dictionary and string in JSON format.
    If you want to add tuple, create list, which key starts with __tuple__.\n
    Example:\n
    ```json
    {"__tuple__my_tuple": [1,2,3]}
    ```
    will be interpreted as
    ```python
    {"my_tuple": (1,2,3)}
    ```
    """

    __slots__ = ['_frozen', 'vars']

    def __init__(self, vars: Mapping[str, atom_types]):
        object.__setattr__(self, '_frozen', False)
        self.vars = vars
        object.__setattr__(self, '_frozen', True)

    def __setattr__(self, name: str, value: object) -> None:
        if not getattr(self, '_frozen'):
            object.__setattr__(self, name, value)
        else:
            raise AttributeError('Object is immutable')

    @classmethod
    def from_json(cls, json_vars: str) -> Evaluator:
        """
        class constructor for json-like string that
        automatically converts to dictionary
        """

        return cls(VarsDictCodec.decode(json_vars))

    def eval(self, node: nodes) -> atom_types | ExecutionBase.Failure:
        """Method to execute AST tree"""

        if isinstance(node, Value):
            return self.handle_value(node)
        elif isinstance(node, Collection):
            return self.handle_collection(node)
        elif isinstance(node, UnaryOp):
            return self.handle_unaryop(node)
        elif isinstance(node, BinaryOp):
            return self.handle_binaryop(node)
        elif isinstance(node, CompareNode):
            return self.handle_comparenode(node)
        elif isinstance(node, Constant): # type:ignore[redundant-isinstance]
            return node.value
        else:
            assert_never(node)

    def _try_dict_val(self, node: Value) -> atom_types | ExecutionBase.Failure:
        try:
            assert isinstance(node.value, str)
            return self.vars[node.value]
        except Exception as e:
            component_name = type(self).__name__
            return self.Failure(component_name, [], (node,), e)

    def handle_value(self, node: Value) -> atom_types | ExecutionBase.Failure:
        if node.token == Parser_tok.Ident:
            assert isinstance(node.value, str)
            return self._try_dict_val(node)
        else:
            return node.value

    def handle_unaryop(self, node: UnaryOp) -> atom_types | ExecutionBase.Failure:
        val = self.eval(node.child)
        if isinstance(val, self.Failure):
            return val
        return self._try_exec_unaryop(node, val)

    def handle_binaryop(self, node: BinaryOp) -> atom_types | ExecutionBase.Failure:
        left = self.eval(node.left_child)
        if isinstance(left, self.Failure):
            return left
        if self.short_circuit_skip(left, node.token):
            return left
        right = self.eval(node.right_child)
        if isinstance(right, self.Failure):
            return right

        return self._try_exec_binaryop(node, left, right)

    def handle_collection(self, node: Collection) -> list[atom_types] | tuple[atom_types, ...] | ExecutionBase.Failure:
        collection: list[atom_types] = []
        for elem in node.collection:
            val = self.eval(elem)
            if isinstance(val, self.Failure):
                return val
            collection.append(val)

        if node.token == Parser_tok.List:
            return collection
        elif node.token == Parser_tok.Tuple:
            return tuple(collection)
        raise RuntimeError(
            f"Container node {node} wasn't recognized and could not be evaluated"
        )

    def handle_comparenode(self, node: CompareNode) -> atom_types | ExecutionBase.Failure:
        all_exprs = zip(node.operators, node.operands, node.operands[1:])
        for op, left, right in all_exprs:
            val_1 = self.eval(left)
            if isinstance(val_1, self.Failure):
                return val_1
            val_2 = self.eval(right)
            if isinstance(val_2, self.Failure):
                return val_2

            truth = self._try_exec_comparenode(
                op, (val_1, left), (val_2, right)
            )
            if isinstance(truth, self.Failure):
                return truth
            if not truth:
                return False
        return True

