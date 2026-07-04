import pytest
from evaluator.protocols.serialization import TypeDictCodec, VarsDictCodec
from evaluator.types import atom_types

def test_serialize_and_deserialize_TypeDictCodec() -> None:
    type_dict = {
        "a": str, "b": int, "c": float, "d": bool,
        "e": None, "f": type(None), "g": list, "h": tuple
    }

    serialized = TypeDictCodec.encode(type_dict)
    expect_serialized = '{"a": "str", "b": "int", "c": "float", "d": "bool", "e": "NoneType", "f": "NoneType", "g": "list", "h": "tuple"}'
    assert serialized == expect_serialized

    deserialized = TypeDictCodec.decode(serialized)
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

def test_serialize_and_deserialize_VarsDictCodec() -> None:
    vvars: dict[str, atom_types] = {
        "str": "string", "int": 1, "float": 6.7, "bool": True,
        "none": None, "list": [1,2,3], "tuple": (1,2,3)
    }

    serialized = VarsDictCodec.encode(vvars)
    expect_serialized = '{"str": "string", "int": 1, "float": 6.7, "bool": true, "none": null, "list": [1, 2, 3], "__tuple__tuple": [1, 2, 3]}'
    assert serialized == expect_serialized

    deserialized = VarsDictCodec.decode(serialized)
    assert deserialized == vvars
