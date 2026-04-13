from __future__ import annotations
import re
import operator
import json

from collections.abc import Callable
from dataclasses import dataclass
from pprint import pprint
from typing import Literal
from types import NoneType
from itertools import product
from evaluator.constants import (
    CompareOP_lookup, op_table, op_type_table,
    atom_types, CompareOP, Lexer_type, nodes,
    Lexer_tok, BinaryOp, UnaryOp, Value, Collection, CompareNode, Constant
)

@dataclass(slots=True, frozen=True)
class Lexer:
    """
    Class, that takes subclass of python code in string object
    and transforms it into list of lexer tokens with lexem type,
    lexem and position
    """

    string: str

    operators = {
        'or', 'and', 'in', '==', '!=', '<', '>', '<=',
        '>=', 'not', '+', '-', '*', '/', '//', '%', '**', 'is'
    }

    IDENT_RE = re.compile(r'[a-zA-Z_][0-9a-zA-Z_]*')
    INT_RE = re.compile(r'[0-9]*')
    FLOAT_RE = re.compile(r'[0-9]*\.[0-9]+')
    STRING_RE = re.compile(r'(\'[^\']*\')|("[^"]*")')

    def raise_syntax_error(self, pos: int):
        raise SyntaxError(f"operator does not exist. POS: {pos}")

    def tokenize(self) -> list[Lexer_tok]:
        tok_stack: list[Lexer_tok] = []
        tok: Lexer_tok | None = None
        i = 0
        while i < len(self.string):
            match self.string[i]:
                case ' ' | '\t' | '\r' | '\n':
                    pass
                case '=':
                    if i + 1 < len(self.string) and self.string[i + 1] == '=':
                        tok = Lexer_tok(Lexer_type.OP, '==', i)
                        i += 1
                    else:
                        self.raise_syntax_error(i)
                case '!':
                    if i + 1 < len(self.string) and self.string[i + 1] == '=':
                        tok = Lexer_tok(Lexer_type.OP, '!=', i)
                        i += 1
                    else:
                        self.raise_syntax_error(i)
                case '<':
                    if i + 1 < len(self.string) and self.string[i + 1] == '=':
                        tok = Lexer_tok(Lexer_type.OP, '<=', i)
                        i += 1
                    else:
                        tok = Lexer_tok(Lexer_type.OP, '<', i)
                case '>':
                    if i + 1 < len(self.string) and self.string[i + 1] == '=':
                        tok = Lexer_tok(Lexer_type.OP, '>=', i)
                        i += 1
                    else:
                        tok = Lexer_tok(Lexer_type.OP, '>', i)
                case '+':
                    tok = Lexer_tok(Lexer_type.OP, '+', i)
                case '-':
                    tok = Lexer_tok(Lexer_type.OP, '-', i)
                case '*':
                    if i + 1 < len(self.string) and self.string[i + 1] == '*':
                        tok = Lexer_tok(Lexer_type.OP, '**', i)
                        i += 1
                    else:
                        tok = Lexer_tok(Lexer_type.OP, '*', i)
                case '/':
                    if i + 1 < len(self.string) and self.string[i + 1] == '/':
                        tok = Lexer_tok(Lexer_type.OP, '//', i)
                        i += 1
                    else:
                        tok = Lexer_tok(Lexer_type.OP, '/', i)
                case '%':
                    tok = Lexer_tok(Lexer_type.OP, '%', i)
                case "'" | '"':
                    str_lexem = re.match(self.STRING_RE, self.string[i:])
                    if str_lexem:
                        strr = str_lexem.group()
                        tok = Lexer_tok(Lexer_type.STR, strr, i)
                        i += len(strr) - 1
                    else:
                        self.raise_syntax_error(i)
                case x if x.isdigit() or x == '.':
                    num_lexem, new_i, typ = self.find_num(i)
                    if num_lexem:
                        self.check_leading_zero(num_lexem, i)
                        tok = Lexer_tok(
                            Lexer_type.INT if typ is int else Lexer_type.FLOAT,
                            num_lexem, i
                        )
                    else:
                        self.raise_syntax_error(i)
                    i = new_i
                case '(':
                    tok = Lexer_tok(Lexer_type.OPEN_TUPLE, '(', i)
                case ')':
                    tok = Lexer_tok(Lexer_type.CLOSE_TUPLE, ')', i)
                case '[':
                    tok = Lexer_tok(Lexer_type.OPEN_LIST, '[', i)
                case ']':
                    tok = Lexer_tok(Lexer_type.CLOSE_LIST, ']', i)
                case ',':
                    tok = Lexer_tok(Lexer_type.COMMA, ',', i)
                case _:
                    match, new_i = self.find_longest_match(i)
                    if match in ('True', 'False'):
                        tok = Lexer_tok(Lexer_type.BOOL, match, i)
                    elif match == 'None':
                        tok = Lexer_tok(Lexer_type.NONE, match, i)
                    elif match:
                        if match in self.operators:
                            tok = Lexer_tok(Lexer_type.OP, match, i)
                        else:
                            tok = Lexer_tok(Lexer_type.IDENT, match, i)
                    else:
                        self.raise_syntax_error(i)
                    i = new_i

            if tok:
                tok_stack.append(tok)
                tok = None
            i += 1

        tok_stack.append(Lexer_tok(Lexer_type.EOF, '$', i))
        return tok_stack

    def find_longest_match(self, pnt: int) -> tuple[str | None, int]:
        keyword = re.match(self.IDENT_RE, self.string[pnt:])
        if keyword:
            new_keyword = keyword.group()
            return new_keyword, pnt + len(new_keyword) - 1
        else:
            return None, 0

    def find_num(self, pnt: int) -> tuple[str | None, int, type]:
        typ: type[object] = object
        str_num = re.match(self.FLOAT_RE, self.string[pnt:])
        typ = float
        if str_num is None:
            str_num = re.match(self.INT_RE, self.string[pnt:])
            typ = int
        if str_num:
            num = str_num.group()
            return num, pnt + len(num) - 1, typ
        else:
            return None, 0, object
    
    def check_leading_zero(self, num: str, pos: int) -> None:
        if len(num) > 1 and num[0] == '0' and num[1] != '.':
            raise SyntaxError(f"Numbers can't start with unnecessary zeroes. POS: {pos}")


