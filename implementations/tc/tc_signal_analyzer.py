import dataclasses
import os
from typing import Optional

from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.shortcuts import yes_no_dialog
from pyads import ADSError
from tabulate import tabulate
from implementations.tc.data_classes import ConsoleArgs, Paths
from implementations.tc.tc_types import validate_rpc_definitions
from signal_analyzers.generic_signal_analyzers import SignalAnalyzer
from implementations.tc.ads import (
    print_out_symbols,
    get_symbol_str,
    print_out_symbol,
    get_ads_symbol,
    add_notification,
    set_symbol,
    signal_to_rpc_call
)
from utilities.file import get_list_from_file, add_to_file, remove_from_file, get_json
from signals.generic_signals import Signal
import pyads

from implementations.tc.tc_signals import TCSignal
from utilities.functions import show_notifications


class TCSignalAnalyzer(SignalAnalyzer):

    def __init__(self, args: ConsoleArgs, port=pyads.PORT_TC3PLC1):
        super().__init__()
        self._paths = Paths(args.path_config)
        self._plc = pyads.Connection(args.ams_net_id, port)
        self._plc.open()
        self._notification_dict = {}

    def cleanup(self):
        for notification in self._notification_dict.values():
            notification.clear_device_notifications()

    async def eval(self, signal: Signal):
        tc_signal = TCSignal(**dataclasses.asdict(signal))
        try:
            if tc_signal.get_all_symbols:
                ignore_symbols: Optional[list] = get_list_from_file(self._paths.ignore_ads_symbols_file_path)
                symbols = self._plc.get_all_symbols()

                filtered_symbols = []
                for symbol in symbols:
                    if ignore_symbols and symbol.name in ignore_symbols:
                        continue
                    add_to_file(self._paths.symbol_hints_file_path, symbol.name)
                    filtered_symbols.append(symbol)
                    if symbol.plc_type:
                        symbol.read()

                print_out_symbols(filtered_symbols)

            elif tc_signal.get_symbol:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    print_out_symbol(self._plc, symbol_str)

            elif tc_signal.set_symbol:
                if signal.payload and len(signal.payload) > 1:
                    symbol_str = signal.payload[0]
                    value = signal.payload[1]
                    set_symbol(self._plc, symbol_str, value)
                    print_out_symbol(self._plc, symbol_str)

            elif tc_signal.add_to_ignore:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    add_to_file(self._paths.ignore_ads_symbols_file_path, symbol_str)

            elif tc_signal.add_to_watchlist:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    add_to_file(self._paths.watchlist_file_path, symbol_str)
                    add_to_file(self._paths.symbol_hints_file_path, symbol_str)
                    print_out_symbol(self._plc, symbol_str)

            elif tc_signal.remove_from_ignore:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    remove_from_file(self._paths.ignore_ads_symbols_file_path, symbol_str)
                    add_to_file(self._paths.symbol_hints_file_path, symbol_str)

            elif tc_signal.remove_from_watchlist:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    remove_from_file(self._paths.watchlist_file_path, symbol_str)

            elif tc_signal.ignore_list:
                if os.path.isfile(self._paths.ignore_ads_symbols_file_path):
                    ignore_list = get_list_from_file(self._paths.ignore_ads_symbols_file_path)
                    tabulate_data = [[value] for value in ignore_list]
                    print(tabulate(tabulate_data, headers=['ADS Symbols in ignore list']))

            elif tc_signal.watchlist:
                if os.path.isfile(self._paths.watchlist_file_path):
                    watchlist = get_list_from_file(self._paths.watchlist_file_path)
                    if watchlist:
                        watchlist_symbols = []
                        for watchlist_symbol in watchlist:
                            symbol = get_ads_symbol(self._plc, watchlist_symbol)
                            watchlist_symbols.append(symbol)
                        print_out_symbols(watchlist_symbols)

            elif tc_signal.add_to_hint_list:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    add_to_file(self._paths.symbol_hints_file_path, symbol_str)
                    print_out_symbol(self._plc, symbol_str)

            elif tc_signal.remove_from_hint_list:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    remove_from_file(self._paths.symbol_hints_file_path, symbol_str)

            elif tc_signal.clear_hint_list:
                if os.path.isfile(self._paths.symbol_hints_file_path):
                    result = await yes_no_dialog(
                        title='Clear hint list',
                        text='Are you sure you want to clear the hint list?',
                    ).run_async()
                    if result:
                        os.remove(self._paths.symbol_hints_file_path)

            elif tc_signal.clear_ignore_list:
                if os.path.isfile(self._paths.ignore_ads_symbols_file_path):
                    result = await yes_no_dialog(
                        title='Clear ignore list',
                        text='Are you sure you want to clear the ignore list?',
                    ).run_async()
                    if result:
                        os.remove(self._paths.ignore_ads_symbols_file_path)

            elif tc_signal.clear_watchlist:
                if os.path.isfile(self._paths.watchlist_file_path):
                    result = await yes_no_dialog(
                        title='Clear watchlist',
                        text='Are you sure you want to clear the watchlist?',
                    ).run_async()
                    if result:
                        os.remove(self._paths.watchlist_file_path)

            elif tc_signal.notify:
                if tc_signal.payload:
                    symbol_str = get_symbol_str(tc_signal)
                    target_symbol = get_ads_symbol(self._plc, symbol_str)

                    add_notification(target_symbol, self._notification_dict, self._paths)

            elif tc_signal.stop_notification:
                if tc_signal.payload:
                    symbol_str = get_symbol_str(tc_signal)
                    if symbol_str in self._notification_dict:
                        self._notification_dict[symbol_str].clear_device_notifications()
                        del self._notification_dict[symbol_str]
                        print("Done")
                    else:
                        print("Nothing to do")

            elif tc_signal.start_notifications:
                if os.path.isfile(self._paths.notification_symbols_file_path):
                    notification_list = get_list_from_file(self._paths.notification_symbols_file_path)
                    if notification_list:
                        for notification_str in notification_list:
                            symbol = get_ads_symbol(self._plc, notification_str)
                            add_notification(symbol, notification_dict=self._notification_dict, paths=self._paths)
                else:
                    print(f"Nothing to do: No file {self._paths.notification_symbols_file_path} found.")

            elif tc_signal.show_notifications:
                show_notifications(file_path=self._paths.ads_notifications_file_path)

            elif tc_signal.add_to_notification_list:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    add_to_file(self._paths.notification_symbols_file_path, symbol_str)
                    add_to_file(self._paths.symbol_hints_file_path, symbol_str)

            elif tc_signal.remove_from_notification_list:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    remove_from_file(self._paths.notification_symbols_file_path, symbol_str)

            elif tc_signal.clear_notification_list:
                if os.path.isfile(self._paths.notification_symbols_file_path):
                    result = await yes_no_dialog(
                        title='Clear notification list',
                        text='Are you sure you want to clear the notification list?',
                    ).run_async()
                    if result:
                        os.remove(self._paths.notification_symbols_file_path)

            elif tc_signal.stop_notifications:
                if os.path.isfile(self._paths.notification_symbols_file_path):
                    notification_list = get_list_from_file(self._paths.notification_symbols_file_path)
                    if notification_list:
                        for notification in notification_list:
                            if notification in self._notification_dict:
                                self._notification_dict[notification].clear_device_notifications()
                                del self._notification_dict[notification]
                                print(f"Notification for {notification} symbol stopped")

            elif tc_signal.rpc:
                rpc_definitions_json = get_json(self._paths.rpc_definitions_file_path)
                if rpc_definitions_json:
                    rpc_definitions = validate_rpc_definitions(rpc_definitions_json)
                    if not rpc_definitions:
                        return
                    try:
                        signal_to_rpc_call(self._plc, tc_signal, rpc_definitions)
                    except ValueError as e:
                        print(e)

                else:
                    print(f"No rpc definitions or file {self._paths.rpc_definitions_file_path} found.")

        except ADSError as e:
            print_formatted_text(HTML(f'<red>ERR: {e}</red>'))
