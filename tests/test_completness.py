import inspect
import pytest
import evaluator.interpreter.stages as stages
from evaluator.interpreter.diagnostics import DIAGNOSTICS_REGISTER
from evaluator.interpreter.stages import BaseFailure

def test_diagnostics_completness():
    members = inspect.getmembers(stages)
    classes = [
        obj for _, obj in members
        if inspect.isclass(obj) and
        obj.__module__ == stages.__name__
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