class Parser:
    """
    Recursive decent parser combined with packrat logic,
    that takes list of tokens and build AST tree
    """

    __slots__ = [
        'tokens', 'pos', 'cache', 'failure', 'rule_stack_count', 'rules_count'
    ]

    MAX_RULES_STACK = 1000
    MAX_RULES = 10000000

    def __init__(self, tokens: list[Lexer_tok]):
        self.tokens = tokens
        self.pos = 0
        self.cache: dict = {}
        self.failure: Parser.Failure | None = None
        self.rule_stack_count = 0
        self.rules_count = 0

    @dataclass(slots=True, frozen=False)
    class Failure:
        pos: int
        wrong_tok: Lexer_tok
        expect: list[str]

    def save_furthest_fail(self, fail: Failure) -> None:
        if self.failure is None:
            self.failure = fail
        else:
            old_pos = self.failure.pos
            new_pos = fail.pos
            if new_pos > old_pos:
                self.failure = fail

    def create_fail(self,
                    pos: int,
                    wrong_tok: Lexer_tok,
                    expect: list[str]) -> None:
        """
        method, that returns Failure object and save it
        to the instance variable, if it is the furthest failure
        """

        fail = self.Failure(pos, wrong_tok, expect)
        self.save_furthest_fail(fail)

    @staticmethod
    def track(funct: Callable) -> Callable:
        """
        decorator, that counts ammount of called rules
        and ammount of called rules ont the call stack.
        If maximum is reached, raise error.
        """

        def wrapper(self, *args, **kwargs) -> None:
            self.rule_stack_count += 1
            self.rules_count += 1
            if self.rule_stack_count > self.MAX_RULES_STACK:
                raise RuntimeError('Max rule call stack height reached')
            if self.rules_count > self.MAX_RULES:
                raise RuntimeError('Max rules count reached')
            try:
                return funct(self, *args, **kwargs)
            finally:
                self.rule_stack_count -= 1
        return wrapper

    @staticmethod
    def memo(funct: Callable) -> Callable:
        """
        decorator, that memoize answer and new position of the rules,
        based on their name and position.
        """

        def wrapper(self, *args, **kwargs) -> None:
            key = (funct.__name__, self.pos)
            if key in self.cache:
                result, new_pos = self.cache[key]
                self.pos = new_pos
                return result
            else:
                result = funct(self, *args, **kwargs)
                self.cache[key] = (result, self.pos)
                return result
        return wrapper

    def peek(self) -> Lexer_tok:
        """returns token, which pointer points to"""

        return self.tokens[self.pos]

    def match(self, token: Lexer_type, lexem: str | None=None) -> bool:
        """
        method, that tries to match Lexer_type and lexem, if is provided.
        If it success, moves pointer and return True. If not, do nothing
        and returns False
        """

        tok = self.peek()
        state = False
        if tok.typ == token:
            if lexem is not None:
                state = True if tok.lexem == lexem else False
            else:
                state = True

        if state:
            self.pos += 1
        return state

    def expect(self, token: Lexer_type, lexem: str) -> bool:
        """
        method, that tries to match the token. If it success, moves pointer
        and return None. If not, pointer stay and return Failure object with
        provided lexem

        PREPISAT POPIS !!!!!
        """

        if self.match(token, lexem):
            return True
        else:
            self.create_fail(self.pos, self.peek(), [lexem])
            return False

    def parse(self) -> nodes | Failure:
        node = self.expr()
        if node is None:
            if self.failure is None:
                raise RuntimeError("failure in parser wasn't stored to variable")
            else:
                return self.failure
        if self.expect(Lexer_type.EOF, '$'):
            return node
        else:
            return self.Failure(self.pos, self.peek(), expect=['$'])

    @track
    @memo
    def expr(self) -> nodes | None:
        return self.disjunction()

    def iterator_op(self,
                    accpet_op: list[str],
                    next_rule: Callable[[], nodes | None]) -> nodes | None:
        left_node = next_rule()

        if left_node is None:
            return left_node

        while True:
            tok = self.peek()
            if any(self.match(Lexer_type.OP, op) for op in accpet_op):
                right_node = next_rule()
                if right_node is None:
                    return right_node
                left_node = BinaryOp(tok, left_node, right_node)
            else:
                break

        return left_node

    @track
    @memo
    def disjunction(self) -> nodes | None:
        return self.iterator_op(['or'], self.conjunction)

    @track
    @memo
    def conjunction(self) -> nodes | None:
        return self.iterator_op(['and'], self.in_operator)

    @track
    @memo
    def in_operator(self) -> nodes | None:
        next_rule = self.compare_operator
        left_node = next_rule()
        if left_node is None:
            return left_node

        lookahead_1 = self.peek()

        if self.match(Lexer_type.OP, 'not'):
            lookahead_2 = self.peek()
            if self.match(Lexer_type.OP, 'in'):
                right_node = self.expr()
                if right_node is None:
                    return right_node
                return UnaryOp(
                    lookahead_1, BinaryOp(lookahead_2, right_node, left_node)
                )
            else:
                self.pos -= 1

        elif self.match(Lexer_type.OP, 'in'):
            right_node = self.expr()
            if right_node is None:
                return right_node
            return BinaryOp(lookahead_1, right_node, left_node)

        return left_node

    @track
    @memo
    def compare_operator(self) -> nodes | None:
        next_rule = self.negation
        left_node = next_rule()
        lexer_operators = ('<=', '>=', '<', '>', '==', '!=')
        if left_node is None:
            return left_node

        operators, operands = [], [left_node]

        while True:
            lookup_1 = self.peek()
            if any(self.match(Lexer_type.OP, tok) for tok in lexer_operators):
                right_node = next_rule()
                if right_node is None:
                    return right_node
                operators.append(CompareOP_lookup[lookup_1.lexem])
                operands.append(right_node)
                continue

            if self.match(Lexer_type.OP, 'is'):
                if self.match(Lexer_type.OP, 'not'):
                    right_node = next_rule()
                    if right_node is None:
                        return right_node
                    operators.append(CompareOP.IS_NOT)
                    operands.append(right_node)
                else:
                    right_node = next_rule()
                    if right_node is None:
                        return right_node
                    operators.append(CompareOP.IS)
                    operands.append(right_node)
                continue

            if len(operators) != 0:
                left_node = CompareNode(operators, operands)
            break

        return left_node

    @track
    @memo
    def negation(self) -> nodes | None:
        next_rule = self.low_ord_operator

        tok = self.peek()
        if self.match(Lexer_type.OP, 'not'):
            node = self.negation()
            if node is None:
                return node
            else:
                return UnaryOp(tok, node)

        return next_rule()

    @track
    @memo
    def low_ord_operator(self) -> nodes | None:
        return self.iterator_op(['+', '-'], self.high_ord_operator)

    @track
    @memo
    def high_ord_operator(self) -> nodes | None:
        return self.iterator_op(['//', '/', '%', '*'], self.factor)

    @track
    @memo
    def factor(self) -> nodes | None:
        next_rule = self.power

        tok = self.peek()
        if any(self.match(Lexer_type.OP, op) for op in ['+', '-']):
            node = self.factor()
            if node is None:
                return node
            else:
                return UnaryOp(tok, node)

        return next_rule()

    @track
    @memo
    def power(self) -> nodes | None:
        next_rule = self.atom
        left_node = next_rule()

        tok = self.peek()
        if self.match(Lexer_type.OP, '**'):
            right_node = self.factor()
            if left_node is None or right_node is None:
                return right_node
            else:
                return BinaryOp(tok, left_node, right_node)

        return left_node

    @track
    @memo
    def atom(self) -> nodes | None:
        tok = self.peek()
        if self.match(Lexer_type.INT):
            return Value(tok)
        elif self.match(Lexer_type.FLOAT):
            return Value(tok)
        elif self.match(Lexer_type.BOOL):
            return Value(tok)
        elif self.match(Lexer_type.IDENT):
            return Value(tok)
        elif self.match(Lexer_type.STR):
            return Value(tok)
        elif self.match(Lexer_type.NONE):
            return Value(tok)
        elif self.match(Lexer_type.IDENT):
            return Value(tok)

        save = self.pos
        if self.match(Lexer_type.OPEN_LIST):
            cont_node = self.list_rule()
            if cont_node is not None:
                return cont_node
        elif self.match(Lexer_type.OPEN_TUPLE):
            cont_node = self.tuple_rule()
            if cont_node is not None:
                return cont_node
        self.pos = save

        if self.match(Lexer_type.OPEN_TUPLE):
            bracket_node = self.expr()
            if self.expect(Lexer_type.CLOSE_TUPLE, ')'):
                return bracket_node
            else:
                return None

        expect = ['int', 'float', 'bool', 'ident', 'str', 'container', 'expr']
        self.create_fail(self.pos, self.peek(), expect)
        return None
        

    @track
    @memo
    def list_rule(self) -> Collection | None:
        collection: list[nodes] = []

        if self.match(Lexer_type.CLOSE_LIST):
            return Collection(list, collection)

        node = self.expr()
        if node is None:
            return node
        collection.append(node)

        while self.match(Lexer_type.COMMA):
            if self.match(Lexer_type.CLOSE_LIST):
                return Collection(list, collection)
            node = self.expr()
            if node is None:
                return node
            collection.append(node)

        if not self.expect(Lexer_type.CLOSE_LIST, ']'):
            return None
        return Collection(list, collection)

    @track
    @memo
    def tuple_rule(self) -> Collection | None:
        collection: list[nodes] = []

        if self.match(Lexer_type.CLOSE_TUPLE):
            return Collection(tuple, collection)

        node = self.expr()
        if node is None:
            return node
        collection.append(node)

        if not self.expect(Lexer_type.COMMA, ','):
            return None

        if self.match(Lexer_type.CLOSE_TUPLE):
            return Collection(tuple, collection)

        node = self.expr()
        if node is None:
            return node
        collection.append(node)

        while self.match(Lexer_type.COMMA):
            if self.match(Lexer_type.CLOSE_TUPLE):
                return Collection(tuple, collection)
            node = self.expr()
            if node is None:
                return node
            collection.append(node)

        if not self.expect(Lexer_type.CLOSE_TUPLE, ')'):
            return None
        return Collection(tuple, collection)


