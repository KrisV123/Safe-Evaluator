from __future__ import annotations
import operator
from collections.abc import Callable
from typing import TypedDict, Any
from evaluator.types import Parser_tok, atom_types, atom_types_runtime

# ------------------------------- Operators table -----------------------------

T_unary_op_table = dict[Parser_tok, Callable[[Any], atom_types]]

unary_op_table: T_unary_op_table = {
    Parser_tok.UnPlus: operator.pos,
    Parser_tok.UnMinus: operator.neg,
    Parser_tok.Not: operator.not_
}

T_binary_op_table = dict[Parser_tok, Callable[[Any, Any], atom_types]]

binary_op_table: T_binary_op_table = {
    Parser_tok.Plus: operator.add,
    Parser_tok.Minus: operator.sub,
    Parser_tok.Mult: operator.mul,
    Parser_tok.TrueDiv: operator.truediv,
    Parser_tok.FloorDiv: operator.floordiv,
    Parser_tok.Mod: operator.mod,
    Parser_tok.Power: operator.pow,
    Parser_tok.Or: lambda x, y: x or y,
    Parser_tok.And: lambda x, y: x and y,
}

T_compare_op_table = dict[Parser_tok, Callable[[Any, Any], bool]]

compare_op_table: T_compare_op_table = {
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

class Op_table(TypedDict):
    unary: T_unary_op_table
    binary: T_binary_op_table
    compare: T_compare_op_table


op_table: Op_table = {
    'unary': unary_op_table,
    'binary': binary_op_table,
    'compare': compare_op_table
}

# -------------------------------- Typing System -------------------------------

# In whole typing system, bool values are converted
# to coresponding integer and vais versa to reduce duplicity

basic_num_typing: dict[tuple[type, type], set[type]] = {
    (int, int): {int},
    (int, float): {float},
    (float, int): {float},
    (float, float): {float}
}

and_or_typing: dict[tuple[type, type], set[type]] = {
    (val_1, val_2): {val_1, val_2}
    for val_1 in atom_types_runtime
    for val_2 in atom_types_runtime
}

basic_compare_typing: dict[tuple[type, type], set[type[int]]] = {
    (int, int): {int},
    (float, float): {int},
    (int, float): {int},
    (float, int): {int},
    (str, str): {int},
    (list, list): {int}
}

is_is_not_typing: dict[tuple[type, type], set[type[int]]] = {
    (val_1, val_2): {int}
    for val_1 in atom_types_runtime
    for val_2 in atom_types_runtime
}

in_not_in_typing: dict[tuple[type, type], set[type[int]]] = {
    **{
        (typ, cont): {int}
        for typ in atom_types_runtime
        for cont in [list, tuple]
    },
    (str, str): {int}
}

T_op_unary_type_table = dict[Parser_tok, dict[tuple[type], set[type]]]

op_unary_type_table: T_op_unary_type_table = {
    Parser_tok.UnPlus: {
        (int,): {int},
        (float,): {float}
    },
    Parser_tok.UnMinus: {
        (int,): {int},
        (float,): {float}
    },
    Parser_tok.Not: {
        (obj,): {int} for obj in atom_types_runtime
    }    
}

T_op_binary_type_table = dict[Parser_tok, dict[tuple[type, type], set[type]]]

op_binary_type_table: T_op_binary_type_table = {
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
}

T_op_compare_type_table =  dict[Parser_tok, dict[tuple[type, type], set[type[int]]]]

op_compare_type_table: T_op_compare_type_table = {
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

class Op_type_table(TypedDict):
    unary: T_op_unary_type_table
    binary: T_op_binary_type_table
    compare: T_op_compare_type_table

op_type_table: Op_type_table = {
    'unary': op_unary_type_table,
    'binary': op_binary_type_table,
    'compare': op_compare_type_table
}
