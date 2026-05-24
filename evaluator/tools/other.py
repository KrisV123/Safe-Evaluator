from evaluator.constants import (
    nodes, Value, UnaryOp, BinaryOp, Constant, CompareNode, Collection, Parser_tok
)

import json

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

def serialize_ast(ast: nodes) -> str:
    """Serialize AST into string in JSON format"""

    return json.dumps(_serialize_ast_worker(ast))

def _serialize_ast_worker(node: nodes) -> dict:
    if isinstance(node, Value):
        return {'name': 'Value', 'token': node.token, 'value': node.value}
    elif isinstance(node, UnaryOp):
        return {
            'name': 'UnaryOp',
            'token': node.token,
            'child': _serialize_ast_worker(node.child)
        }
    elif isinstance(node, BinaryOp):
        return {
            'name': 'BinaryOp',
            'token': node.token,
            'left_child': _serialize_ast_worker(node.left_child),
            'right_child': _serialize_ast_worker(node.right_child)
        }
    elif isinstance(node, Collection):
        if node.typ is list:
            typ = 'list'
        elif node.typ is tuple:
            typ = 'tuple'
        else:
            raise TypeError('Type of collection is not recognized')

        return {
            'name': 'Collection',
            'type': typ,
            'collection': [_serialize_ast_worker(n) for n in node.collection]
        }
    elif isinstance(node, CompareNode):
        return {
            'name': 'CompareNode',
            'operators': node.operators,
            'operands': [_serialize_ast_worker(n) for n in node.operands]
        }
    elif isinstance(node, Constant):
        return {
            'name': 'Constant',
            'value': node.value
        }
    
    raise RuntimeError('Node in AST during serialization was not recognized')

def deserialize_ast(json_ast: str) -> nodes:
    """Deserialize string in JSON format into AST python data structure"""

    dict_ast = json.loads(json_ast)
    ast = _deserialize_ast_worker(dict_ast)
    return ast

def _deserialize_ast_worker(dict_ast: dict) -> nodes:
    match dict_ast['name']:
        case 'Value':
            node = Value(Parser_tok(dict_ast['token']), dict_ast['value'])
            return node
        case 'UnaryOp':
            return UnaryOp(
                Parser_tok(dict_ast['token']),
                _deserialize_ast_worker(dict_ast['child'])
            )
        case 'BinaryOp':
            return BinaryOp(
                Parser_tok(dict_ast['token']),
                _deserialize_ast_worker(dict_ast['left_child']),
                _deserialize_ast_worker(dict_ast['right_child'])
            )
        case 'Collection':
            typ: type[list | tuple]
            json_type = dict_ast['type']

            if json_type == 'list':
                typ = list
            elif json_type == 'tuple':
                typ = tuple
            else:
                raise TypeError('Type of collection is not recognized')

            return Collection(
                typ,
                [_deserialize_ast_worker(d) for d in dict_ast['collection']]
            )
        case 'CompareNode':
            return CompareNode(
                [Parser_tok(d) for d in dict_ast['operators']],
                [_deserialize_ast_worker(d) for d in dict_ast['operands']]
            )
        case 'Constant':
            return Constant(
                dict_ast['value']
            )

    raise RuntimeError('JSON can not recognized as node')