@dataclass(slots=True, frozen=True)
class TypeChecker:
    """
    Type checker, that staticly check expression

    bool values are replaced with integers
    """

    vars: dict[str, atom_types]

    @dataclass(slots= True, frozen=True)
    class TypeFail:
        failed_node: nodes
        types: tuple[object] | tuple[object, object]

    def check(self, node: nodes):
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
        elif isinstance(node, Constant):
            raise RuntimeError("""Constant node should not appear in TypeChecker""")

        raise RuntimeError(
            f"Container node {node} wasn't recognized and could not be folded"
        )
    
    def check_value(self, node: Value) -> set[object]:
        typ = node.token.typ
        if typ == Lexer_type.STR:
            return {str}
        elif typ == Lexer_type.INT or typ == Lexer_type.BOOL:
            return {int}
        elif typ == Lexer_type.FLOAT:
            return {float}
        elif typ == Lexer_type.NONE:
            return {NoneType}
        elif typ == Lexer_type.IDENT:
            val = type(self.vars[node.token.lexem])
            return {val} if val is not bool else {int}
        else:
            raise RuntimeError(
                f"Value node {node} wasn't recognized and could not be evaluated"
            )
    
    def check_unaryop(self, node: UnaryOp) -> set[object] | TypeFail:
        union_type = self.check(node.child)
        if isinstance(union_type, self.TypeFail):
            return union_type

        op_lexem = node.token.lexem
        new_union_type = set()
        for typ in union_type:
            new_typ = op_type_table['unary'][op_lexem].get((typ,))
            if new_typ is None:
                return self.TypeFail(node, (typ,))
            else:
                new_union_type |= new_typ

        return new_union_type

    def check_binaryop(self, node: BinaryOp) -> set[object] | TypeFail:
        left_union_type = self.check(node.left_child)
        right_union_type = self.check(node.right_child)
        if isinstance(left_union_type, self.TypeFail):
            return left_union_type
        if isinstance(right_union_type, self.TypeFail):
            return right_union_type
        
        op_lexem = node.token.lexem
        new_union_type = set()

        for left_typ, right_typ in product(left_union_type, right_union_type):
            new_typ = op_type_table['binary'][op_lexem].get((left_typ, right_typ))
            if new_typ is None:
                return self.TypeFail(node, (left_typ, right_typ))
            else:
                new_union_type |= new_typ

        return new_union_type

    def check_collection(self, node: Collection) -> set[object] | TypeFail:
        for elem in node.collection:
            ret = self.check(elem)
            if isinstance(ret, self.TypeFail):
                return ret
        return {node.typ}

    def check_comparenode(self, node: CompareNode) -> set[object] | TypeFail:

        all_ops = zip(node.operators, node.operands, node.operands[1:])
        left_union_type = self.check(node.operands[0])

        for op, _, val_2 in all_ops:
            right_union_type = self.check(val_2)
            if isinstance(left_union_type, self.TypeFail):
                return left_union_type
            if isinstance(right_union_type, self.TypeFail):
                return right_union_type
            
            for left_typ, right_typ in product(left_union_type, right_union_type):
                new_typ = op_type_table['compare'][op].get((left_typ, right_typ))
                if new_typ is None:
                    return self.TypeFail(node, (left_typ, right_typ))
            
            left_union_type = right_union_type
        
        return {int}


