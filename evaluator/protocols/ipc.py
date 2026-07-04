from __future__ import annotations
import json
from typing import cast, assert_never

import evaluator.types as iconst
import evaluator.protocols.ipc_types as ipc_const

class ValueCodec:

    @staticmethod
    def encode(value: iconst.atom_types) -> ipc_const.T_serialized_atom:
        """
        Serialize basic python value into TypedDict,
        that holds information about value and type.

        Can serialize: str, int, float, bool, None, list, tuple
        """

        typ = type(value).__name__
        cast_typ = cast(ipc_const.json_atom_types, typ)
        match cast_typ:
            case 'list' | 'tuple':
                assert isinstance(value, (list, tuple))
                collection = [ValueCodec.encode(x) for x in value]
                return {"type": cast_typ, "value": collection}
            case 'str' | 'int' | 'float' | 'bool' | 'NoneType':
                assert isinstance(value, (str, int, float, bool, type(None)))
                return {"type": cast_typ, "value": value}
            case _ as unreachable:
                assert_never(unreachable)

    @staticmethod
    def decode(data: ipc_const.T_serialized_atom) -> iconst.atom_types:
        """Deserialize data in T_serialized_atom TypedDict structure"""

        typ, value = data["type"], data["value"]        
        cast_typ = cast(ipc_const.json_atom_types, typ)
        match cast_typ:
            case 'list' | 'tuple':
                assert isinstance(value, (list, tuple))
                collection = [ValueCodec.decode(x) for x in value]

                if cast_typ == "list":
                    return collection
                elif cast_typ == "tuple":
                    return tuple(collection)
                else:
                    raise SyntaxError(
                        f'In ValueCoded.decode, unexpected typ for list value: {typ!r}'
                    )
            case 'str' | 'int' | 'float' | 'bool' | 'NoneType':
                assert isinstance(value, (str, int, float, bool, type(None)))
                return cast(str | int | float | bool | None, value)
            case _ as unreachable:
                assert_never(unreachable)


class LexerTokCodec:

    @staticmethod
    def encode(tok: iconst.Lexer_tok) -> str:
        return json.dumps({"typ": tok.typ, "lexem": tok.lexem, "position": tok.position})

    @staticmethod
    def decode(str_tok: str) -> iconst.Lexer_tok:
        dict_tok = cast(ipc_const.Lexer_tok_dict, json.loads(str_tok))
        return iconst.Lexer_tok(
            iconst.Lexer_type(dict_tok['typ']),
            dict_tok['lexem'],
            dict_tok['position']
        )

class ASTCodec:

    @staticmethod
    def encode(ast: iconst.nodes) -> str:
        """Serialize AST into string in JSON format"""

        return json.dumps(ASTCodec._encode_worker(ast))

    @staticmethod
    def _encode_worker(node: iconst.nodes) -> dict:
        if isinstance(node, iconst.Value):
            return {
                'name': 'Value',
                'token': node.token,
                'value': ValueCodec.encode(node.value),
                'lexer_tok': LexerTokCodec.encode(node.lexer_tok)
            }
        elif isinstance(node, iconst.UnaryOp):
            return {
                'name': 'UnaryOp',
                'token': node.token,
                'child': ASTCodec._encode_worker(node.child),
                'lexer_tok': LexerTokCodec.encode(node.lexer_tok)
            }
        elif isinstance(node, iconst.BinaryOp):
            return {
                'name': 'BinaryOp',
                'token': node.token,
                'left_child': ASTCodec._encode_worker(node.left_child),
                'right_child': ASTCodec._encode_worker(node.right_child),
                'lexer_tok': LexerTokCodec.encode(node.lexer_tok)
            }
        elif isinstance(node, iconst.Collection):
            left, right = node.brackets
            return {
                'name': 'Collection',
                'token': node.token,
                'collection': [ASTCodec._encode_worker(n) for n in node.collection],
                'brackets': [
                    LexerTokCodec.encode(left),
                    LexerTokCodec.encode(right),
                ]
            }
        elif isinstance(node, iconst.CompareNode):
            return {
                'name': 'CompareNode',
                'operators': [
                    {
                        'parser_tok': parser_tok,
                        'lexer_toks': [LexerTokCodec.encode(tok) for tok in lexer_toks]
                    }
                    for parser_tok, lexer_toks
                    in node.operators
                ],
                'operands': [ASTCodec._encode_worker(n) for n in node.operands]
            }
        elif isinstance(node, iconst.Constant):
            return {
                'name': 'Constant',
                'value': ValueCodec.encode(node.value),
                'source': ASTCodec._encode_worker(node.source)
            }
        else:
            assert_never(node)

    @staticmethod
    def decode(json_ast: str) -> iconst.nodes:
        """Deserialize string in JSON format into AST python data structure"""

        return ASTCodec._decode_worker(json.loads(json_ast))

    @staticmethod
    def _decode_worker(dict_ast: ipc_const.dict_nodes) -> iconst.nodes:
        match dict_ast['name']:
            case 'Value':
                value_dict = cast(ipc_const.Value_dict, dict_ast)
                return iconst.Value(
                    iconst.Parser_tok(value_dict['token']),
                    ValueCodec.decode(value_dict['value']),
                    LexerTokCodec.decode(value_dict['lexer_tok'])
                )
            case 'UnaryOp':
                unary_op_dict = cast(ipc_const.UnaryOp_dict, dict_ast)
                return iconst.UnaryOp(
                    iconst.Parser_tok(unary_op_dict['token']),
                    ASTCodec._decode_worker(unary_op_dict['child']),
                    LexerTokCodec.decode(unary_op_dict['lexer_tok'])
                )
            case 'BinaryOp':
                binary_op_dict = cast(ipc_const.BinaryOp_dict, dict_ast)
                return iconst.BinaryOp(
                    iconst.Parser_tok(binary_op_dict['token']),
                    ASTCodec._decode_worker(binary_op_dict['left_child']),
                    ASTCodec._decode_worker(binary_op_dict['right_child']),
                    LexerTokCodec.decode(binary_op_dict['lexer_tok'])
                )
            case 'Collection':
                collection_dict = cast(ipc_const.Collection_dict, dict_ast)
                brackets = collection_dict['brackets']
                return iconst.Collection(
                    iconst.Parser_tok(collection_dict['token']),
                    [ASTCodec._decode_worker(d) for d in collection_dict['collection']],
                    (
                        LexerTokCodec.decode(brackets[0]),
                        LexerTokCodec.decode(brackets[1])
                    )
                )
            case 'CompareNode':
                compare_dict = cast(ipc_const.CompareNode_dict, dict_ast)
                return iconst.CompareNode(
                    [
                        (
                            iconst.Parser_tok(op['parser_tok']),
                            [LexerTokCodec.decode(tok) for tok in op['lexer_toks']]
                        )
                        for op in compare_dict['operators']
                    ],
                    [ASTCodec._decode_worker(d) for d in compare_dict['operands']]
                )
            case 'Constant':
                constant_dict = cast(ipc_const.Constant_dict, dict_ast)
                val = ValueCodec.decode(constant_dict['value'])
                source = ASTCodec._decode_worker(constant_dict['source'])
                return iconst.Constant(val, source)
            case _ as unreachable:
                assert_never(unreachable)

        raise RuntimeError('JSON can not recognized as node')
