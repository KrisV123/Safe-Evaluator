from evaluator.pipelines import build
from evaluator.tools.other import serialize_ast, deserialize_type_dict

import sys
import json

if __name__ == '__main__':
    data = json.loads(sys.stdin.read())
    expr, types = data['expr'], deserialize_type_dict(data['types'])

    ast = build(expr, types)
    json_ast = serialize_ast(ast)
    print(json_ast)
    sys.stdout.flush()