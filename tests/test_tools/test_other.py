import pytest

from evaluator.tools.other import serialize_type_dict, deserialize_type_dict

def test_serialize_and_deserialize_type_dict() -> None:
    type_dict = {
        "a": str, "b": int, "c": float, "d": bool,
        "e": None, "f": type(None), "g": list, "h": tuple
    }

    serialized = serialize_type_dict(type_dict)
    expect_serialized = '{"a": "str", "b": "int", "c": "float", "d": "bool", "e": "NoneType", "f": "NoneType", "g": "list", "h": "tuple"}'
    assert serialized == expect_serialized

    deserialized = deserialize_type_dict(serialized)
    expect_deserialized = {
        'a': str,
        'b': int,
        'c': float,
        'd': bool,
        'e': type(None),
        'f': type(None),
        'g': list,
        'h': tuple
    }
    assert deserialized == expect_deserialized
