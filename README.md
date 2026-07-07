# Safe Evaluator

[![Python application](https://github.com/KrisV123/Safe-Evaluator/actions/workflows/python-app.yml/badge.svg)](https://github.com/KrisV123/Safe-Evaluator/actions/workflows/python-app.yml)

Single expression interpreter based on a subset of Python syntax (Python 3.11+) for mathematical and logical expressions with safety features. A safer alternative to the eval function.

Examples:

```python
promo_ok = evaluate(
    "(total > 150 and points >= 500) or bf",
    {"total": 189.99, "points": 720, "bf": False}
)
row_ok = evaluate_safe(
    "age >= min_age and status == 'active' and last_login < 30",
    '{"age": 29, "min_age": 18, "status": "active", "last_login": 12}'
)
runtime_check = evaluate_isolated(
    "load < max_load and errors == 0",
    '{"load": 0.73, "max_load": 0.9, "errors": 0}'
)
loan_ok = build(
    "score >= 700 and income > 50000 and dti < 0.4",
    {"score": int, "income": int, "dti": float}
)
rate_ok = build_safe(
    "reqs < max_r and burst < max_b",
    '{"reqs": "int", "max_r": "int", "burst": "int", "max_b": "int"}'
)
policy_result = build_isolated(
    "amount >= min_amount and tier == 'pro'",
    '{"amount": "int", "min_amount": "int", "tier": "str"}'
)
```

DISCLAIMER: Before using this in production, it is recommended to study all safety features and decide whether they are sufficient. See the "Security features" section for more details.

## Features

6 main functions:

- `evaluate` (main function for evaluating expressions)
- `evaluate_safe` (more secure version, uses JSON input for variables)
- `evaluate_isolated` (safest evaluating function, that at the top use process-level isolation)
- `build` (function for precompiling an expression into an AST)
- `build_safe` (more secure compile function, uses JSON input)
- `build_isolated` (safest compile function, that at the top use process-level isolation)

Each component can also be used separately.

allowed types:

- int
- float
- str
- bool
- NoneType
- list
- tuple

allowed functions:

- add: +
- sub: -
- multiply: *
- truediv: /
- floordiv: //
- modulo: %
- power: **
- or: or
- and: and
- unary plus: +
- unary minus: -
- not: not
- in: in
- not in: not in
- is: is
- is not: is not
- lower: <
- greater: >
- lower equal: <=
- greater equal: >=
- equal: ==
- not equal: !=

Operators logic is the same as in python

## How to use it

You can install it from pip with

```bash
pip install git+https://github.com/KrisV123/Safe-Evaluator.git
```

or copy the repository. Than you only need to import the required function from /evaluator/pipelines.

Example:

```python
from evaluator import evaluate
```

## Interpreter architecture

The main motivations for this project are educational purposes, but also to create a usable production-ready product with no external dependencies (for both security and also educational reasons).

Whole interpreter consists of 5 components

- Lexer
- Parser
- TypeChecker
- ConstantFolder
- Evaluator

- diagnostic tools

Each component returns it's own Failure object, that catches every possible exception. Each Failure have it's own specific data about error. This makes capturing errors more simple (only one or two Failure objects can occure in each component based on it's purpose except many different exceptions), code can easily adapt in pipeline based on Failure and makes diagnostics simple.

Components are handwritten, no parser generators are used (only regex in a few cases for performance).

---

### Lexer

Takes a string as input and returns a list of lexer tokens (Lexer_tok objects).
Each token stores the lexeme type, value, and position. Only the type is required for evaluation, the rest is for debugging.

If tokenization fails, a Lexer.Failure object is returned with error details.

---

### Parser

A Packrat parser that takes lexer tokens and returns an decorated Abstract Syntax Tree (AST).
Parser is based on PEG grammar rules defined in evaluator/parser_grammer.gram, mimicking a subset of Python grammar.

If parsing fails, a Parser.Failure object is returned with error details.

---

### TypeChecker

A static type checker that takes an dictionary with variable names and their type objects, AST and returns the resulting type based on rules in evaluator/interpreter/tables.py (mimicking type rules in python).

Each type is represented as a set of possible types (UnionType), even for single type.

It can be also used separately, just to evaluate type of expression, if it is necessary. Inside a prebuild pipelines, TypeChecker is only used to check, if Failure is returned and for better error dignostics. Other values are ignored.

Limitations:

- Cannot check contents inside containers (shallow typing)

If a type error occurs, a TypeChecker.Failure object is returned with error details. TypeChecker distinguishes between two error types (TypeFailure and GenericFailure). TypeFailure will be returned, if TypeChecker catches type error and in every other case will be returned as GenericFailure (for example dividing with zero). TypeFailure and GenericFailure inherit from main parent TypeChecker.Failure object, so each of them can be recognized as that object

If user is operating with json-like strings, TypeChecker instance can be created with classmethod

```python
TypeChecker.from_json('{"x": "int"}')
```

and string will be automatically converted to dict in the background.

Not strictly required, but adds safety and prevents runtime issues.

---

### ConstantFolder

Optimizes AST by folding constant expressions into single nodes.

Not required, but improves performance if same AST is evaluated repeatedly.

If runtime error occures, a Failure object is returned with error details.

---

### Evaluator

The final component that takes dictionary with variable names and runtime values, AST and returnes evaluated value.

If runtime error occures, a Evaluator.Failure object will be returned with error details.

If user is also operating with json-like strings, Evaluator instance can be also created with classmethod

```python
Evaluator.from_json('{"x": 5}')
```

and will be automatically converted.

---

### Diagnostic tools

Every component have build it's own diagnosting tool for their specific errors and registered in DIAGNOSTICS_REGISTER table. Every tool analyze error data and returns string with error message.

For creating error message, diagnose function can be used, which works as orchestrator to choose right diagnosting tool.

---

## Sandboxes (process isolation)

Since the project itself does not analyze the cost of an evaluated expression before execution, the library includes a sandbox module that limits resource usage at the OS level by isolating each evaluation in a separate process.

Limits are OS-specific, since each operating system tracks and enforces resources differently. `time_limit` and `memory_limit` are configurable per call (both default to 5s / 100 MB); all other limits below are fixed constants.

**UNIX (Linux + macOS)**

- Wall-clock time: `time_limit` (default 5s)
- CPU execution time: `time_limit` (default 5s)
- Open file descriptors: 10
- Process/thread creation: disabled
- Stack size: 4 MB
- Core dumps: disabled
- Locked memory: disabled

**Linux additionally**

- Virtual memory: `memory_limit` (default 100 MB)
- POSIX message queues: disabled
- Priority increase (niceness): disabled
- Real-time CPU time: disabled
- Pending signals: 32

**Windows**

- CPU (user-mode) execution time: `time_limit` (default 5s) — kernel-enforced via Job Object
- Wall-clock time: `time_limit` (default 5s) — enforced via a polling watchdog thread
- Committed memory: `memory_limit` (default 100 MB)
- Handles: 481 — enforced via a polling watchdog thread, so this limit is approximate rather than kernel-guaranteed
- Job object active processes: 1 — kernel-enforced
- Kill on job close: enabled (all processes in the job are terminated if the job handle is closed, e.g. on crash of the controlling process)

This prevents:

- CPU overload
- RAM overload
- Uncontrolled creation of kernel objects and open files
- Fork bombs
- A crashing subprocess from affecting the main process

However, process isolation introduces significant overhead when spawning processes, and watchdog-based limits (Windows handle count, wall-clock time) are polled rather than instantaneous, so they are not perfectly deterministic. Use this when security is the top priority, not when raw throughput matters.

**macOS-specific limitations**

Resource limiting relies on `setrlimit`, which has known limitations on macOS. `RLIMIT_NPROC` applies per-user rather than per-process, so setting it to 0 may interfere with other processes running under the same user account. Additionally, limits are applied between `fork()` and `exec()` during process spawning — if the parent process is multithreaded, locks held by other threads are not transferred to the child, which can cause deadlocks or crashes. Use on macOS only if you understand these limitations and accept the weaker security guarantees.

**General limits**

- The sandbox is designed to limit resource usage, not as a full substitute for OS-level isolation (some APIs go further, but this is not a general-purpose sandboxing tool).
- Resource tracking via process isolation is non-deterministic and depends on OS state.

### Usage

The module exposes two main APIs, `WindowsProcessAPI` and `UnixProcessAPI`, both inheriting from the abstract class `Sandbox`, which defines the shared interface. Since each API is tied to a specific operating system, and using them directly could cause irrelevant typing errors, the `get_sandbox()` function resolves the correct implementation at runtime and unifies their behavior across systems. The main method, `create_process()`, has the same signature on every API and returns an object wrapping either the real output or an error state. Because implementation and error conditions differ across operating systems, each API can return a different subset of the error types below.

Method signature:

```python
create_process(cls,
               cmd: list[str],
               input: str,
               time_limit: int = 5,
               memory_limit: int = 100) -> Sandbox.Output | Sandbox.Error
```

**Shared return types**

- `Output` — valid output from the subprocess (no error).
- `Error` — generic parent class for all error types below.
- `SubprocessError` — contains the stderr output (e.g. a Python traceback) produced by the worker process.

**Linux and macOS specific**

- `WallKill` — returned if the wall-clock time limit is reached; carries no additional data.
- `KilledProcess` — returned if any other limit is reached; carries the signal number that terminated the process.

Since usage is a bit more involved, a direct use case can be found in the `build_isolated` and `evaluate_isolated` function implementations in `evaluator/pipelines.py`.

## Build-in functions

There are already 6 built-in functions using these tools to fully evaluate expression.

1. `evaluate(expr: str, vars: dict[str, atom_types], max_expr_length:int=80)`

Takes string with expression and python dictionary with variables to evaluate expression. Parameter max_expr_length filter any expression larger than limit (presetted to 80 chars).

2. `evaluate_safe(expr: str, vars: str, max_expr_length:int=80)`

Same as evaluate, but takes string with JSON, that contains variables to evaluate expression.

3. `evaluate_isolated(expr: str, vars: str, max_expr_length:int=80)`

Same as evaluate_safe, but evaluate expression in separate process with limited resources.

4. `build(expr: str, vars: Mapping[str, type], max_expr_length:int=80)`

Takes string with expression and python dictionary with variables and it's coresponding type to create Abstract Syntax Tree. AST tree can be evaluated with Evaluator. Great, if you need to calculate same expression with multiple sets of variables. AST can be executed with Evaluator.

Example:

```python
from evaluator import build
from evaluator import Evaluator

expr = "x + 7"
types = {"x": int}
variables = {"x": 6}

ast = build(expr, types)
answer = Evaluator(variables).eval(ast)
```

Parameter max_expr_length filter any expression larger than limit (presetted to 80 chars).

5. `build_safe(expr: str, vars: str, max_expr_length:int=80)`

Same as build, but takes string with JSON, that contains variables and it's types are in string format

6. `build_isolated(expr: str, vars: str, max_expr_length:int=80)`

Same as build_safe, but build AST in separate process with limited resources.

In some cases, it is not necessary to use every component. So feel free to build your own pipelines.

## Optimalizations

Since Python is relatively slow, several optimizations were used:

1. Memoization in the Parser
2. Constant Folding
3. Short-circuit logic
4. Python regex engine for Lexer in few cases
5. General Python performance tricks

## Testing

Since interpreter instead of raising exceptions returns Fialure objects, it needs do ensured, that interpeter does not have any unreachable states. In testing was used

1. unit tests
2. fuzzer tests
3. completion tests for some dependent components
4. integration tests for whole pipelines

## Security features

This interpreter is designed to reduce risks compared to Python’s built-in eval, primarily by restricting the allowed syntax, operations, and data types. It is not a full sandbox and should not be considered a complete security solution.

### Restricted execution model

Only a predefined subset of Python syntax is supported.
No function calls, attribute access, or arbitrary object interaction

This prevents execution of arbitrary Python code (e.g. __import__, file access, or method calls).
However, it does not protect against resource-intensive computations within the allowed subset.

Also, library does not use any external libraries to prevent supply chain attack.

---

### Whitelisted operations

Only explicitly allowed operators are supported (mentioned previously)

Each operation is mapped to a controlled implementation, preventing unexpected behavior from Python internals.

This reduces the attack surface, but still allows expressions that may be computationally expensive.

---

### Expression length

Accepts only expressions up to a predefined maximum length. Longer expressions are automatically rejected before any processing begins.

This serves as a first-pass filter against obviously malformed or malicious input, but is not sufficient to prevent DoS attacks on its own.

---

### Safe input handling (evaluate_safe, build_safe)

Accepts variables as JSON strings instead of Python objects

This prevents injection of:

- custom objects
- objects with overridden dunder methods
- callable values

However JSON parsing adds overhead. Recommended only when necessary or when the problem is not computationally expensive.

---

### Sandboxing (evaluate_isolated, build_isolated)

Specific functions evaluate themselves in a separate process with limited resources. See "Sandboxes (process isolation)" for more details about limitations.

---

### Static type checking (TypeChecker)

Performs shallow type checking before evaluation

This prevents certain invalid operations (e.g. adding incompatible types) before execution.

Limitations:

- container contents are not checked

e.g. [1, "a"] is treated simply as list

- does not guarantee absence of runtime errors in all cases

---

### Parser limits (basic DoS protection)

- Limits:

  - recursion depth
  - total number of parser rule evaluations

- This helps mitigate:

  - extremely deep or pathological expressions
  - certain algorithmic complexity attacks on the parser

However:

it does not prevent expensive evaluation after parsing
large but valid expressions may still consume significant resources

---

### Constant folding

Constant expressions are evaluated during preprocessing.
This improves performance and reduces evaluation overhead.

However:

large constant expressions (e.g. very large powers) can still be expensive during folding itself

---

### Limitations

This project improves safety compared to eval, but does not provide full protection against all attack vectors.

It does not prevent:

- deterministic and pre-execution resource limiting
- long evaluation time from valid expressions
- logical misuse of expressions
- e.g. always-true conditions
- side-channel or timing attacks
- type system is not strict enough to guarantee full safety

---

### Summary

This interpreter is significantly safer than using eval directly due to:

- strict syntax control
- operation whitelisting
- optional safe input handling
- resource limiting

However, it should be used with care in production systems, especially when evaluating untrusted input at scale.
