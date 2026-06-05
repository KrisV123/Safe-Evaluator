from evaluator.interpreter.stages import Lexer, Parser, TypeChecker, ConstantFolder, Evaluator
from evaluator.interpreter.constants import atom_types, nodes
from evaluator.tools.other import (
    json_str_to_dict, deserialize_ast, deserialize_value, deserialize_type_dict
)

import json
from platform import system
from collections.abc import Mapping

OS = system()
if OS == 'Windows':
    from evaluator.tools.windows_sandbox import WindowsProcessAPI
elif OS in ('Linux', 'Darwin'):
    from evaluator.tools.unix_sandbox import UnixProcessAPI

def build(expr: str, types: Mapping[str, type]) -> nodes:
    """
    Basic compiler, that compiles string into Abstract Syntax Tree,
    that could be interpreted with Evaluator.

    Parameter types accept dictionary, where key
    is variable name in string and value is its type.\n
    Example:
    ```python
    {"my_tuple": tuple}
    {"my_int": int, "my_float": float, "none_value": None, "none_value": None}
    ```

    For more secure variables, use build_safe
    """

    tokens = Lexer(expr).tokenize()
    ast = Parser(tokens).parse()

    if isinstance(ast, Parser.Failure):
        raise RuntimeError(ast)

    typ = TypeChecker(types).check(ast)

    if isinstance(typ, TypeChecker.TypeFail):
        raise RuntimeError(typ)

    return ConstantFolder().fold(ast)

def build_safe(expr: str, json_types: str) -> nodes:
    """
    More secure compiler, that use json in string format,
    to evaluate variables. Recomended, if variables are taken from user.

    Parameter json_types accept string in json format, where key
    is variable name in string and value is its type in string.\n
    Example:
    ```python
    '{"my_tuple": "tuple"}'
    '{"my_int": "int", "my_float": "float", "none_value": "None"}'
    ```

    For more secure version, use build_isolated
    """

    return build(expr, deserialize_type_dict(json_types))

def build_isolated(expr: str, json_types: str) -> nodes:
    """
    Safest compiler. Works same as build_safe but also runs script
    in separated process with setted resource limits

    WINDOWS:
        - memory: 100 MB
        - execution time: 5s
        - handles: 481
    
    LINUX:
        - memory: 100 MB
        - execution time: 5s
        - file descriptors: 10
        - adress space: 200 MB
    
    MacOS:
        WARNING:

        Resource limiting has known issues. Memory limits are
        not enforced by the OS and other limits may behave unexpectedly,
        especially in multithreaded programs. See documentation for details

        - execution time: 5s
        - file descriptors: 10
        - adress space: 200 MB
    
    these are main limits. Others are listed in documentation
    """

    data = json.dumps({'expr': expr, 'types': json_types})
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

def evaluate(expr: str, vars: Mapping[str, atom_types]) -> atom_types:
    """
    Basic interpreter, that have all interpreter stages
    and evaluate variables from python dictionary.

    For more secure variables, use evaluate_safe
    """

    type_dict = {key: type(val) for key, val in vars.items()}
    folded_ast = build(expr, type_dict)
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

    For more secure version, use evaluate_isolated
    """

    return evaluate(expr, json_str_to_dict(json_vars))

def evaluate_isolated(expr: str, json_vars: str) -> atom_types:
    """
    Safest evaluator. Works same as evaluate_safe but also runs script
    in separated process with setted resource limits

    WINDOWS:
        - adress space (committed): 100 MB
        - execution time: 5s
        - handles: 481

    LINUX:
        - execution time: 5s
        - file descriptors: 10
        - adress space: 100 MB
        - processes/threads: creation disabled
        - stack size: 4 MB
        - core dumps: disabled
        - locked memory: 0 B
        - POSIX message queues: disabled
        - priority increase: disabled
        - real-time CPU time: disabled
        - pending signals: 32
    
    MacOS:
        WARNING:

        Resource limiting has known issues. Memory limits are
        not enforced by the OS and other limits may behave unexpectedly,
        especially in multithreaded programs. See documentation for details

        - execution time: 5s
        - file descriptors: 10
        - processes: process creation disabled
        - stack size: 4 MB
        - core dumps: disabled
        - locked memory: 0 B

    these are main limits. Others are listed in documentation
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