@dataclass(slots=True, frozen=True)
class Evaluator:
    """Evaluator, that execute AST tree with dictionary prefilled with variables"""

    vars: dict[str, atom_types]

    def eval(self, node: nodes) -> atom_types:
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
        elif isinstance(node, Constant):
            return node.value
        else:
            raise RuntimeError(
                f"Node type {node} wasn't recognized and could not be evaluated"
            )

    def handle_value(self, node: Value) -> atom_types:
        typ = node.token.typ
        lexem = node.token.lexem

        if typ == Lexer_type.STR:
            return lexem
        elif typ == Lexer_type.INT:
            return int(lexem)
        elif typ == Lexer_type.FLOAT:
            return float(lexem)
        elif typ == Lexer_type.NONE:
            return None
        elif typ == Lexer_type.BOOL:
            if lexem == 'True':
                return True
            elif lexem == 'False':
                return False
            else:
                raise SyntaxError('Syntax error during evaluation')
        elif typ == Lexer_type.IDENT:
            try:
                return self.vars[lexem]
            except:
                raise RuntimeError(f"Variable {lexem} does not exist")
        else:
            raise RuntimeError(
                f"Value node {node} wasn't recognized and could not be evaluated"
            )

    def handle_collection(self, node: Collection) -> list[atom_types] | tuple[atom_types, ...]:
        vals_iter = (self.eval(elem) for elem in node.collection)
        if node.typ == list:
            return list(vals_iter)
        elif node.typ == tuple:
            return tuple(vals_iter)

        raise RuntimeError(
            f"Container node {node} wasn't recognized and could not be evaluated"
        )

    def handle_unaryop(self, node: UnaryOp) -> atom_types:
        lexem = node.token.lexem
        return op_table['unary'][lexem](self.eval(node.child))

    def handle_binaryop(self, node: BinaryOp) -> atom_types:
        lexem = node.token.lexem
        left = self.eval(node.left_child)
        if self.short_circuit_skip(left, lexem):
            return left
        right = self.eval(node.right_child)
        return op_table['binary'][lexem](left, right)

    def handle_comparenode(self, node: CompareNode) -> atom_types:
        return all(
            op_table['compare'][op](self.eval(val_1), self.eval(val_2))
            for op, val_1, val_2
            in zip(node.operators, node.operands, node.operands[1:])
        )

    def short_circuit_skip(self, left: atom_types, op_lexem: str) -> bool:
        """Check if short-circuit operation can be skipped"""

        if op_lexem == 'and' and not left:
            return True
        elif op_lexem == 'or' and left:
            return True
        return False


