from __future__ import annotations

from dataclasses import replace
from typing import cast, assert_never

from evaluator.types import (
    nodes,
    Parser_tok, BinaryOp, UnaryOp, Value, Collection, CompareNode, Constant
)
from evaluator.interpreter.stages.base import ExecutionBase

class ConstantFolder(ExecutionBase):
    """Component, that folds nodes, which results are constant"""

    def fold(self, node: nodes) -> nodes | ExecutionBase.Failure:
        if isinstance(node, Value):
            return self.fold_value(node)
        elif isinstance(node, UnaryOp):
            return self.fold_unaryop(node)
        elif isinstance(node, BinaryOp):
            return self.fold_binaryop(node)
        elif isinstance(node, Collection):
            return self.fold_collection(node)
        elif isinstance(node, CompareNode):
            return self.fold_comparenode(node)
        elif isinstance(node, Constant): # type:ignore[redundant-isinstance]
            raise RuntimeError("Constant node was found during constant folding")
        else:
            assert_never(node)

    def fold_value(self, node: Value) -> nodes | ExecutionBase.Failure:
        return node if node.token == Parser_tok.Ident else Constant(node.value, node)

    def fold_unaryop(self, node: UnaryOp) -> nodes | ExecutionBase.Failure:
        source = node
        fold_child = self.fold(node.child)
        if isinstance(fold_child, self.Failure):
            return fold_child
        elif isinstance(fold_child, Constant):
            const = self._try_exec_unaryop(node, fold_child.value)
            return (
                const if isinstance(const, self.Failure)
                else Constant(const, source)
            )
        else:
            return replace(node, child=fold_child)

    def fold_binaryop(self, node: BinaryOp) -> nodes | ExecutionBase.Failure:
        source = node

        left_fold = self.fold(node.left_child)
        if isinstance(left_fold, self.Failure):
            return left_fold

        if (isinstance(left_fold, Constant) and
            self.short_circuit_skip(left_fold.value, node.token)):
            return Constant(left_fold.value, source)

        right_fold = self.fold(node.right_child)
        if isinstance(right_fold, self.Failure):
            return right_fold

        if (isinstance(left_fold, Constant) and
            isinstance(right_fold, Constant)):

            const = self._try_exec_binaryop(node, left_fold.value, right_fold.value)
            return (
                const if isinstance(const, self.Failure)
                else Constant(const, source)
            )
        else:
            return replace(node, left_child=left_fold, right_child=right_fold)

    def fold_collection(self, node: Collection) -> nodes | ExecutionBase.Failure:
        source = node
        foldable = True

        new_collection: list[nodes] = []
        for elem in node.collection:
            new_elem = self.fold(elem)
            if isinstance(new_elem, self.Failure):
                return new_elem
            if not isinstance(new_elem, Constant):
                foldable = False
            new_collection.append(new_elem)

        if foldable:
            vals_iter = (cast(Constant, elem).value for elem in new_collection)
            if node.token == Parser_tok.List:
                return Constant(list(vals_iter), source)
            elif node.token == Parser_tok.Tuple:
                return Constant(tuple(vals_iter), source)
            else:
                raise RuntimeError(
                    f"Container node {node} wasn't recognized and could not be evaluated"
                )
        else:
            return replace(node, collection=new_collection)

    def fold_comparenode(self, node: CompareNode) -> nodes | ExecutionBase.Failure:
        source = node
        foldable = True

        new_operands: list[nodes] = []
        for elem in node.operands:
            new_operand = self.fold(elem)
            if isinstance(new_operand, self.Failure):
                return new_operand
            if not isinstance(new_operand, Constant):
                foldable = False
            new_operands.append(new_operand)

        if foldable:
            all_exprs = zip(node.operators, new_operands, new_operands[1:])
            for op, left, right in all_exprs:
                left = cast(Constant, left)
                right = cast(Constant, right)
                truth = self._try_exec_comparenode(
                    op, (left.value, left.source), (right.value, right.source)
                )
                if isinstance(truth, self.Failure):
                    return truth
                if not truth:
                    return Constant(False, source)
            return Constant(True, source)
        else:
            return replace(node, operands=new_operands)
