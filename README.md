# Safe Evaluator

Single expression interpreter based on subset of python  3.12 for matematical and logical expressions with safety features. Safer alternative for eval function

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
loan_ok = compile(
    "score >= 700 and income > 50000 and dti < 0.4",
    {"score": 742, "income": 68000, "dti": 0.32}
)
rate_ok = compile_safe(
    "reqs < max_r and burst < max_b",
    '{"reqs": 80, "max_r": 100, "burst": 10, "max_b": 20}'
)
```

DISCLAIMER: Before using in production is recomended to study all safety features and decide, if they are sufficient. More in category "Security features"

## Features

4 main functions:
- evaluate (main function for evalving expressions)
- evaluate_safe (more secure evaluate function, which uses JSON as imput for variables)
- compile (function for precompiling expression to AST)
- compile_safe (more secure compile function, which uses JSON as imput for variables)

and every component is also allowed to be used separately

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

Python evaluation logic is the same as in python

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

Takes string as imput and returns list of Lexer tokens (Lexer_tok object). Token stores Lexem type, lexem and position. Necessary for the functionality is only Lexem type, other two values are for debugging. If lexer fail to tokenize text, it will raise SyntaxError with given position.

---

### Parser

Parkrat/Recursive-Decent parser, that takes list of Lexer tokens and returns Abstract Syntax Tree. Parser is based on PEG grammer rules in evaluator/parser_grammer.gram, which is imitating substet of python grammer. For more detailsm rules are written in grammer file. If order of Lexer tokens can't match any rule, Failure object will be returned with informations about the fail.

---

### TypeChecker

Static type checker, that takes AST tree as input and returns resulting type based on rules defined in evaluator/constants.py. Every type is represented as set of every possible return type (even single type) for easier implementation of UnionTypes and working with them. Currently TypeChecker can't check content in containers. In case of type error, TypeFail object will be returned with failing AST branch and wrong types.

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

3. compile(expr: string, vars: dict[str, atom_types])

Takes string with expression and python dictionary with variables to create Abstract Syntax Tree. AST tree can be evaluated with Evaluator. Creat, if you need to calculate same expression with multiple set of variables

3. compile_safe(expr: str, vars: str)

Same as compile, but takes string with JSON, that contains variables


In some cases, it is not necessary to use every component. So feel free to build your own pipeline.


## Optimalizations

As python itself is slow language, few optimalizations had to be used, to be usable.

1. Memoization of rules in Parser
2. Constant Folding
3. Short-circuit logic
3. Python regex engine for Lexer in few cases

and few python optimalization tricks


## Security features

Main security feature, around which is whole project build is Evaluator as it creates "whilelist" of allowed functions. Also every component is expecting strict rules, so every component adds layer of protection. Parser contains tracker, that counts ammount of rules called in recursion stack and global amount of called rules against DDoS attacks (max values can be redefined in parser). If any of them is reached, exception will be raised. However complex expressions will not be blocked. For example, large repetetive exprssions like deeply nested parentesies will be blocked after reaching one of the limits, however power of large numbers will slow down in Evaluator. TypeChecker also creates another "whitelist" of allowed operations, cause python can have multiple functions in same symbol (for example + can be add or concatenate). In case, when values of variables are comming from outer systems, it is recomended to use evaluate_safe and compile_safe insted of default one. These functions takes JSON in python string to ensure, that values can't be for example malicious functions or objects with redefined dunder methods and translates it safely into python dict. However this translation can slow down evaluation in large ammount of expressions. In case, when JSON is not used, TypeChecker is doing similar security checks, but it does not work perfectly. Last important information is, that parser is heavily using memoization, so in case of DDoS attacks, expression can be evaluated quickly, but memory will be overloaded.

THIS CODEBASE IS NOT 100% SECURITY SOLUTION FOR EVERY TYPE OF ATTACK, ONLY MUCH BETTER ALTERNATE FOR BASIC EVAL FUNCTION