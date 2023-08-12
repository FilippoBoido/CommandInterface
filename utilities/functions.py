import dataclasses
from typing import Optional

from tabulate import tabulate

from implementations.tc import constants
from utilities.file import get_list_from_file


def payload_to_dataclass(payload: list, dataclass_arg):
    dataclass_list = []
    for elem in payload:
        try:
            dataclass_list.append(dataclass_arg(**elem))
        except TypeError:
            fields = [elem.__getattribute__(field.name) for field in dataclasses.fields(dataclass_arg)]
            dataclass_list.append(dataclass_arg(*fields))
    return dataclass_list


def fill_table(elem_list: list, dataclass_arg) -> str:
    table_data = [[field.name.capitalize() for field in dataclasses.fields(dataclass_arg)]]

    for elem in elem_list:
        table_data.append([value for value in dataclasses.asdict(elem).values()])
    return tabulate(table_data, headers='firstrow')


def symbol_hint() -> Optional[dict]:
    hints = get_list_from_file(constants.SYMBOL_HINT_FILE_PATH)
    if hints:
        return dict([(entry, None) for entry in hints])