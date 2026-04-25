# Safe Evaluator

Single expression interpreter based on subset of python for matematical and logical expressions with safety features. Safer alternative for eval function

DISCLAIMER: Before using, it is recomended to study all safety features and decide, if they are sufficient

Examples:

```python
promo_ok = evaluate(
    "(total > 150 and points >= 500) or bf",
    {"total": 189.99, "points": 720, "bf": False}
)
row_ok = evaluate_safe(
    "age >= min_age and status == 'active' and last_login < 30",
    {"age": 29, "min_age": 18, "status": "active", "last_login": 12}
)
loan_ok = compile(
    "score >= 700 and income > 50000 and dti < 0.4",
    {"score": 742, "income": 68000, "dti": 0.32}
)
rate_ok = compile_safe(
    "reqs < max_r and burst < max_b",
    {"reqs": 80, "max_r": 100, "burst": 10, "max_b": 20}
)
```

## Features

4 main functions:
- evaluate (main function for evalving expressions)
- evaluate_safe (more secure evaluate function, which uses json as imput for variables)
- compile (function for precompiling expression to AST)
- compile_safe (more secure compile function, which uses json as imput for variables)

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

- add,
- sub,
- multiply,
- truediv,
- floordiv,
- modulo,
- power,
- or,
- and,
- unary plus,
- unary minus,
- not
- in,
- not in,
- is
- is not
- lower,
- greater,
- lower equal,
- greater equal,
- equal,
- not equal,

## Architecture

Main motivation for that project are educational purposes but still usable product in production and no dependencies on external dependencies (for security and also educational purposes). 

Whole interpreter consists of 5 tools

- Lexer
- Parser
- TypeChecker
- ConstantFolder
- Evaluator

Each component is hand-written and any engine was used to generate them (only regex in few cases)

### Lexer

Takes string as imput and returns list of Lexer tokens. Token stores Lexem type, lexem and position. Necessary for the functionality is only Lexem type, other two values are for debugging. Recognized lexems are

OR: or
AND: and
NOT: not
IN: in
IS: is
EQ: ==
NE !=
GT: >
LT: <
GE: >=
LE: <=
PLUS: +
MINUS: -
STAR: *
DSTAR: **
SLASH: /
DSLASH: //
PERCENT: %
STR: python string (can also be written with single or double quotes)
INT: python integer
FLOAT: python float
BOOL: python bool (True, False)
IDENT: python identificator (
    also with similar python rules
    1. allowed characters [a-z, A-Z, 0-9, _]
    2. can't start with numbers
)
NONE: None
LSQB: [
RSQB: ]
LPAR: (
RPAR: )
COMMA: ;
EOF: $ (internal character that will be added at the end of every lexem list)

Skipped are characters '\t', '\r', 'n' and empty spaces, if they are not necessary to the syntax. For indentifiers, integers, floats and strings is used python regegex module for better performance in hot loopes

### Parser

...