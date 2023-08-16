from typing import Callable, Any

from implementations.tc.data_classes import Paths
from implementations.tc.tc_types import RPCDefinition, validate_rpc_definitions
from utilities.file import get_list_from_file, get_json


def symbol_hint_callback(paths: Paths) -> Callable[[], dict[Any, None]]:
    def symbol_hint():
        hints = get_list_from_file(paths.symbol_hints_file_path)
        if hints:
            return dict([(entry, None) for entry in hints])

    return symbol_hint


def rpc_hint_callback(paths: Paths) -> Callable[[], dict[str, dict[str, None]]]:
    def rpc_hint():
        rpc_definitions_list = get_json(paths.rpc_definitions_file_path)
        if rpc_definitions_list:
            rpc_definitions: list[RPCDefinition] = validate_rpc_definitions(rpc_definitions_list, silent=True)
            if rpc_definitions:
                return dict(
                    [(entry.symbol_path, dict([(method.name, None) for method in entry.methods])) for entry in
                     rpc_definitions])

    return rpc_hint
