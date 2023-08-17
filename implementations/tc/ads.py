import csv
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Union, Callable

from pyads import Connection
from pyads.constants import ADSIGRP_SYM_VALBYHND
from pydantic import BaseModel

from implementations.tc.data_classes import Paths
from implementations.tc.tc_signals import TCSignal
from implementations.tc.tc_types import get_plc_array_type, get_plc_type, raise_on_required_args, RPCMethod, \
    RPCDefinition, find_rpc_definition, find_rpc_method, check_method_args_list_len, RecipeDefinition, \
    validate_model_definitions, convert_arg
from signals.generic_signals import Signal
from utilities.file import get_json
from utilities.functions import payload_to_dataclass, fill_table


@dataclass
class Symbol:
    name: str
    comment: str
    symbol_type: str
    array_size: int
    auto_update: bool
    index_group: Union[int, str]
    index_offset: Union[int, str]
    value: None

    def __post_init__(self):
        self.index_group = hex(self.index_group)
        self.index_offset = hex(self.index_offset)


def get_ads_symbol(plc: Connection, symbol_str):
    symbol = plc.get_symbol(symbol_str)
    if symbol.plc_type:
        symbol.read()

    return symbol


def print_out_symbol(plc: Connection, symbol_str):
    symbol = get_ads_symbol(plc, symbol_str)
    table_list = payload_to_dataclass([symbol], Symbol)
    table = fill_table(table_list, Symbol)
    print(table)


def print_out_symbols(symbols):
    dataclass_symbols = payload_to_dataclass(symbols, Symbol)
    table = fill_table(dataclass_symbols, Symbol)
    print(table)


def get_symbol_str(signal: Signal) -> str:
    symbol_str = signal.payload[0]
    signal.payload = None
    return symbol_str


def validate_recipe_and_execute_callback(file_path, callback: Callable[[list[BaseModel], dict], None]):
    recipe_definitions_json = get_json(file_path)
    if recipe_definitions_json:
        recipe_definitions = validate_model_definitions(recipe_definitions_json, RecipeDefinition)
        if not recipe_definitions:
            return
        callback(recipe_definitions, recipe_definitions_json)

    else:
        print(f"No recipe definitions found in {file_path}")


def download_recipe(plc: Connection, file_path):
    def callback(recipe_definitions: list[BaseModel], recipe_definitions_json: dict):
        for recipe_definition in recipe_definitions:
            plc.write_by_name(recipe_definition.symbol_path, recipe_definition.value)
        print("Recipe downloaded successfully")

    validate_recipe_and_execute_callback(file_path, callback)


def upload_recipe(plc: Connection, file_path):
    def callback(recipe_definitions: list[BaseModel], recipe_definitions_json: dict):
        for i, recipe_definition in enumerate(recipe_definitions):
            value = plc.read_by_name(recipe_definition.symbol_path)
            recipe_definitions_json[i]['value'] = value

        with open(file_path, 'w') as file:
            json.dump(recipe_definitions_json, file, indent=4)

        print("Recipe uploaded successfully")

    validate_recipe_and_execute_callback(file_path, callback)


def rpc(plc: Connection, symbol, method: RPCMethod, args_datatype=None, args=None):
    handle = plc.get_handle(symbol)
    return_types = method.return_types
    # FB has more than one return value, for example variables defined in the
    # VAR_OUTPUT section
    if len(return_types) > 1:
        array_callable = get_plc_array_type(return_types[0])
        return plc.read_write(ADSIGRP_SYM_VALBYHND,
                              handle,
                              plc_read_datatype=array_callable(len(return_types)),
                              plc_write_datatype=args_datatype,
                              value=args)
    else:

        return_type = None
        if return_types:
            return_type = get_plc_type(return_types[0])
        return plc.read_write(ADSIGRP_SYM_VALBYHND,
                              handle,
                              plc_read_datatype=return_type,
                              plc_write_datatype=args_datatype,
                              value=args)


def signal_to_rpc_call(plc, tc_signal: TCSignal, rpc_definitions: list[RPCDefinition]):
    # The RPC-Method has more than 1 args
    if len(tc_signal.payload) > 3:
        symbol_path, method_name, *args = tc_signal.payload
        symbol = symbol_path + '#' + method_name

        rpc_definition = find_rpc_definition(rpc_definitions, symbol_path)
        method = find_rpc_method(method_name, rpc_definition.methods)

        # Check if len of args is the same as the number of RPC-Method args
        check_method_args_list_len(args, method)
        # Get PLC array type for method args
        array_callable = get_plc_array_type(method.arguments[0].type)
        args_datatype = array_callable(len(args))
        response = rpc(plc, symbol, method, args_datatype, args)
        if response:
            print(response)

    # The RPC-Method has 1 arg
    elif len(tc_signal.payload) == 3:

        symbol_path, method_name, arg = tc_signal.payload
        symbol = symbol_path + '#' + method_name
        rpc_definition = find_rpc_definition(rpc_definitions, symbol_path)
        method = find_rpc_method(method_name, rpc_definition.methods)
        check_method_args_list_len([arg], method)
        type_as_str = method.arguments[0].type
        arg_datatype = get_plc_type(type_as_str)
        value = convert_arg(arg, type_as_str)
        response = rpc(plc, symbol, method, arg_datatype, value)
        if response:
            print(response)

    # The RPC-Method has no arguments
    elif len(tc_signal.payload) == 2:
        symbol_path, method_name = tc_signal.payload
        symbol = symbol_path + '#' + method_name

        # Check if the arguments of the RPC-Method are required if any
        rpc_definition = find_rpc_definition(rpc_definitions, symbol_path)
        method = find_rpc_method(method_name, rpc_definition.methods)
        raise_on_required_args(method)

        response = rpc(plc, symbol, method)
        if response:
            print(response)

    elif len(tc_signal.payload) == 1:
        raise ValueError("RPC method name missing")

    else:
        raise ValueError("Symbol path missing.")


def set_symbol(plc: Connection, symbol_str, value):
    def is_float(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def is_numeric(s):
        s = s.replace("-", "")
        return s.isnumeric()

    if is_numeric(value):
        value = int(value)
    elif is_float(value):
        value = float(value)

    plc.write_by_name(symbol_str, value)


def add_notification(symbol, notification_dict, paths: Paths, callback=None):
    if symbol.name not in notification_dict:
        symbol.auto_update = True
        if not callback:
            def _notification_callback(notification_header, index_tuple):
                timestamp_microseconds = notification_header.contents.nTimeStamp // 10
                # Convert the timestamp to a datetime object
                date_time = datetime(1601, 1, 1) + timedelta(
                    microseconds=timestamp_microseconds)
                formatted_date_time = date_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                if 'STRING' in symbol.symbol_type:
                    symbol_value = notification_dict[symbol.name].value
                    byte_string = b''
                    for byte in symbol_value:
                        if byte == b'\x00':
                            break
                        byte_string += byte
                    payload = byte_string.decode('utf-8')
                else:
                    payload = notification_dict[symbol.name].value

                csv_output = [formatted_date_time, symbol.name, payload]
                with open(paths.ads_notifications_file_path, 'a', newline='') as notification_file:
                    writer = csv.writer(notification_file)
                    writer.writerow(csv_output)

            callback = _notification_callback

        return_val = symbol.add_device_notification(callback)
        notification_dict[symbol.name] = symbol
        print(f"Notification callback for symbol {symbol.name} setup successfully {return_val}")
