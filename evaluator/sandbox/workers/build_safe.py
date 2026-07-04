from evaluator.pipelines import build
from evaluator.protocols.ipc import ASTCodec
from evaluator.protocols.serialization import TypeDictCodec

import sys
import json

if __name__ == '__main__':
    data = json.loads(sys.stdin.read())
    expr, types, expr_len = data['expr'], TypeDictCodec.decode(data['types']), data['expr_len']

    ast = build(expr, types, expr_len)
    json_ast = ASTCodec.encode(ast)
    print(json_ast)
    sys.stdout.flush()