import json
from typing import List

from pyads import (
    PLCTYPE_INT,
    PLCTYPE_BOOL,
    PLCTYPE_BYTE,
    PLCTYPE_DINT,
    PLCTYPE_LREAL,
    PLCTYPE_REAL,
    PLCTYPE_SINT,
    PLCTYPE_STRING,
    PLCTYPE_UDINT, PLCTYPE_UINT, PLCTYPE_USINT, PLCTYPE_LINT, PLCTYPE_ULINT
)
from pyads.constants import PLC_ARRAY_MAP

from pydantic import BaseModel, ValidationError


class Argument(BaseModel):
    type: str
    required: bool


class RPCMethod(BaseModel):
    name: str
    arguments: List[Argument]
    return_types: List[str]


class RPCDefinition(BaseModel):
    symbol_path: str
    methods: List[RPCMethod]


def raise_on_required_args(method: RPCMethod):
    arguments = method.arguments
    if arguments:
        for argument in arguments:
            if argument.required:
                raise ValueError(f"Required argument type {argument.type}")


def check_method_args_list_len(args: list, method: RPCMethod):
    if len(method.arguments) != len(args):
        raise ValueError(f'Missing argument values.\n'
                         f'Available method arguments: {method.arguments}\n'
                         f'Provided arguments {args}')


def find_rpc_definition(rpc_definitions: list[RPCDefinition], symbol_path: str) -> RPCDefinition:
    for rpc_definition in rpc_definitions:
        if rpc_definition.symbol_path == symbol_path:
            return rpc_definition
    raise ValueError(f"Symbol {symbol_path} not found in rpc definitions")


def find_rpc_method(method_name: str, methods: list[RPCMethod]) -> RPCMethod:
    for method in methods:
        if method.name == method_name:
            return method
    raise ValueError(f'Method {method_name} not found in rpc methods')


def validate_rpc_definitions(payload, silent=False):
    try:
        return [RPCDefinition(**rpc_definition) for rpc_definition in payload]
    except ValidationError as e:
        if not silent:
            print(e)
            schema_file_name = "rpc_definitions_schema.json"
            with open(schema_file_name, 'w') as file:
                json.dump(RPCDefinition.model_json_schema(), file, indent=4)
            print(f"Schema file {schema_file_name} created to help in the creation of the rpc definition file.")


def get_plc_array_type(type_as_str: str):
    try:
        return PLC_ARRAY_MAP[type_as_str]
    except KeyError:
        raise ValueError(f"Wrong return type detected: {type_as_str}")


# PLCTYPE_BOOL = c_bool
# PLCTYPE_BYTE = c_ubyte
# PLCTYPE_DWORD = c_uint32
# PLCTYPE_DINT = c_int32
# PLCTYPE_INT = c_int16
# PLCTYPE_LREAL = c_double
# PLCTYPE_REAL = c_float
# PLCTYPE_SINT = c_int8
# PLCTYPE_STRING = c_char
# PLCTYPE_TOD = c_int32
# PLCTYPE_UBYTE = c_ubyte
# PLCTYPE_UDINT = c_uint32
# PLCTYPE_UINT = c_uint16
# PLCTYPE_USINT = c_uint8
# PLCTYPE_WORD = c_uint16
# PLCTYPE_LINT = c_int64
# PLCTYPE_ULINT = c_uint64
def get_plc_type(type_as_str: str):
    match type_as_str:
        case 'bool':
            return PLCTYPE_BOOL
        case 'byte':
            return PLCTYPE_BYTE
        case 'int64':
            return PLCTYPE_LINT
        case 'uint64':
            return PLCTYPE_ULINT
        case 'uint32':
            return PLCTYPE_UDINT
        case 'int32':
            return PLCTYPE_DINT
        case 'int16':
            return PLCTYPE_INT
        case 'uint16':
            return PLCTYPE_UINT
        case 'int8':
            return PLCTYPE_SINT
        case 'uint8':
            return PLCTYPE_USINT
        case 'double':
            return PLCTYPE_LREAL
        case 'float':
            return PLCTYPE_REAL
        case 'char':
            return PLCTYPE_STRING
        case _:
            raise ValueError(f"Wrong return type detected: {type_as_str}")
