# Safe Evaluator

Single expression interpreter based on a subset of Python 3.12 for mathematical and logical expressions with safety features. A safer alternative to the eval function.

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
loan_ok = build(
    "score >= 700 and income > 50000 and dti < 0.4",
    {"score": 742, "income": 68000, "dti": 0.32}
)
rate_ok = build_safe(
    "reqs < max_r and burst < max_b",
    '{"reqs": 80, "max_r": 100, "burst": 10, "max_b": 20}'
)
```

DISCLAIMER: Before using this in production, it is recommended to study all safety features and decide whether they are sufficient. See the "Security features" section for more details.

## Features

4 main functions:
- evaluate (main function for evaluating expressions)
- evaluate_safe (more secure version, uses JSON input for variables)
- build (function for precompiling an expression into an AST)
- build_safe (more secure compile function, uses JSON input)

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

You only need to import the required function from /evaluator/literal_parser.

Example:

```python
from evaluator.literal_parser import evaluate
```

The library does not use any external dependencies, so nothing needs to be installed.


## Architecture

The main motivations for this project are educational purposes, but also to create a usable production-ready product with no external dependencies (for both security and educational reasons).

Whole interpreter consists of 5 components

- Lexer
- Parser
- TypeChecker
- ConstantFolder
- Evaluator

Each component is handwritten, no parser generators are used (only regex in a few cases for performance).

---

### Lexer

Takes a string as input and returns a list of lexer tokens (Lexer_tok objects).
Each token stores the lexeme type, value, and position. Only the type is required, the rest is for debugging.

If tokenization fails, a SyntaxError is raised with the position.

---

### Parser

A Packrat / recursive-descent parser that takes lexer tokens and returns an Abstract Syntax Tree (AST).
It is based on PEG grammar rules defined in evaluator/parser_grammer.gram, mimicking a subset of Python grammar.

If parsing fails, a Failure object is returned with error details.

---

### TypeChecker

A static type checker that takes an AST and returns the resulting type based on rules in evaluator/constants.py.

Each type is represented as a set of possible types (UnionType), even for single types.

It can be also used separately, just to evaluate type of expression, if it is necessary. Inside a prebuild pipelines, TypeChecker is only used to check, if type fail is returned. Other values are ignored.

Limitations:

- Cannot check contents inside containers (shallow typing)

If a type error occurs, a TypeFail object is returned with details.

Not strictly required, but adds safety and prevents runtime issues.

---

### ConstantFolder

Optimizes the AST by folding constant expressions into single nodes.

Not required, but improves performance.

---

### Evaluator

The final component that evaluates the AST.

---

## Build-in functions

There are already build 4 functions with that tools to fully evaluate expression.

1. evaluate(expr: string, vars: dict[str, atom_types])

Takes string with expression and python dictionary with variables to evaluate expression

2. evaluate_safe(expr: str, vars: str)

Same as evaluate, but takes string with JSON, that contains variables to evaluate expression

3. build(expr: string, vars: dict[str, atom_types])

Takes string with expression and python dictionary with variables to create Abstract Syntax Tree. AST tree can be evaluated with Evaluator. Great, if you need to calculate same expression with multiple sets of variables. AST can be executed with Evaluator

Example:

```python
from evaluator.literal_parser import build, Evaluator

variables = {"x": 6}
expr = "x + 7"
ast = build(expr, variables)
answer = Evaluator(variables).eval(ast)
```

4. build_safe(expr: str, vars: str)

Same as build, but takes string with JSON, that contains variables


In some cases, it is not necessary to use every component. So feel free to build your own pipelines.


## Optimalizations

Since Python is relatively slow, several optimizations were used:

1. Memoization in the Parser
2. Constant Folding
3. Short-circuit logic
4. Python regex engine for Lexer in few cases
5. General Python performance tricks


## Security features

This interpreter is designed to reduce risks compared to Python’s built-in eval, primarily by restricting the allowed syntax, operations, and data types. It is not a full sandbox and should not be considered a complete security solution.

### Restricted execution model

Only a predefined subset of Python syntax is supported.
No function calls, attribute access, or arbitrary object interaction

This prevents execution of arbitrary Python code (e.g. __import__, file access, or method calls).
However, it does not protect against resource-intensive computations within the allowed subset.

Also, library does not use any external libraries to prevent supply chain attack.

### Whitelisted operations

Only explicitly allowed operators are supported (mentioned previously)

Each operation is mapped to a controlled implementation, preventing unexpected behavior from Python internals.

This reduces the attack surface, but still allows expressions that may be computationally expensive.

### Safe input handling (evaluate_safe, build_safe)

Accepts variables as JSON strings instead of Python objects

This prevents injection of:

- custom objects
- objects with overridden dunder methods
- callable values

However JSON parsing adds overhead. Recomended only if it is necessary or problem is not computationaly expencive.

### Static type checking (TypeChecker)

Performs shallow type checking before evaluation

This prevents certain invalid operations (e.g. adding incompatible types) before execution.

Limitations:

- container contents are not checked

e.g. [1, "a"] is treated simply as list

- does not guarantee absence of runtime errors in all cases

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

### Constant folding

Constant expressions are evaluated during preprocessing.
This improves performance and reduces evaluation overhead.

However:

large constant expressions (e.g. very large powers) can still be expensive during folding itself

### Limitations

This project improves safety compared to eval, but does not provide full protection against all attack vectors.

It does not prevent:

- CPU exhaustion
- e.g. 2 ** 100000000
- memory exhaustion
- large lists or deeply nested structures
- long evaluation time from valid expressions
- logical misuse of expressions
- e.g. always-true conditions
- side-channel or timing attacks

Additionally:

- No isolation from the Python process (no sandboxing)
- No timeout or execution limits in the evaluator
- Type system is not strict enough to guarantee full safety

### Summary

This interpreter is significantly safer than using eval directly due to:

- strict syntax control
- operation whitelisting
- optional safe input handling

However, it should be used with care in production systems, especially when evaluating untrusted input at scale.
