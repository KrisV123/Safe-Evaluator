from __future__ import annotations
import re

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from types import NoneType
from itertools import product
from typing import cast, assert_never
from pprint import pprint

from evaluator.types import (
    atom_types, nodes,
    Lexer_type, Parser_tok, Lexer_tok,
    BinaryOp, UnaryOp, Value, Collection, CompareNode, Constant
)
from evaluator.interpreter.tables import op_table, op_type_table
from evaluator.protocols.serialization import TypeDictCodec, VarsDictCodec

@dataclass(slots=True, frozen=True)
class BaseFailure:
    """
    Base for Failure objects in interpreter components
    for identification in testing.
    """


class Lexer:
    """
    Component, that takes subclass of python code in string object
    and transforms it into list of lexer tokens with lexem type,
    lexem and position
    """

    __slots__ = ['_frozen', 'string']

    def __init__(self, string: str):
        object.__setattr__(self, '_frozen', False)
        self.string = string
        object.__setattr__(self, '_frozen', True)

    def __setattr__(self, name: str, value: object) -> None:
        if not getattr(self, '_frozen'):
            object.__setattr__(self, name, value)
        else:
            raise AttributeError('Object is immutable')

    keyword_op = {
        'or': Lexer_type.OR,
        'and': Lexer_type.AND,
        'in': Lexer_type.IN,
        'not': Lexer_type.NOT,
        'is': Lexer_type.IS
    }

    IDENT_RE = re.compile(r'[a-zA-Z_][0-9a-zA-Z_]*')
    INT_RE = re.compile(r'[0-9]*')
    FLOAT_RE = re.compile(r'[0-9]*\.[0-9]+')
    STRING_RE = re.compile(r'(\'[^\']*\')|("[^"]*")')

    @dataclass(slots=True, frozen=True)
    class Failure(BaseFailure):
        pos: int
        end_pos: int


    def tokenize(self) -> list[Lexer_tok] | Failure:
        tok_stack: list[Lexer_tok] = []
        tok: Lexer_tok | None = None
        i = 0
        while i < len(self.string):
            match self.string[i]:
                case ' ' | '\t' | '\r' | '\n':
                    pass
                case '=':
                    if i + 1 < len(self.string) and self.string[i + 1] == '=':
                        tok = Lexer_tok(Lexer_type.EQ, '==', i)
                        i += 1
                    else:
                        return self.Failure(i, i + 1)
                case '!':
                    if i + 1 < len(self.string) and self.string[i + 1] == '=':
                        tok = Lexer_tok(Lexer_type.NE, '!=', i)
                        i += 1
                    else:
                        return self.Failure(i, i + 1)
                case '<':
                    if i + 1 < len(self.string) and self.string[i + 1] == '=':
                        tok = Lexer_tok(Lexer_type.LE, '<=', i)
                        i += 1
                    else:
                        tok = Lexer_tok(Lexer_type.LT, '<', i)
                case '>':
                    if i + 1 < len(self.string) and self.string[i + 1] == '=':
                        tok = Lexer_tok(Lexer_type.GE, '>=', i)
                        i += 1
                    else:
                        tok = Lexer_tok(Lexer_type.GT, '>', i)
                case '+':
                    tok = Lexer_tok(Lexer_type.PLUS, '+', i)
                case '-':
                    tok = Lexer_tok(Lexer_type.MINUS, '-', i)
                case '*':
                    if i + 1 < len(self.string) and self.string[i + 1] == '*':
                        tok = Lexer_tok(Lexer_type.DSTAR, '**', i)
                        i += 1
                    else:
                        tok = Lexer_tok(Lexer_type.STAR, '*', i)
                case '/':
                    if i + 1 < len(self.string) and self.string[i + 1] == '/':
                        tok = Lexer_tok(Lexer_type.DSLASH, '//', i)
                        i += 1
                    else:
                        tok = Lexer_tok(Lexer_type.SLASH, '/', i)
                case '%':
                    tok = Lexer_tok(Lexer_type.PERCENT, '%', i)
                case "'" | '"':
                    str_lexem = re.match(self.STRING_RE, self.string[i:])
                    if str_lexem:
                        strr = str_lexem.group()
                        tok = Lexer_tok(Lexer_type.STR, strr, i)
                        i += len(strr) - 1
                    else:
                        return self.Failure(i, len(self.string))
                case x if x.isdigit() or x == '.':
                    num_lexem, new_i, typ = self.find_num(i)
                    if num_lexem:
                        check = self.check_leading_zero(num_lexem, i)
                        if isinstance(check, self.Failure):
                            return check
                        tok = Lexer_tok(
                            Lexer_type.INT if typ is int else Lexer_type.FLOAT,
                            num_lexem, i
                        )
                    else:
                        return self.Failure(i, i + 1)
                    i = new_i
                case '(':
                    tok = Lexer_tok(Lexer_type.LPAR, '(', i)
                case ')':
                    tok = Lexer_tok(Lexer_type.RPAR, ')', i)
                case '[':
                    tok = Lexer_tok(Lexer_type.LSQB, '[', i)
                case ']':
                    tok = Lexer_tok(Lexer_type.RSQB, ']', i)
                case ',':
                    tok = Lexer_tok(Lexer_type.COMMA, ',', i)
                case _:
                    match, new_i = self.find_longest_match(i)
                    if match in ('True', 'False'):
                        tok = Lexer_tok(Lexer_type.BOOL, match, i)
                    elif match == 'None':
                        tok = Lexer_tok(Lexer_type.NONE, match, i)
                    else:
                        if match in self.keyword_op.keys():
                            assert isinstance(match, str)
                            tok = Lexer_tok(self.keyword_op[match], match, i)
                        elif match is not None:
                            tok = Lexer_tok(Lexer_type.IDENT, match, i)
                        else:
                            return self.Failure(i, i)
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
    
    def check_leading_zero(self, num: str, pos: int) -> Failure | None:
        if len(num) > 1 and num[0] == '0' and num[1] != '.':
            return self.Failure(pos, pos + len(num))
        return None


