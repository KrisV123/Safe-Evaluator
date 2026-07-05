import re
from dataclasses import dataclass

from evaluator.types import Lexer_type, Lexer_tok
from evaluator.interpreter.stages.base import BaseFailure

class Lexer:
    """
    Component, that takes subclass of python code in string object
    and transforms it into list of lexer tokens with lexem type,
    lexem and position
    """

    __slots__ = ['_frozen', 'string']

    def __init__(self, string: str):
        object.__setattr__(self, '_frozen', False)
        self.string = string
        object.__setattr__(self, '_frozen', True)

    def __setattr__(self, name: str, value: object) -> None:
        if not getattr(self, '_frozen'):
            object.__setattr__(self, name, value)
        else:
            raise AttributeError('Object is immutable')

    keyword_op = {
        'or': Lexer_type.OR,
        'and': Lexer_type.AND,
        'in': Lexer_type.IN,
        'not': Lexer_type.NOT,
        'is': Lexer_type.IS
    }

    IDENT_RE = re.compile(r'[a-zA-Z_][0-9a-zA-Z_]*')
    INT_RE = re.compile(r'[0-9]*')
    FLOAT_RE = re.compile(r'[0-9]*\.[0-9]+')
    STRING_RE = re.compile(r'(\'[^\']*\')|("[^"]*")')

    @dataclass(slots=True, frozen=True)
    class Failure(BaseFailure):
        pos: int
        end_pos: int


    def tokenize(self) -> list[Lexer_tok] | Failure:
        tok_stack: list[Lexer_tok] = []
        tok: Lexer_tok | None = None
        i = 0
        while i < len(self.string):
            match self.string[i]:
                case ' ' | '\t' | '\r' | '\n':
                    pass
                case '=':
                    if i + 1 < len(self.string) and self.string[i + 1] == '=':
                        tok = Lexer_tok(Lexer_type.EQ, '==', i)
                        i += 1
                    else:
                        return self.Failure(i, i + 1)
                case '!':
                    if i + 1 < len(self.string) and self.string[i + 1] == '=':
                        tok = Lexer_tok(Lexer_type.NE, '!=', i)
                        i += 1
                    else:
                        return self.Failure(i, i + 1)
                case '<':
                    if i + 1 < len(self.string) and self.string[i + 1] == '=':
                        tok = Lexer_tok(Lexer_type.LE, '<=', i)
                        i += 1
                    else:
                        tok = Lexer_tok(Lexer_type.LT, '<', i)
                case '>':
                    if i + 1 < len(self.string) and self.string[i + 1] == '=':
                        tok = Lexer_tok(Lexer_type.GE, '>=', i)
                        i += 1
                    else:
                        tok = Lexer_tok(Lexer_type.GT, '>', i)
                case '+':
                    tok = Lexer_tok(Lexer_type.PLUS, '+', i)
                case '-':
                    tok = Lexer_tok(Lexer_type.MINUS, '-', i)
                case '*':
                    if i + 1 < len(self.string) and self.string[i + 1] == '*':
                        tok = Lexer_tok(Lexer_type.DSTAR, '**', i)
                        i += 1
                    else:
                        tok = Lexer_tok(Lexer_type.STAR, '*', i)
                case '/':
                    if i + 1 < len(self.string) and self.string[i + 1] == '/':
                        tok = Lexer_tok(Lexer_type.DSLASH, '//', i)
                        i += 1
                    else:
                        tok = Lexer_tok(Lexer_type.SLASH, '/', i)
                case '%':
                    tok = Lexer_tok(Lexer_type.PERCENT, '%', i)
                case "'" | '"':
                    str_lexem = re.match(self.STRING_RE, self.string[i:])
                    if str_lexem:
                        strr = str_lexem.group()
                        tok = Lexer_tok(Lexer_type.STR, strr, i)
                        i += len(strr) - 1
                    else:
                        return self.Failure(i, len(self.string))
                case x if x.isdigit() or x == '.':
                    num_lexem, new_i, typ = self.find_num(i)
                    if num_lexem:
                        check = self.check_leading_zero(num_lexem, i)
                        if isinstance(check, self.Failure):
                            return check
                        tok = Lexer_tok(
                            Lexer_type.INT if typ is int else Lexer_type.FLOAT,
                            num_lexem, i
                        )
                    else:
                        return self.Failure(i, i + 1)
                    i = new_i
                case '(':
                    tok = Lexer_tok(Lexer_type.LPAR, '(', i)
                case ')':
                    tok = Lexer_tok(Lexer_type.RPAR, ')', i)
                case '[':
                    tok = Lexer_tok(Lexer_type.LSQB, '[', i)
                case ']':
                    tok = Lexer_tok(Lexer_type.RSQB, ']', i)
                case ',':
                    tok = Lexer_tok(Lexer_type.COMMA, ',', i)
                case _:
                    match, new_i = self.find_longest_match(i)
                    if match in ('True', 'False'):
                        tok = Lexer_tok(Lexer_type.BOOL, match, i)
                    elif match == 'None':
                        tok = Lexer_tok(Lexer_type.NONE, match, i)
                    else:
                        if match in self.keyword_op.keys():
                            assert isinstance(match, str)
                            tok = Lexer_tok(self.keyword_op[match], match, i)
                        elif match is not None:
                            tok = Lexer_tok(Lexer_type.IDENT, match, i)
                        else:
                            return self.Failure(i, i)
                    i = new_i

            if tok:
                tok_stack.append(tok)
                tok = None
            i += 1

        tok_stack.append(Lexer_tok(Lexer_type.EOF, '$', i))
        return tok_stack

    def find_longest_match(self, pnt: int) -> tuple[str | None, int]:
        keyword = re.match(self.IDENT_RE, self.string[pnt:])
        if keyword:
            new_keyword = keyword.group()
            return new_keyword, pnt + len(new_keyword) - 1
        else:
            return None, 0

    def find_num(self, pnt: int) -> tuple[str | None, int, type]:
        typ: type[object] = object
        str_num = re.match(self.FLOAT_RE, self.string[pnt:])
        typ = float
        if str_num is None:
            str_num = re.match(self.INT_RE, self.string[pnt:])
            typ = int
        if str_num:
            num = str_num.group()
            return num, pnt + len(num) - 1, typ
        else:
            return None, 0, object
    
    def check_leading_zero(self, num: str, pos: int) -> Failure | None:
        if len(num) > 1 and num[0] == '0' and num[1] != '.':
            return self.Failure(pos, pos + len(num))
        return None
