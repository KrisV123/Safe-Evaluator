from evaluator.interpreter.stages import Lexer, Parser, TypeChecker, ConstantFolder, Evaluator
from evaluator.types import atom_types, nodes
from evaluator.protocols.ipc import ValueCodec, ASTCodec
from evaluator.protocols.serialization import TypeDictCodec, VarsDictCodec
from evaluator.interpreter.diagnostics import diagnose

import json
from platform import system
from typing import assert_never

from evaluator.sandbox.os_orchester import get_sandbox

OS = system()
SANDBOX = get_sandbox()

def check_expr_len(expr: str, limit: int) -> None:
    """check if expression exceed the limit. If yes, raise the exception"""

    expr_len = len(expr)
    if expr_len > limit:
        raise RuntimeError(
            f"Expression length limit exceeded. Lenght: {expr_len}, Limit: {limit}"
        )

def build(expr: str, types: dict[str, type], max_expr_length:int=80) -> nodes:
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

    check_expr_len(expr, max_expr_length)

    tokens = Lexer(expr).tokenize()

    if isinstance(tokens, Lexer.Failure):
        error_msg = diagnose(expr, tokens)
        raise RuntimeError(error_msg)

    ast = Parser(tokens).parse()

    if isinstance(ast, Parser.Failure):
        error_msg = diagnose(expr, ast)
        raise RuntimeError(error_msg)

    typ = TypeChecker(types).check(ast)

    if isinstance(typ, TypeChecker.Failure):
        error_msg = diagnose(expr, typ)
        raise RuntimeError(error_msg)

    folded_ast = ConstantFolder().fold(ast)

    if isinstance(folded_ast, ConstantFolder.Failure):
        error_msg = diagnose(expr, folded_ast)
        raise RuntimeError(error_msg)

    return folded_ast

def build_safe(expr: str, json_types: str, max_expr_length:int=80) -> nodes:
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

    return build(expr, TypeDictCodec.decode(json_types), max_expr_length)

def build_isolated(expr: str, json_types: str, max_expr_length:int=80) -> nodes:
    """
    Safest compiler. Works same as build_safe but also runs script
    in separated process with setted resource limits

    WINDOWS:
        - adress space (committed): 100 MB
        - CPU execution time: 5s
        - user space execution time: 5s
        - handles: 481
        - job object active processes: 1
        - cleanup on job close: enabled

    LINUX:
        - Wall-clock execution time: 5s
        - CPU execution time: 5s
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

        - CPU execution time: 5s
        - file descriptors: 10
        - processes: process creation disabled
        - stack size: 4 MB
        - core dumps: disabled
        - locked memory: 0 B
    """

    data = json.dumps({'expr': expr, 'types': json_types, 'expr_len': max_expr_length})
    cmd_args = ['python', '-m', 'evaluator.sandbox.workers.build_safe']
    new_data = SANDBOX.create_process(cmd_args, data)

    if OS in ('Linux', 'Darwin'):
        if isinstance(new_data, SANDBOX.Output):
            return ASTCodec.decode(new_data.value)

        elif isinstance(new_data, SANDBOX.Error):
            if isinstance(new_data, SANDBOX.KilledProcess):
                raise RuntimeError(f'Process was killed with signal {new_data.signal}')

            elif isinstance(new_data, SANDBOX.WallKill):
                raise RuntimeError('process was killed by reaching wall-time limit')
            
            elif isinstance(new_data, SANDBOX.SubprocessError):
                raise RuntimeError(new_data.value)

            else:
                raise AttributeError(
                    f'Fail object {repr(new_data)} does not exist as error type'
                )
        else:
            assert_never(new_data)
    
    elif OS == 'Windows':
        if isinstance(new_data, SANDBOX.Output):
            return ASTCodec.decode(new_data.value)
            
        elif isinstance(new_data, SANDBOX.Error):
            if isinstance(new_data, SANDBOX.SubprocessError):
                raise RuntimeError(new_data.value)
            else:
                raise AttributeError(
                    f'Fail object {repr(new_data)} does not exist as error type'
                )

        else:
            assert_never(new_data)
        
    else:
        raise RuntimeError('During launching sandbox, OS was not recognized')

def evaluate(expr: str, vars: dict[str, atom_types], max_expr_length:int=80) -> atom_types:
    """
    Basic interpreter, that have all interpreter stages
    and evaluate variables from python dictionary.

    For more secure variables, use evaluate_safe
    """

    check_expr_len(expr, max_expr_length)

    type_dict = {key: type(val) for key, val in vars.items()}
    folded_ast = build(expr, type_dict)

    ans = Evaluator(vars).eval(folded_ast)

    if isinstance(ans, Evaluator.Failure):
        error_msg = diagnose(expr, ans)
        raise RuntimeError(error_msg)

    return ans

def evaluate_safe(expr: str, json_vars: str, max_expr_length:int=80) -> atom_types:
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

    return evaluate(expr, VarsDictCodec.decode(json_vars), max_expr_length)

def evaluate_isolated(expr: str, json_vars: str, max_expr_length:int=80) -> atom_types:
    """
    Safest evaluator. Works same as evaluate_safe but also runs script
    in separated process with setted resource limits

    WINDOWS:
        - adress space (committed): 100 MB
        - CPU execution time: 5s
        - user space execution time: 5s
        - handles: 481
        - job object active processes: 1
        - cleanup on job close: enabled

    LINUX:
        - Wall-clock execution time: 5s
        - CPU execution time: 5s
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
    """

    data = json.dumps({'expr': expr, 'vvars': json_vars, 'expr_len': max_expr_length})
    cmd_args = ['python', '-m', 'evaluator.sandbox.workers.evaluate_safe']
    new_data = SANDBOX.create_process(cmd_args, data)

    if OS in ('Linux', 'Darwin'):
        if isinstance(new_data, SANDBOX.Output):
            return ValueCodec.decode(json.loads(new_data.value))

        elif isinstance(new_data, SANDBOX.Error):
            if isinstance(new_data, SANDBOX.KilledProcess):
                raise RuntimeError(f'Process was killed with signal {new_data.signal}')

            elif isinstance(new_data, SANDBOX.WallKill):
                raise RuntimeError('process was killed by reaching wall-clock time limit')

            elif isinstance(new_data, SANDBOX.SubprocessError):
                raise RuntimeError(new_data.value)

            else:
                raise AttributeError(
                    f'Fail object {repr(new_data)} does not exist as error type'
                )

        else:
            assert_never(new_data)

    elif OS == 'Windows':
        if isinstance(new_data, SANDBOX.Output):
            return ValueCodec.decode(json.loads(new_data.value))

        elif isinstance(new_data, SANDBOX.Error):
            if isinstance(new_data, SANDBOX.SubprocessError):
                raise RuntimeError(new_data.value)
            else:
                raise AttributeError('assert never')
        else:
            raise AttributeError(
                f'Fail object {repr(new_data)} does not exist as error type'
            )
    else:
        raise RuntimeError('During launching sandbox, OS was not recognized')
