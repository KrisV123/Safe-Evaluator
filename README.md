# Safe Evaluator

Single expression interpreter based on subset of python 3.12 for matematical and logical expressions with safety features. Safer alternative for eval function

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

DISCLAIMER: Before using in production is recomended to study all safety features and decide, if they are sufficient. More in category "Security features"

## Features

4 main functions:
- evaluate (main function for evalving expressions)
- evaluate_safe (more secure evaluate function, which uses JSON as input for variables)
- build (function for precompiling expression to AST)
- build_safe (more secure compile function, which uses JSON as input for variables)

and every component can also be used separately

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

You only need to import requested function from /evaluator/literal_parser

Example:

```python
from evaluator.literal_parser import evaluate
```

Library does not use any external libraries, so anything has to be installed additionaly


## Architecture

Main motivations for that project are educational purposes but also usable product in production and no external dependencies (for security and also educational purposes). 

Whole interpreter consists of 5 components

- Lexer
- Parser
- TypeChecker
- ConstantFolder
- Evaluator

Each component is hand-written and any engine was used to generate them (only regex in few cases for increasing performance)

---

### Lexer

Takes string as imput and returns list of Lexer tokens (Lexer_tok object). Token stores Lexeme type, lexeme and position. Necessary for the functionality is only Lexeme type, other two values are for debugging. If lexer fail to tokenize text, it will raise SyntaxError with given position.

---

### Parser

Packrat/Recursive-Decent parser, that takes list of Lexer tokens and returns Abstract Syntax Tree. Parser is based on PEG grammer rules in evaluator/parser_grammer.gram, which is imitating substet of python grammer. For more detailsm rules are written in grammer file. If order of Lexer tokens can't match any rule, Failure object will be returned with informations about the fail.

---

### TypeChecker

Static type checker, that takes AST tree as input and returns resulting type based on rules defined in evaluator/constants.py. Every type is represented as set of every possible return type (UnionType), even single type for easier implementation of UnionTypes and working with them. Currently TypeChecker can't check content in containers (shallow typing). In case of type error, TypeFail object will be returned with failing AST branch and wrong types.

It can be also used separately, just to evaluate type of expression, if it is necessary. Inside a prebuild pipelines, TypeChecker is only used to check, if type fail is returned. Other values are ignored.

TypeChecker is not necessary for working interpreter, however it adds layer of security and prevents theoretical bugs in production (like expression rasie type error on tuple in database, bud previous tuples are already modified. TypeChecker stops that before happening)

---

### ConstantFolder

Folds branches that have constant values in Constant node. Again, this is not necessary for fully functional interpreter but can increase performance.

---

### Evaluator

Last component in pipeline, that evaluate AST tree.

---

There are already build 4 functions with that tools to fully evaluate expression.

1. evaluate(expr: string, vars: dict[str, atom_types])

Takes string with expression and python dictionary with variables to evaluate expression

2. evaluate_safe(expr: str, vars: str)

Same as evaluate, but takes string with JSON, that contains variables to evaluate expression

3. build(expr: string, vars: dict[str, atom_types])

Takes string with expression and python dictionary with variables to create Abstract Syntax Tree. AST tree can be evaluated with Evaluator. Creat, if you need to calculate same expression with multiple set of variables. AST can be executed with Evaluator

EXAMPLE:

```python
from evaluator.literal_parser import build, Evaluator

variables = {"x": 6}
expr = "x + 7"
ast = build(expr, variables)
answer = Evaluator(variables).eval(ast)
```

3. build_safe(expr: str, vars: str)

Same as build, but takes string with JSON, that contains variables


In some cases, it is not necessary to use every component. So feel free to build your own pipeline.


## Optimalizations

As python itself is slow language, few optimalizations had to be used, to be usable.

1. Memoization of rules in Parser
2. Constant Folding
3. Short-circuit logic
3. Python regex engine for Lexer in few cases

and few python optimalization tricks


## Security features

This interpreter is designed to reduce risks compared to Python’s built-in eval, primarily by restricting the allowed syntax, operations, and data types. It is not a full sandbox and should not be considered a complete security solution.

### Restricted execution model

Only a predefined subset of Python syntax is supported
No function calls, attribute access, or arbitrary object interaction

This prevents execution of arbitrary Python code (e.g. __import__, file access, or method calls).
However, it does not protect against resource-intensive computations within the allowed subset.

### Whitelisted operations

Only explicitly allowed operators are supported (mentioned previously)

Each operation is mapped to a controlled implementation, preventing unexpected behavior from Python internals.

This reduces the attack surface, but still allows expressions that may be computationally expensive.

### Safe input handling (evaluate_safe, compile_safe)

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
