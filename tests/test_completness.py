import inspect
import pytest
import evaluator.interpreter.stages as stages
from evaluator.interpreter.diagnostics import DIAGNOSTICS_REGISTER
from evaluator.interpreter.stages.base import BaseFailure

def test_diagnostics_completness():
    members = inspect.getmembers(stages)
    stage_modules = [
        module for name, module in members if not name.startswith('__')
    ]

    classes = [
        obj
        for module in stage_modules
        for _, obj in inspect.getmembers(module)
        if inspect.isclass(obj)
        if obj.__module__ == module.__name__
    ]

    failures = [
        obj
        for stage in classes
        for _, obj in inspect.getmembers(stage)
        if inspect.isclass(obj)
        if issubclass(obj, BaseFailure)
        if obj.__module__ == stage.__module__
    ]

    assert set(DIAGNOSTICS_REGISTER) == set(failures)