class ConstantFolder(Evaluator):
    """Class, that folds nodes, which results are constant"""

    def __init__(self):
        pass

    def fold(self, node: nodes) -> nodes:
        if isinstance(node, Value):
            if node.token.typ != Lexer_type.IDENT:
                return Constant(self.handle_value(node))
            else:
                return node
        elif isinstance(node, UnaryOp):
            return self.fold_unaryop(node)
        elif isinstance(node, BinaryOp):
            return self.fold_binaryop(node)
        elif isinstance(node, Collection):
            return self.fold_collection(node)
        elif isinstance(node, CompareNode):
            return self.fold_comparenode(node)
        elif isinstance(node, Constant):
            raise RuntimeError("Constant node was found during constant folding")

        raise RuntimeError(
            f"Container node {node} wasn't recognized and could not be folded"
        )

    def fold_unaryop(self, node: UnaryOp) -> nodes:
        node.child = self.fold(node.child)
        if isinstance(node.child, Constant):
            lexem = node.token.lexem
            const = op_table['unary'][lexem](node.child.value)
            return Constant(const)
        else:
            return node

    def fold_binaryop(self, node: BinaryOp) -> nodes:
        node.left_child = self.fold(node.left_child)
        node.right_child = self.fold(node.right_child)
        if (isinstance(node.left_child, Constant) and
            isinstance(node.right_child, Constant)):
            lexem = node.token.lexem
            const = op_table['binary'][lexem](
                node.left_child.value, node.right_child.value
            )
            return Constant(const)
        else:
            return node

    def fold_collection(self, node: Collection) -> nodes:
        foldable = True
        for i, elem in enumerate(node.collection):
            node.collection[i] = self.fold(elem)
            if not isinstance(node.collection[i], Constant):
                foldable = False

        if foldable:
            vals_iter = (self.eval(elem) for elem in node.collection)
            if node.typ == list:
                return Constant(list(vals_iter))
            elif node.typ == tuple:
                return Constant(tuple(vals_iter))
            else:
                raise RuntimeError(
                    f"Container node {node} wasn't recognized and could not be evaluated"
                )
        else:
            return node

    def fold_comparenode(self, node: CompareNode) -> nodes:
        foldable = True
        for i, elem in enumerate(node.operands):
            node.operands[i] = self.fold(elem)
            if not isinstance(node.operands[i], Constant):
                foldable = False

        if foldable:
            return Constant(all(
                op_table['compare'][op](self.eval(val_1), self.eval(val_2))
                for op, val_1, val_2
                in zip(node.operators, node.operands, node.operands[1:])
            ))
        else:
            return node

