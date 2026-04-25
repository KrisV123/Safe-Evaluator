import operator
from collections.abc import Callable
from enum import IntEnum, auto
from types import NoneType
from dataclasses import dataclass

type atom_types = (
    str | int | float | bool | None |
    list['atom_types'] | tuple['atom_types', ...]
)
#bool is skipped cause it's represented as int
basic_atom_types = (str, int, float, NoneType, list, tuple)

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

    # REST
    STR = auto()
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    IDENT = auto()
    NONE = auto()
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

    #numeric
    Plus = auto()
    UnPlus = auto()
    Minus = auto()
    UnMinus = auto()
    Mult = auto()
    Power = auto()
    TrueDiv = auto()
    FloorDiv = auto()
    Mod = auto()

    #rest
    Str = auto()
    Int = auto()
    Float = auto()
    Bool = auto()
    Ident = auto()
    None_ = auto()


op_table: dict[str, dict[Parser_tok, Callable]] = {
    'binary': {
        Parser_tok.Plus: operator.add,
        Parser_tok.Minus: operator.sub,
        Parser_tok.Mult: operator.mul,
        Parser_tok.TrueDiv: operator.truediv,
        Parser_tok.FloorDiv: operator.floordiv,
        Parser_tok.Mod: operator.mod,
        Parser_tok.Power: operator.pow,
        Parser_tok.Or: lambda x, y: x or y,
        Parser_tok.And: lambda x, y: x and y,
    },
    'unary': {
        Parser_tok.UnPlus: operator.pos,
        Parser_tok.UnMinus: operator.neg,
        Parser_tok.Not: operator.not_
    },
    'compare': {
        Parser_tok.In: lambda x, y: x in y,
        Parser_tok.NotIn: lambda x, y: x not in y,
        Parser_tok.IsNot: operator.is_not,
        Parser_tok.Is: operator.is_,
        Parser_tok.Lt: operator.lt,
        Parser_tok.Gt: operator.gt,
        Parser_tok.Le: operator.le,
        Parser_tok.Ge: operator.ge,
        Parser_tok.Eq: operator.eq,
        Parser_tok.Ne: operator.ne,
    }
}

"""
In whole typing system, bool values are converted
to coresponding integer and vais versa to reduce duplicity
"""

basic_num_typing: dict[tuple[object, object], set[object]] = {
    (int, int): {int},
    (int, float): {float},
    (float, int): {float},
    (float, float): {float}
}

and_or_typing: dict[tuple[object, object], set[object]] = {
    (val_1, val_2): {val_1, val_2}
    for val_1 in basic_atom_types
    for val_2 in basic_atom_types
}

basic_compare_typing: dict[tuple[object, object], set[object]] = {
    (int, int): {int},
    (float, float): {int},
    (int, float): {int},
    (float, int): {int},
    (str, str): {int},
    (list, list): {int}
}

is_is_not_typing: dict[tuple[object, object], set[object]] = {
    (val_1, val_2): {int}
    for val_1 in basic_atom_types
    for val_2 in basic_atom_types
}

in_not_in_typing: dict[tuple[object, object], set[object]] = {
    (typ, cont): {int}
    for typ in basic_atom_types
    for cont in [list, tuple, str]
}

op_type_table:  dict[
                    str, dict[
                        Parser_tok,
                        dict[
                            tuple, set[object]
                        ]
                    ]
                ] = {
    'binary': {
        Parser_tok.Plus: {
            **basic_num_typing,
            (str, str): {str},
            (list, list): {list}
        },
        Parser_tok.Minus: {
            **basic_num_typing,
        },
        Parser_tok.Mult: {
            **basic_num_typing,
            (str, int): {str},
            (list, int): {list}
        },
        Parser_tok.TrueDiv: {
            (int, int): {float},
            (int, float): {float},
            (float, int): {float},
            (float, float): {float}
        },
        Parser_tok.FloorDiv: {
            (int, int): {int},
            (int, float): {float},
            (float, int): {float},
            (float, float): {float}
        },
        Parser_tok.Mod: {
            **basic_num_typing
        },
        Parser_tok.Power: {
            **basic_num_typing
        },
        Parser_tok.Or: and_or_typing,
        Parser_tok.And: and_or_typing,
    },
    'unary': {
        Parser_tok.UnPlus: {
            (int,): {int},
            (float,): {float}
        },
        Parser_tok.UnMinus: {
            (int,): {int},
            (float,): {float}
        },
        Parser_tok.Not: {
            (obj,): {int} for obj in basic_atom_types
        }
    },
    'compare': {
        Parser_tok.In: in_not_in_typing,
        Parser_tok.NotIn: in_not_in_typing,
        Parser_tok.IsNot: is_is_not_typing,
        Parser_tok.Is: is_is_not_typing,
        Parser_tok.Lt: basic_compare_typing,
        Parser_tok.Gt: basic_compare_typing,
        Parser_tok.Le: basic_compare_typing,
        Parser_tok.Ge: basic_compare_typing,
        Parser_tok.Eq: basic_compare_typing,
        Parser_tok.Ne: basic_compare_typing,
    }
}

type nodes = UnaryOp | BinaryOp | Value | Collection | CompareNode | Constant

@dataclass(slots=True, frozen=True)
class Lexer_tok:
    typ: Lexer_type
    lexem: str
    position: int


@dataclass(slots=True, frozen=False)
class BinaryOp:
    token: Parser_tok
    left_child: nodes
    right_child: nodes


@dataclass(slots=True, frozen=False)
class UnaryOp:
    token: Parser_tok
    child: nodes


@dataclass(slots=True, frozen=False)
class Value:
    token: Parser_tok
    value: atom_types


@dataclass(slots=True, frozen=False)
class Collection:
    typ: type[list | tuple]
    collection: list[nodes]


@dataclass(slots=True, frozen=False)
class CompareNode:
    operators: list[Parser_tok]
    operands: list[nodes]


@dataclass(slots=True, frozen=False)
class Constant:
    value: atom_types | list[atom_types]
