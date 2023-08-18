import json
from typing import List, Type, Any
import numpy as np

from pyads import (
    PLCTYPE_INT,
    PLCTYPE_BOOL,
    PLCTYPE_BYTE,
    PLCTYPE_DINT,
    PLCTYPE_LREAL,
    PLCTYPE_REAL,
    PLCTYPE_SINT,
    PLCTYPE_STRING,
    PLCTYPE_UDINT,
    PLCTYPE_UINT,
    PLCTYPE_USINT,
    PLCTYPE_LINT,
    PLCTYPE_ULINT
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


class RecipeDefinition(BaseModel):
    symbol_path: str
    value: Any


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


def validate_model_definitions(payload, model_class: Type[BaseModel],
                               silent=False,
                               on_error_schema_file_name='schema.json'):
    try:
        return [model_class(**definition) for definition in payload]
    except ValidationError as e:
        if not silent:
            print(e)
            with open(on_error_schema_file_name, 'w') as file:
                json.dump(model_class.model_json_schema(), file, indent=4)
            print(f"Schema file {on_error_schema_file_name} created to help overcoming validation errors.")


def get_plc_array_type(type_as_str: str):
    try:
        type_as_str = 'boolean' if type_as_str == 'bool' else type_as_str
        return PLC_ARRAY_MAP[type_as_str]
    except KeyError:
        raise ValueError(f"Wrong return type detected: {type_as_str}")


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


def convert_arg(arg, type_as_str: str):
    match type_as_str:
        case 'bool':
            return bool(arg)
        case 'byte':
            if len(arg) != 2:
                raise ValueError("Hex string should have exactly 2 characters")

            byte_value = int(arg, 16)
            # Keep only the lowest 8 bits
            return byte_value & 0xFF
        case 'int64':
            return np.int64(arg)
        case 'uint64':
            return np.uint64(arg)
        case 'uint32':
            return np.uint32(arg)
        case 'int32':
            return np.int32(arg)
        case 'int16':
            return np.int16(arg)
        case 'uint16':
            return np.uint16(arg)
        case 'int8':
            return np.int8(arg)
        case 'uint8':
            return np.uint8(arg)
        case 'double':
            return np.real(arg)
        case 'float':
            return np.float(arg)
        case 'char':
            return arg
        case _:
            raise ValueError(f"Wrong return type detected: {type_as_str}")
