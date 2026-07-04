import json
from typing import cast

from evaluator.types import atom_types

class TypeDictCodec:

    name_to_type: dict[str, type] = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "None": type(None),
        "NoneType": type(None),
        "list": list,
        "tuple": tuple
    }

    @staticmethod
    def encode(type_dict: dict[str, type | None]) -> str:
        """Serialize dictionary with variable names and their types in object"""

        return json.dumps({
            var: type(None).__name__ if typ is None else typ.__name__
            for var, typ in type_dict.items()
        })

    @classmethod
    def decode(cls, json_type_dict: str) -> dict[str, type]:
        """
        Deserialize string in json format with variable names
        and their types in string format
        """

        json_dict =  json.loads(json_type_dict)
        return {
            var: cls.name_to_type[str_type] for var, str_type in json_dict.items()
        }


class VarsDictCodec:

    @staticmethod
    def encode(vars_dict: dict[str, atom_types]) -> str:
        """
        Serialize dictionary with variables into JSON
        and to every tuple variable name adds prefix __tuple__
        """

        noted_vvars_dict = {
            '__tuple__' + key if isinstance(val, tuple) else key: val
            for key, val in vars_dict.items()
        }
        return json.dumps(noted_vvars_dict)

    @staticmethod
    def decode(json_vars_dict: str) -> dict[str, atom_types]:
        """
        Deserialize string in json format to dictionary.
        Every variable, which name starts with prefix '__tuple__'
        will be converted into tuple
        """

        vvars: dict[str, atom_types] = json.loads(json_vars_dict)
        denoted_vvars = {
            (
                key[9:] if key.startswith('__tuple__') else key
            ): (
                tuple(cast(tuple, val)) if key.startswith('__tuple__') else val
            )
            for key, val in vvars.items()
        }
        # ignore comment is here to hold convertion logic,
        # isinstance is not semantically correct
        return denoted_vvars # type:ignore
