from evaluator.literal_parser import Lexer, Parser, TypeChecker, ConstantFolder, Evaluator
from evaluator.constants import atom_types, nodes
from evaluator.tools.other import json_str_to_dict, deserialize_ast, deserialize_value

import json
from platform import system

OS = system()
if OS == 'Windows':
    from evaluator.tools.windows_sandbox import WindowsProcessAPI
elif OS in ('Linux', 'Darwin'):
    from evaluator.tools.unix_sandbox import UnixProcessAPI

def build(expr: str, vars: dict[str, atom_types]) -> nodes:
    """
    Basic compiler, that compiles string into Abstract Syntax Tree,
    that could be interpreted with Evaluator. For more secure variables,
    use compile_safe
    """

    tokens = Lexer(expr).tokenize()
    ast = Parser(tokens).parse()

    if isinstance(ast, Parser.Failure):
        raise RuntimeError(ast)

    typ = TypeChecker(vars).check(ast)

    if isinstance(typ, TypeChecker.TypeFail):
        raise RuntimeError(typ)

    return ConstantFolder().fold(ast)

def build_safe(expr: str, json_vars: str) -> nodes:
    """
    More secure compiler, that use json in string format,
    to evaluate variables. Recomended, if variables are taken from user.
    If you want to add tuple, create list, which key starts with __tuple__.\n
    Example:\n
    ```json
    {"__tuple__my_tuple": [1,2,3]}
    ```
    will be interpreted as
    ```python
    {"my_tuple": (1,2,3)}
    ```
    """

    vars = json_str_to_dict(json_vars)
    return build(expr, vars)

def build_isolated(expr: str, json_vars: str) -> nodes:
    """
    Safest compiler. Works same as build_safe but also runs script
    in separated process with setted resource limits

    LIMITS:
        - memory: 100 MB
        - execution time: 5 s
    
    UNIX ONLY:
        - file descriptors: 10,
        - adress space: 200 MB
    
    WINDOWS ONLY:
        - handles: 481
    """

    data = json.dumps({'expr': expr, 'vvars': json_vars})
    cmd_args = ['python', '-m', 'evaluator.workers.build_safe']

    if OS in ('Linux', 'Darwin'):
        unix_api = UnixProcessAPI #type:ignore
        new_unix_data = unix_api.create_unix_process(cmd_args, data)
        return deserialize_ast(new_unix_data)

    elif OS == 'Windows':
        win_api = WindowsProcessAPI #type:ignore
        new_win_data = win_api.create_windows_process(
            ' '.join(cmd_args),
            data.encode('utf-8')
        )
        decode_data = new_win_data.value.decode('utf-8')
        if isinstance(new_win_data, win_api.Error):
            raise RuntimeError(decode_data)
        elif isinstance(new_win_data, win_api.Output):
            return deserialize_ast(decode_data)
        else:
            raise RuntimeError('Process returned invalid object')
    else:
        raise RuntimeError('During launching sandbox, OS was not recognized')

def evaluate(expr: str, vars: dict[str, atom_types]) -> atom_types:
    """
    Basic interpreter, that have all features and evaluate variables
    from python dictionary. For more secure variables, use evaluate_safe
    """

    folded_ast = build(expr, vars)
    return Evaluator(vars).eval(folded_ast)

def evaluate_safe(expr: str, json_vars: str) -> atom_types:
    """
    More secure interpreter, that use json in string format,
    to evaluate variables. Recomended, if variables are taken from user.
    If you want to add tuple, create list, which key starts with __tuple__.\n
    Example:\n
    ```json
    {"__tuple__my_tuple": [1,2,3]}
    ```
    will be interpreted as
    ```python
    {"my_tuple": (1,2,3)}
    ```
    """

    return evaluate(expr, json_str_to_dict(json_vars))

def evaluate_isolated(expr: str, json_vars: str) -> atom_types:
    """
    Safest evaluator. Works same as evaluate_safe but also runs script
    in separated process with setted resource limits

    LIMITS:
        - memory: 100 MB
        - execution time: 5 s
    
    UNIX ONLY:
        - file descriptors: 10,
        - adress space: 200 MB
    
    WINDOWS ONLY:
        - handles: 481
    """

    data = json.dumps({'expr': expr, 'vvars': json_vars})
    cmd_args = ['python', '-m', 'evaluator.workers.evaluate_safe']

    if OS in ('Linux', 'Darwin'):
        unix_api = UnixProcessAPI #type:ignore
        decode_data = unix_api.create_unix_process(cmd_args, data)
        return deserialize_value(json.loads(decode_data))
    elif OS == 'Windows':
        win_api = WindowsProcessAPI #type:ignore
        new_win_data = win_api.create_windows_process(
            ' '.join(cmd_args),
            data.encode('utf-8')
        )
        decode_data = new_win_data.value.decode('utf-8')
        if isinstance(new_win_data, win_api.Error):
            raise RuntimeError(decode_data)
        elif isinstance(new_win_data, win_api.Output):
            return deserialize_value(json.loads(decode_data))
        else:
            raise RuntimeError('Process returned invalid object')
    else:
        raise RuntimeError('During launching sandbox, OS was not recognized')
