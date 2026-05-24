from evaluator.pipelines import build
from evaluator.tools.other import serialize_ast, json_str_to_dict

import sys
import json

if __name__ == '__main__':
    data = json.loads(sys.stdin.read())
    expr, vvars = data['expr'], json_str_to_dict(data['vvars'])

    ast = build(expr, vvars)
    json_ast = serialize_ast(ast)
    print(json_ast)
    sys.stdout.flush()