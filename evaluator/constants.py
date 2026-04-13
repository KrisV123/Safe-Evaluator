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

class CompareOP(IntEnum):
    IS_NOT = auto()
    IS = auto()
    LTE = auto()
    GTE = auto()
    LT = auto()
    GT = auto()
    EQ = auto()
    NE = auto()

"""is and is not is not added cause it is handled differently"""
CompareOP_lookup = {
    '<=': CompareOP.LTE,
    '>=': CompareOP.GTE,
    '<': CompareOP.LT,
    '>': CompareOP.GT,
    '==': CompareOP.EQ,
    '!=': CompareOP.NE
}

CompareOP_lookup_reverse = {
    CompareOP.LTE: '<=',
    CompareOP.GTE: '>=',
    CompareOP.LT: '<',
    CompareOP.GT: '>',
    CompareOP.EQ: '==',
    CompareOP.NE: '!='
}

class Lexer_type(IntEnum):
    OP = auto()
    STR = auto()
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    IDENT = auto()
    NONE = auto()
    OPEN_LIST = auto()
    CLOSE_LIST = auto()
    OPEN_TUPLE = auto()
    CLOSE_TUPLE = auto()
    COMMA = auto()
    EOF = auto()

op_table: dict[str, dict[str | CompareOP, Callable]] = {
    'binary': {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '//': operator.floordiv,
        '%': operator.mod,
        '**': operator.pow,
        'or': lambda x, y: x or y,
        'and': lambda x, y: x and y,
        'in': operator.contains,
        'is': operator.is_
    },
    'unary': {
        '+': operator.pos,
        '-': operator.neg,
        'not': operator.not_
    },
    'compare': {
        CompareOP.IS_NOT: operator.is_not,
        CompareOP.IS: operator.is_,
        CompareOP.LT: operator.lt,
        CompareOP.GT: operator.gt,
        CompareOP.LTE: operator.le,
        CompareOP.GTE: operator.ge,
        CompareOP.EQ: operator.eq,
        CompareOP.NE: operator.ne,
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

op_type_table:  dict[
                    str, dict[
                        str | CompareOP,
                        dict[
                            tuple, set[object]
                        ]
                    ]
                ] = {
    'binary': {
        '+': {
            **basic_num_typing,
            (str, str): {str},
            (list, list): {list}
        },
        '-': {
            **basic_num_typing,
        },
        '*': {
            **basic_num_typing,
            (str, int): {str},
            (list, int): {list}
        },
        '/': {
            (int, int): {float},
            (int, float): {float},
            (float, int): {float},
            (float, float): {float}
        },
        '//': {
            (int, int): {int},
            (int, float): {float},
            (float, int): {float},
            (float, float): {float}
        },
        '%': {
            **basic_num_typing
        },
        '**': {
            **basic_num_typing
        },
        'or': and_or_typing,
        'and': and_or_typing,
        'in': {
            (cont, typ): {int}
            for typ in basic_atom_types
            for cont in [list, tuple, str]
        },
    },
    'unary': {
        '+': {
            (int,): {int},
            (float,): {float}
        },
        '-': {
            (int,): {int},
            (float,): {float}
        },
        'not': {
            (obj,): {int} for obj in basic_atom_types
        }
    },
    'compare': {
        CompareOP.IS_NOT: is_is_not_typing,
        CompareOP.IS: is_is_not_typing,
        CompareOP.LT: basic_compare_typing,
        CompareOP.GT: basic_compare_typing,
        CompareOP.LTE: basic_compare_typing,
        CompareOP.GTE: basic_compare_typing,
        CompareOP.EQ: basic_compare_typing,
        CompareOP.NE: basic_compare_typing,
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
    token: Lexer_tok
    left_child: nodes
    right_child: nodes


@dataclass(slots=True, frozen=False)
class UnaryOp:
    token: Lexer_tok
    child: nodes


@dataclass(slots=True, frozen=False)
class Value:
    token: Lexer_tok


@dataclass(slots=True, frozen=False)
class Collection:
    typ: type[list | tuple]
    collection: list[nodes]


@dataclass(slots=True, frozen=False)
class CompareNode:
    operators: list[CompareOP]
    operands: list[nodes]


@dataclass(slots=True, frozen=False)
class Constant:
    value: atom_types | list[atom_types]
