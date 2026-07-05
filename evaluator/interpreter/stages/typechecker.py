from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import NoneType
from itertools import product
from typing import assert_never

from evaluator.types import (
    nodes,
    Parser_tok, Lexer_tok,
    BinaryOp, UnaryOp, Value, Collection, CompareNode, Constant
)
from evaluator.interpreter.tables import op_type_table
from evaluator.protocols.serialization import TypeDictCodec
from evaluator.interpreter.stages.base import BaseFailure

class TypeChecker:
    """
    Type checker, that staticly check expression

    bool values are replaced with integers
    """

    __slots__ = ['_frozen', 'vars', '_cache']

    def __init__(self, vars: Mapping[str, type]):
        object.__setattr__(self, '_frozen', False)
        self.vars = vars
        object.__setattr__(self, '_frozen', True)

    def __setattr__(self, name: str, value: object) -> None:
        if not getattr(self, '_frozen'):
            object.__setattr__(self, name, value)
        else:
            raise AttributeError('Object is immutable')
    
    @classmethod
    def from_json(cls, json_vars: str) -> TypeChecker:
        """
        class constructor for json-like string that
        automatically converts to dictionary
        """

        return cls(TypeDictCodec.decode(json_vars))

    @dataclass(slots=True, frozen=True)
    class Failure:
        operator: list[Lexer_tok]
        operands: tuple[nodes,...]


    @dataclass(slots=True, frozen=True)
    class TypeFailure(Failure, BaseFailure):
        types: tuple[type] | tuple[type, type]


    @dataclass(slots=True, frozen=True)
    class GenericFailure(Failure, BaseFailure):
        exception: Exception


    def check(self, node: nodes) -> set[type] | Failure:
        if isinstance(node, Value):
            return self.check_value(node)
        elif isinstance(node, UnaryOp):
            return self.check_unaryop(node)
        elif isinstance(node, BinaryOp):
            return self.check_binaryop(node)
        elif isinstance(node, Collection):
            return self.check_collection(node)
        elif isinstance(node, CompareNode):
            return self.check_comparenode(node)
        elif isinstance(node, Constant): # type: ignore[redundant-isinstance]
            raise RuntimeError("Constant node should not appear in TypeChecker")
        else:
            assert_never(node)

    def check_value(self, node: Value) -> set[type] | Failure:
        token = node.token
        if token == Parser_tok.Str:
            return {str}
        elif token == Parser_tok.Int or token == Parser_tok.Bool:
            return {int}
        elif token == Parser_tok.Float:
            return {float}
        elif token == Parser_tok.None_:
            return {NoneType}
        elif token == Parser_tok.Ident:
            assert isinstance(node.value, str)
            try:
                typ = self.vars[node.value]
            except Exception as e:
                return self.GenericFailure([node.lexer_tok], (node,), e)
            if typ is bool:
                typ = int
            return {typ}
        else:
            raise RuntimeError(
                f"Value node {node} wasn't recognized and could not be evaluated"
            )

    def check_unaryop(self, node: UnaryOp) -> set[type] | Failure:
        union_type = self.check(node.child)
        if isinstance(union_type, self.Failure):
            return union_type

        token = node.token
        new_union_type: set[type] = set()
        for typ in union_type:
            new_typ = op_type_table['unary'][token].get((typ,))
            if new_typ is None:
                return self.TypeFailure([node.lexer_tok], (node.child,), (typ,))
            else:
                new_union_type |= new_typ

        return new_union_type

    def check_binaryop(self, node: BinaryOp) -> set[type] | Failure:
        left_union_type = self.check(node.left_child)
        right_union_type = self.check(node.right_child)
        if isinstance(left_union_type, self.Failure):
            return left_union_type
        if isinstance(right_union_type, self.Failure):
            return right_union_type
     
        token = node.token
        new_union_type: set[type] = set()

        for left_typ, right_typ in product(left_union_type, right_union_type):
            new_typ = op_type_table['binary'][token].get((left_typ, right_typ))
            if new_typ is None:
                return self.TypeFailure(
                    [node.lexer_tok],
                    (node.left_child, node.right_child),
                    (left_typ, right_typ)
                )
            else:
                new_union_type |= new_typ

        return new_union_type

    def check_collection(self, node: Collection) -> set[type] | Failure:
        for elem in node.collection:
            ret = self.check(elem)
            if isinstance(ret, self.Failure):
                return ret
        if node.token == Parser_tok.List:
            return {list}
        elif node.token == Parser_tok.Tuple:
            return {tuple}
        else:
            raise RuntimeError(f"Parser token {node.token} is not implemented in type checker")

    def check_comparenode(self, node: CompareNode) -> set[type] | Failure:
        left_union_type = self.check(node.operands[0])
        all_exprs = zip(node.operators, node.operands, node.operands[1:])

        for (pars_tok, lex_toks), val_1, val_2 in all_exprs:
            right_union_type = self.check(val_2)
            if isinstance(left_union_type, self.Failure):
                return left_union_type
            if isinstance(right_union_type, self.Failure):
                return right_union_type

            for left_typ, right_typ in product(left_union_type, right_union_type):
                new_typ = op_type_table['compare'][pars_tok].get((left_typ, right_typ))
                if new_typ is None:
                    return self.TypeFailure(
                        lex_toks,
                        (val_1, val_2),
                        (left_typ, right_typ)
                    )

            left_union_type = right_union_type

        return {int}