def json_str_to_dict(json_str: str) -> dict:
    """
    converts json string to python dictionary.
    If json key starts with __tuple__, list value will be converted to tuple
    """

    vars: dict = json.loads(json_str)
    for key, val in vars.copy().items():
        if key.startswith('__tuple__'):
            vars[key[9:]] = tuple(val)
    return vars

def compile(expr: str, vars: dict[str, atom_types]) -> nodes:
    """
    Basic compiler, that compiles string into Abstract Syntax Tree,
    that could be interpreted with Evaluator. For more secure variables,
    use compile_safe
    """

    tokens = Lexer(expr).tokenize()
    ast = Parser(tokens).parse()

    if isinstance(ast, Parser.Failure):
        raise RuntimeError(ast)

    typ = TypeChecker(vars).check(ast)

    if isinstance(typ, TypeChecker.TypeFail):
        raise RuntimeError(typ)

    return ConstantFolder().fold(ast)

def compile_save(expr: str, json_vars: str) -> nodes:
    """
    More secure compiler, that use json in string format,
    to evaluate variables. Recomended, if variables are taken from user.
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

    vars = json_str_to_dict(json_vars)
    return compile(expr, vars)

def evaluate(expr: str, vars: dict[str, atom_types]) -> atom_types:
    """
    Basic interpreter, that have all features and evaluate variables
    from python dictionary. For more secure variables, use evaluate_safe
    """

    folded_ast = compile(expr, vars)
    return Evaluator(vars).eval(folded_ast)

def evaluate_safe(expr: str, json_vars: str) -> atom_types:
    """
    More secure interpreter, that use json in string format,
    to evaluate variables. Recomended, if variables are taken from user.
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

    return evaluate(expr, json_str_to_dict(json_vars))

