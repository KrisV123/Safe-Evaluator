
# SOURCE OF TRUTH FOR WHOLE CODEBASE

from __future__ import annotations

from enum import IntEnum, auto
from dataclasses import dataclass
from typing import get_args, get_origin, Literal

atom_types = (
    str | int | float | bool | None |
    list["atom_types"] | tuple["atom_types", ...]
)

# all types that can be converted in ipc, needs to match with atom_types
json_atom_types = Literal['str', 'int', 'float', 'bool', 'NoneType', 'list', 'tuple']

# atom_types enumerated in tuple in runtime objects
atom_types_runtime = tuple(
    typ if isinstance(typ, type) else get_origin(typ)
    for typ in get_args(atom_types)
)

# ------------------------------------ Tokens ---------------------------------

@dataclass(slots=True, frozen=True)
class Lexer_tok:
    typ: Lexer_type
    lexem: str
    position: int


class Lexer_type(IntEnum):

    # OPERATORS

    # logic
    OR = auto()
    AND = auto()
    NOT = auto()

    # compare op
    IN = auto()
    IS = auto()
    EQ = auto()
    NE = auto()
    GT = auto()
    LT = auto()
    GE = auto()
    LE = auto()

    # numeric
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    DSTAR = auto()
    SLASH = auto()
    DSLASH = auto()
    PERCENT = auto()

    # ATOMS

    STR = auto()
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    IDENT = auto()
    NONE = auto()

    # REST

    LSQB = auto()
    RSQB = auto()
    LPAR = auto()
    RPAR = auto()
    COMMA = auto()
    EOF = auto()


class Parser_tok(IntEnum):

    # OPERATORS

    # logic
    Or = auto()
    And = auto()
    Not = auto()

    # compare op
    In = auto()
    NotIn = auto()
    Is = auto()
    IsNot = auto()
    Eq = auto()
    Ne = auto()
    Gt = auto()
    Lt = auto()
    Ge = auto()
    Le = auto()

    # numeric
    Plus = auto()
    UnPlus = auto()
    Minus = auto()
    UnMinus = auto()
    Mult = auto()
    Power = auto()
    TrueDiv = auto()
    FloorDiv = auto()
    Mod = auto()

    # ATOMS

    Str = auto()
    Int = auto()
    Float = auto()
    Bool = auto()
    Ident = auto()
    None_ = auto()
    List = auto()
    Tuple = auto()


# ---------------------------------- AST nodes ---------------------------------


@dataclass(slots=True, frozen=True)
class BinaryOp:
    token: Parser_tok
    left_child: nodes
    right_child: nodes
    lexer_tok: Lexer_tok


@dataclass(slots=True, frozen=True)
class UnaryOp:
    token: Parser_tok
    child: nodes
    lexer_tok: Lexer_tok


@dataclass(slots=True, frozen=True)
class Value:
    token: Parser_tok
    value: atom_types
    lexer_tok: Lexer_tok


@dataclass(slots=True, frozen=True)
class Collection:
    token: Parser_tok
    collection: list[nodes]
    brackets: tuple[Lexer_tok, Lexer_tok]


@dataclass(slots=True, frozen=True)
class CompareNode:
    operators: list[tuple[Parser_tok, list[Lexer_tok]]]
    operands: list[nodes]


@dataclass(slots=True, frozen=True)
class Constant:
    value: atom_types
    source: nodes


nodes = UnaryOp | BinaryOp | Value | Collection | CompareNode | Constant
