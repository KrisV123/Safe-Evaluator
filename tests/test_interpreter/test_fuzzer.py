import pytest
import random
import string as s

from evaluator.interpreter.stages import (
    Lexer, Parser, TypeChecker, ConstantFolder, Evaluator
)
from evaluator.types import Lexer_tok, Lexer_type
from tests.test_interpreter.utils import Random_ast, create_all_lexer_toks, log_error_from_fuzzer

def test_Lexer_fuzzing_all_chars():
    chars = s.ascii_letters + s.digits + s.punctuation + s.whitespace
    for _ in range(100_000):
        random_imput = ''.join(random.choices(chars, k = 20))
        try:
            Lexer(random_imput).tokenize()
        except Exception as e:
            log_error_from_fuzzer('test_Lexer_fuzzing', random_imput, e)
            assert False

def test_lexer_fuzzing_usable_chars():
    keywords = '+-*/=!"\'()[],'
    chars = s.ascii_letters + s.digits + s.whitespace + keywords
    for _ in range(100_000):
        random_imput = ''.join(random.choices(chars, k = 20))
        try:
            Lexer(random_imput).tokenize()
        except Exception as e:
            log_error_from_fuzzer('test_Lexer_fuzzing', random_imput, e)
            assert False

def test_Parser_fuzzing():
    all_lexer_toks = create_all_lexer_toks()
    for _ in range(100_000):
        tokens_list = random.choices(all_lexer_toks, k=10)
        tokens_list.append(Lexer_tok(Lexer_type.EOF, '$', 0))
        try:
            Parser(tokens_list).parse()
        except Exception as e:
            log_error_from_fuzzer('test_Parser_fuzzing', tokens_list, e)
            assert False

def test_TypeChecker_fuzzing():
    for _ in range(100_000):
        ast = Random_ast(4).generate_rand_ast()
        try:
            TypeChecker({}).check(ast)
        except Exception as e:
            log_error_from_fuzzer('test_TypeChecker_fuzzing', ast, e)
            assert False

def test_ConstantFolder_fuzzing():
    for _ in range(100_000):
        ast = Random_ast(4).generate_rand_ast()
        try:
            ConstantFolder().fold(ast)
        except Exception as e:
            log_error_from_fuzzer('test_ConstantFolder_fuzzing', ast, e)
            assert False

def test_Evaluator_fuzzing():
    for _ in range(100_000):
        ast = Random_ast(4).generate_rand_ast()
        try:
            Evaluator({}).eval(ast)
        except Exception as e:
            log_error_from_fuzzer('test_Evaluator_fuzzing', ast, e)
            assert False
