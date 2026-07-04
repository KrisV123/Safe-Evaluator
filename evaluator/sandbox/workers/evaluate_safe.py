from evaluator.pipelines import evaluate
from evaluator.protocols.ipc import ValueCodec
from evaluator.protocols.serialization import VarsDictCodec

import sys
import json

if __name__ == '__main__':
    data = json.loads(sys.stdin.read())
    expr, vvars, expr_len = data['expr'], VarsDictCodec.decode(data['vvars']), data['expr_len']

    ans = evaluate(expr, vvars, expr_len)
    s_ans = json.dumps(ValueCodec.encode(ans))
    print(s_ans)
    sys.stdout.flush()