class Parser:
    """
    Recursive decent parser combined with packrat logic,
    that takes list of tokens and build AST tree with
    semantically same grammer as Python
    """

    __slots__ = [
        'tokens', 'pos', '_cache', 'failure', '_rule_stack_count', '_rules_count'
    ]

    MAX_RULES_STACK = 1000
    MAX_RULES = 10000000

    def __init__(self, tokens: list[Lexer_tok]):
        self.tokens = tokens
        self.pos = 0
        self.failure: Parser.Failure | None = None
        self._cache: dict[tuple[str, int], tuple[nodes | None, int]] = {}
        self._rule_stack_count = 0
        self._rules_count = 0

    @dataclass(slots=True, frozen=True)
    class Failure(BaseFailure):
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
    def print_meta(funct: Callable[[Parser], nodes | None]) -> Callable[[Parser], nodes | None]:
        """
        decorator for debugging.
        Needs to be placed right over the rule
        """

        def wrapper(self: Parser) -> nodes | None:
            print("RULE: ", funct.__name__)
            print("POS: ", self.pos)
            print("LIST_LEN: ", len(self.tokens))
            print("TOKEN: ", self.peek())
            print()
            ast = funct(self)
            print("RETURNING FROM: ", funct.__name__)
            print("AST:")
            pprint(ast)
            print()
            return ast
        return wrapper

    @staticmethod
    def track(funct: Callable[[Parser], nodes | None]) -> Callable[[Parser], nodes | None]:
        """
        decorator, that counts ammount of called rules
        and ammount of called rules ont the call stack.
        If maximum is reached, raise error.
        """

        def wrapper(self: Parser) -> nodes | None:
            self._rule_stack_count += 1
            self._rules_count += 1
            if self._rule_stack_count > self.MAX_RULES_STACK:
                raise RuntimeError('Max rule call stack height reached')
            if self._rules_count > self.MAX_RULES:
                raise RuntimeError('Max rules count reached')
            try:
                return funct(self)
            finally:
                self._rule_stack_count -= 1
        return wrapper

    @staticmethod
    def memo(funct: Callable[[Parser], nodes | None]) -> Callable[[Parser], nodes | None]:
        """
        decorator, that memoize answer and new position of the rules,
        based on their name and position.
        """

        def wrapper(self: Parser) -> nodes | None:
            key = (funct.__name__, self.pos)
            if key in self._cache:
                result, new_pos = self._cache[key]
                self.pos = new_pos
                return result
            else:
                result = funct(self)
                self._cache[key] = (result, self.pos)
                return result
        return wrapper
    
    @staticmethod
    def backtrack_pos(funct: Callable[[Parser], nodes | None]) -> Callable[[Parser], nodes | None]:
        def wrapper(self: Parser) -> nodes | None:
            orig_pos = self.pos
            ret = funct(self)
            if ret is None:
                self.pos = orig_pos
                return ret
            else:
                return ret
        return wrapper

    def peek(self) -> Lexer_tok:
        """returns token, which pointer points to"""

        return self.tokens[self.pos]
    
    def previous(self) -> Lexer_tok:
        """returns previous Lexer token from self.tokens"""

        return self.tokens[self.pos - 1]

    def match(self, token: Lexer_type) -> bool:
        """
        tries to match Lexer_type. If it success,
        moves pointer and return True. If not, do nothing
        and returns False
        """

        tok = self.peek()
        state = False
        if tok.typ == token:
            state = True
        if state:
            self.pos += 1
        return state

    def expect(self, token: Lexer_type, lexem: str) -> bool:
        """
        tries to match the token. If it success, moves pointer
        and return True. If not, pointer stay, return False a and set new
        instance Failiure object with provided lexem
        """

        if self.match(token):
            return True

        self.create_fail(self.pos, self.peek(), [lexem])
        return False

    def parse(self) -> nodes | Failure:
        """main method to execute parsing"""

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
    @backtrack_pos
    def expr(self) -> nodes | None:
        return self.disjunction()

    def iterator_op(self,
                    accept_op: dict[Lexer_type, Parser_tok],
                    next_rule: Callable[[], nodes | None]) -> nodes | None:
        left_node = next_rule()

        if left_node is None:
            return left_node

        while True:
            skip = True
            for key, val in accept_op.items():
                tok = self.peek()
                if self.match(key):
                    skip = False
                    right_node = next_rule()
                    if right_node is None:
                        return right_node
                    left_node = BinaryOp(val, left_node, right_node, tok)
            if skip:
                break

        return left_node

    @track
    @memo
    @backtrack_pos
    def disjunction(self) -> nodes | None:
        return self.iterator_op(
            {Lexer_type.OR: Parser_tok.Or},self.conjunction
        )

    @track
    @memo
    @backtrack_pos
    def conjunction(self) -> nodes | None:
        return self.iterator_op(
            {Lexer_type.AND: Parser_tok.And}, self.compare_operator
        )

    @track
    @memo
    @backtrack_pos
    def compare_operator(self) -> nodes | None:
        next_rule = self.negation
        left_node = next_rule()
        lexer_operators = {
            Lexer_type.IN: Parser_tok.In,
            Lexer_type.LE: Parser_tok.Le,
            Lexer_type.GE: Parser_tok.Ge,
            Lexer_type.LT: Parser_tok.Lt,
            Lexer_type.GT: Parser_tok.Gt,
            Lexer_type.EQ: Parser_tok.Eq,
            Lexer_type.NE: Parser_tok.Ne
        }
        if left_node is None:
            return left_node

        operators: list[tuple[Parser_tok, list[Lexer_tok]]] = []
        operands = [left_node]

        while True:
            skip = False
            tok = self.peek()
            for key, val in lexer_operators.items():
                if self.match(key):
                    skip = True
                    right_node = next_rule()
                    if right_node is None:
                        return right_node
                    operators.append((val, [tok]))
                    operands.append(right_node)
                    break
            if skip:
                continue

            if self.match(Lexer_type.NOT):
                tok_2 = self.peek()
                if self.match(Lexer_type.IN):
                    right_node = next_rule()
                    if right_node is None:
                        return right_node
                    operators.append((Parser_tok.NotIn, [tok, tok_2]))
                    operands.append(right_node)
                    continue
                else:
                    self.pos -= 1

            if self.match(Lexer_type.IS):
                tok_2 = self.peek()
                if self.match(Lexer_type.NOT):
                    right_node = next_rule()
                    if right_node is None:
                        return right_node
                    operators.append((Parser_tok.IsNot, [tok, tok_2]))
                    operands.append(right_node)
                else:
                    right_node = next_rule()
                    if right_node is None:
                        return right_node
                    operators.append((Parser_tok.Is, [tok]))
                    operands.append(right_node)
                continue

            if len(operators) != 0:
                left_node = CompareNode(operators, operands)
            break

        return left_node

    @track
    @memo
    @backtrack_pos
    def negation(self) -> nodes | None:
        next_rule = self.low_ord_operator
        tok = self.peek()

        if self.match(Lexer_type.NOT):
            node = self.negation()
            if node is None:
                return node
            return UnaryOp(Parser_tok.Not, node, tok)

        return next_rule()

    @track
    @memo
    @backtrack_pos
    def low_ord_operator(self) -> nodes | None:
        return self.iterator_op(
            {
                Lexer_type.PLUS: Parser_tok.Plus,
                Lexer_type.MINUS: Parser_tok.Minus
            },
            self.high_ord_operator
        )

    @track
    @memo
    @backtrack_pos
    def high_ord_operator(self) -> nodes | None:
        return self.iterator_op(
            {
                Lexer_type.DSLASH: Parser_tok.FloorDiv,
                Lexer_type.SLASH: Parser_tok.TrueDiv,
                Lexer_type.PERCENT: Parser_tok.Mod,
                Lexer_type.STAR: Parser_tok.Mult
            },
            self.factor
        )

    @track
    @memo
    @backtrack_pos
    def factor(self) -> nodes | None:
        next_rule = self.power
        accept_op = {
            Lexer_type.PLUS: Parser_tok.UnPlus,
            Lexer_type.MINUS: Parser_tok.UnMinus
        }

        tok = self.peek()
        for key, val in accept_op.items():
            if self.match(key):
                node = self.factor()
                if node is None:
                    return node
                return UnaryOp(val, node, tok)

        return next_rule()

    @track
    @memo
    @backtrack_pos
    def power(self) -> nodes | None:
        next_rule = self.atom
        left_node = next_rule()

        tok = self.peek()
        if self.match(Lexer_type.DSTAR):
            right_node = self.factor()
            if left_node is None or right_node is None:
                return right_node
            return BinaryOp(Parser_tok.Power, left_node, right_node, tok)

        return left_node

    @track
    @memo
    @backtrack_pos
    def atom(self) -> nodes | None:
        tok = self.peek()

        if self.match(Lexer_type.INT):
            return Value(Parser_tok.Int, int(tok.lexem), tok)
        elif self.match(Lexer_type.FLOAT):
            return Value(Parser_tok.Float, float(tok.lexem), tok)
        elif self.match(Lexer_type.BOOL):
            return Value(
                Parser_tok.Bool,
                True if tok.lexem == 'True' else False,
                tok
            )
        elif self.match(Lexer_type.IDENT):
            return Value(Parser_tok.Ident, tok.lexem, tok)
        elif self.match(Lexer_type.STR):
            return Value(Parser_tok.Str, tok.lexem[1:-1], tok)
        elif self.match(Lexer_type.NONE):
            return Value(Parser_tok.None_, None, tok)

        save = self.pos
        if self.match(Lexer_type.LSQB):
            cont_node = self.list_rule()
            if cont_node is not None:
                return cont_node
        elif self.match(Lexer_type.LPAR):
            cont_node = self.tuple_rule()
            if cont_node is not None:
                return cont_node
        self.pos = save

        if self.match(Lexer_type.LPAR):
            bracket_node = self.expr()
            if self.expect(Lexer_type.RPAR, ')'):
                return bracket_node
            return None

        expect = ['int', 'float', 'bool', 'ident', 'str', 'container', 'expr']
        self.create_fail(self.pos, self.peek(), expect)
        return None

    @track
    @memo
    def list_rule(self) -> Collection | None:
        open_bracket = self.previous()
        collection: list[nodes] = []

        if self.match(Lexer_type.RSQB):
            brackets = (open_bracket, self.previous())
            return Collection(Parser_tok.List, collection, brackets)

        node = self.expr()
        if node is None:
            return node
        collection.append(node)

        while self.match(Lexer_type.COMMA):
            if self.match(Lexer_type.RSQB):
                brackets = (open_bracket, self.previous())
                return Collection(Parser_tok.List, collection, brackets)
            node = self.expr()
            if node is None:
                return node
            collection.append(node)

        if not self.expect(Lexer_type.RSQB, ']'):
            return None

        brackets = (open_bracket, self.previous())
        return Collection(Parser_tok.List, collection, brackets)

    @track
    @memo
    def tuple_rule(self) -> Collection | None:
        open_bracket = self.previous()
        collection: list[nodes] = []

        if self.match(Lexer_type.RPAR):
            brackets = (open_bracket, self.previous())
            return Collection(Parser_tok.Tuple, collection, brackets)

        node = self.expr()
        if node is None:
            return node
        collection.append(node)

        if not self.expect(Lexer_type.COMMA, ','):
            return None

        if self.match(Lexer_type.RPAR):
            brackets = (open_bracket, self.previous())
            return Collection(Parser_tok.Tuple, collection, brackets)

        node = self.expr()
        if node is None:
            return node
        collection.append(node)

        while self.match(Lexer_type.COMMA):
            if self.match(Lexer_type.RPAR):
                brackets = (open_bracket, self.previous())
                return Collection(Parser_tok.Tuple, collection, brackets)
            node = self.expr()
            if node is None:
                return node
            collection.append(node)

        if not self.expect(Lexer_type.RPAR, ')'):
            return None

        brackets = (open_bracket, self.previous())
        return Collection(Parser_tok.Tuple, collection, brackets)


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
