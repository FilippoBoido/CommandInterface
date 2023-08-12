from dataclasses import dataclass
from datetime import datetime, timedelta

from pyads import Connection

from signals.generic_signals import Signal
from utilities.functions import payload_to_dataclass, fill_table


@dataclass
class Symbol:
    name: str
    comment: str
    symbol_type: str
    array_size: int
    auto_update: bool
    index_group: int
    index_offset: int
    value: None


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


def add_notification(symbol, notification_dict, callback=None):
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

                # {notification_header.contents.data}
                output_string = (
                    f"{formatted_date_time}: Notification received for symbol {symbol.name}. "
                    f"Value changed to: {payload}\n")

                with open('ADSNotification.txt', 'a') as notification_file:
                    notification_file.write(output_string)

            callback = _notification_callback

        return_val = symbol.add_device_notification(callback)
        notification_dict[symbol.name] = symbol
        print(f"Notification callback for symbol {symbol.name} setup successfully {return_val}")
