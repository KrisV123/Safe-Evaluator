import random
import string
import traceback
from typing import Any, assert_never
from enum import IntEnum, auto
from pprint import pformat

from evaluator.types import (
    nodes, UnaryOp, BinaryOp, Value, Collection, CompareNode,
    Parser_tok, Lexer_tok, Lexer_type
)
from evaluator.types import atom_types

class Random_ast:
    """
    Class to generate randomly loocking AST tree.
    All lexer tokens in AST are replaced with placeholder value,
    because it is irelevant in evaluatoin process.
    """

    random_atom = (
        Parser_tok.Int,
        Parser_tok.Float,
        Parser_tok.None_,
        Parser_tok.Str,
        Parser_tok.Bool,
        Parser_tok.Ident
    )

    random_binary_op = (
        Parser_tok.Or,
        Parser_tok.And,
        Parser_tok.Plus,
        Parser_tok.Minus,
        Parser_tok.Mult,
        Parser_tok.Power,
        Parser_tok.TrueDiv,
        Parser_tok.FloorDiv,
        Parser_tok.Mod
    )

    random_unary_op = (
        Parser_tok.Not,
        Parser_tok.UnPlus,
        Parser_tok.UnMinus
    )

    random_compare_op = (
        Parser_tok.In,
        Parser_tok.NotIn,
        Parser_tok.Is,
        Parser_tok.IsNot,
        Parser_tok.Eq,
        Parser_tok.Ne,
        Parser_tok.Gt,
        Parser_tok.Lt,
        Parser_tok.Ge,
        Parser_tok.Le
    )

    random_collection = (
        Parser_tok.List,
        Parser_tok.Tuple
    )

    class NodesEnum(IntEnum):
        Value = auto()
        UnaryOp = auto()
        BinaryOp = auto()
        Collection = auto()
        CompareNode = auto()


    random_nodes = [
        (NodesEnum.Value, 10),
        (NodesEnum.UnaryOp, 35),
        (NodesEnum.BinaryOp, 35),
        (NodesEnum.Collection, 10),
        (NodesEnum.CompareNode, 10)
    ]

    plcholder_lexer_tok = Lexer_tok(Lexer_type.EOF, '', 0)

    __slots__ = ('max_depth')

    def __init__(self, max_depth: int):
        self.max_depth = max_depth

    @classmethod
    def generate_atom_val(cls, atom_type: Parser_tok) -> atom_types:
        if atom_type == Parser_tok.Int:
            return random.choices((0, random.randint(1, 1000)))
        elif atom_type == Parser_tok.Float:
            return random.random()
        elif atom_type in (Parser_tok.Str, Parser_tok.Ident):
            str_len = random.randint(1,10)
            return ''.join(random.choices(string.ascii_letters, k=str_len))
        elif atom_type == Parser_tok.Bool:
            (bool_val,) = random.choices((True, False))
            return bool_val
        elif atom_type == Parser_tok.None_:
            return None
        else:
            raise RuntimeError(f'{str(atom_type)} is not accepted')

    def generate_rand_ast(self, current_depth: int=0) -> nodes:
        """Generate random ast tree. Keed current_depth param at default value"""

        enum_nodes, weights = zip(*self.random_nodes)
        (node,) = random.choices(enum_nodes, weights=weights)

        if current_depth >= self.max_depth:
            node = self.NodesEnum.Value

        if node == self.NodesEnum.Value:
            tok = random.choice(self.random_atom)
            val = self.generate_atom_val(tok)
            return Value(tok, val, self.plcholder_lexer_tok)

        elif node == self.NodesEnum.UnaryOp:
            op = random.choice(self.random_unary_op)
            return UnaryOp(
                op,
                self.generate_rand_ast(current_depth + 1),
                self.plcholder_lexer_tok
            )
        elif node == self.NodesEnum.BinaryOp:
            op = random.choice(self.random_binary_op)
            return BinaryOp(
                op,
                self.generate_rand_ast(current_depth + 1),
                self.generate_rand_ast(current_depth + 1),
                self.plcholder_lexer_tok
            )
        elif node == self.NodesEnum.Collection:
            collection_typ = random.choice(self.random_collection)
            collection_len = random.randint(0,5)
            rand_collection = [
                self.generate_rand_ast(current_depth + 1)
                for _ in range(collection_len)
            ]
            brackets = (
                (Lexer_tok(Lexer_type.LPAR, '(', 0), Lexer_tok(Lexer_type.RPAR, ')', 0))
                if collection_typ == Parser_tok.Tuple
                else (Lexer_tok(Lexer_type.LSQB, '[', 0), Lexer_tok(Lexer_type.RSQB, ']', 0))
            )

            return Collection(
                collection_typ,
                rand_collection,
                brackets
            )
        elif node == self.NodesEnum.CompareNode:
            op_amount = random.randint(1,5)
            rand_op = random.choices(self.random_compare_op, k=op_amount)
            operators = [(op, [self.plcholder_lexer_tok]) for op in rand_op]
            operands = [
                self.generate_rand_ast(current_depth + 1)
                for _ in range(op_amount + 1)
            ]
            return CompareNode(operators, operands)
        else:
            assert_never(node)


def create_all_lexer_toks() -> list[Lexer_tok]:
    lexem: str | None = None

    toks_list = []
    for typ in Lexer_type:
        if typ == Lexer_type.INT:
            lexem = str(random.randint(1, 100))
        elif typ == Lexer_type.FLOAT:
            lexem = str(random.random())
        elif typ == Lexer_type.BOOL:
            lexem = str(random.choice(['True', 'False']))
        elif typ == Lexer_type.IDENT:
            lexem = ''.join(random.choices(string.ascii_letters, k=5))
        elif typ == Lexer_type.STR:
            lexem = ''.join(random.choices(string.ascii_letters, k=5))
        elif typ == Lexer_type.NONE:
            lexem = 'None'
        elif typ == Lexer_type.EOF:
            lexem = '$'

        if lexem is not None:
            toks_list.append(Lexer_tok(typ, lexem, 0))
            lexem = None
            continue

        toks_list.append(Lexer_tok(typ, '', 0))

    return toks_list

def log_error_from_fuzzer(test_name: str, input: Any, error: Exception) -> None:
    error_log = (
        f"TEST NAME:\n {test_name}\n\n"

        f"INPUT:\n {pformat(input)}\n"
        f"OUTPUT:\n {pformat(error)}\n"
        f"TRACEBACK:\n {pformat(traceback.format_tb(error.__traceback__))}\n"
        "--------------------------------------------------------------------------------------\n\n"
    )

    with open('tests/test_interpreter/fuzzer_error.log', 'a') as f:
        f.write(error_log)
