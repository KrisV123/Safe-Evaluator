from __future__ import annotations
from typing import TypedDict, Literal
from evaluator.types import json_atom_types

class T_serialized_atom(TypedDict):
    type: json_atom_types
    value: str | int | float | bool | None | list["T_serialized_atom"]


class Lexer_tok_dict(TypedDict):
    typ: int
    lexem: str
    position: int


class Value_dict(TypedDict):
    name: Literal['Value']
    token: int
    value: T_serialized_atom
    lexer_tok: str


class UnaryOp_dict(TypedDict):
    name: Literal['UnaryOp']
    token: int
    child: dict_nodes
    lexer_tok: str


class BinaryOp_dict(TypedDict):
    name: Literal['BinaryOp']
    token: int
    left_child: dict_nodes
    right_child: dict_nodes
    lexer_tok: str


class Collection_dict(TypedDict):
    name: Literal['Collection']
    token: int
    collection: list[dict_nodes]
    brackets: list[str]


class Parser_Lexer_toks_tuple(TypedDict):
    parser_tok: int
    lexer_toks: list[str]


class CompareNode_dict(TypedDict):
    name: Literal['CompareNode']
    operators: list[Parser_Lexer_toks_tuple]
    operands: list[dict_nodes]


class Constant_dict(TypedDict):
    name: Literal['Constant']
    value: T_serialized_atom
    source: dict_nodes


dict_nodes = Value_dict | UnaryOp_dict | BinaryOp_dict | Collection_dict | CompareNode_dict | Constant_dict
