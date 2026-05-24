from evaluator.pipelines import evaluate
from evaluator.tools.other import json_str_to_dict

import sys
import json

if __name__ == '__main__':
    data = json.loads(sys.stdin.read())
    expr, vvars = data['expr'], json_str_to_dict(data['vvars'])

    ans = evaluate(expr, vvars)
    print(ans)
    sys.stdout.flush()