if __name__ == '__main__':
    expr = "5 == 5 None or awdawdaw==, 'awdaw' [dawda not 69.8 <[]('awdawd') True False"
    expr_2 = "(2 + 3) * (4 + 5)"
    test_expr = '< <= > >= == not'
    #pprint(lexer(expr))

    furthest = '1 in [2, 3 and 4 not in [5, 6] or 7 not in ]'

    test_2 = '[0] * 5'
    test_3 = '((((((((((((((((((5))))))))))))))))))'

    #ans = evaluate(expr_2_5, {"tvoja_mama": 12, "my_tuple": [1,2,3], "bool": True, "my_none": None})
    #print(ans)
    tokens = Lexer("2 in [1,2,3] == 1").tokenize()
    ast = Parser(tokens).parse()
    pprint(ast)
    assert not isinstance(ast, Parser.Failure)
    typ = TypeChecker({"a": 2, "b": 3, "c": 4, "d": 10, "e": 2, "f": [1,2,3], "g": None, "h": None}).check(ast)
    #pprint(typ)
    ans = Evaluator({}).eval(ast)
    print('MOJ EVAL',ans)
    print('STANDART EVAL', eval("2 in [1,2,3] == 1"))
    """print(
        eval(
            "((a + b) * c > d) and (e in f or g is h)",
            {"a": 2, "b": 3, "c": 4, "d": 10, "e": 2, "f": [1,2,3], "g": None, "h": None}
        )
    )"""
