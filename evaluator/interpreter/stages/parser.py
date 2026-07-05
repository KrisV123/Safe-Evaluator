from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pprint import pprint

from evaluator.types import (
    nodes,
    Lexer_type, Parser_tok, Lexer_tok,
    BinaryOp, UnaryOp, Value, Collection, CompareNode
)
from evaluator.interpreter.stages.base import BaseFailure

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
