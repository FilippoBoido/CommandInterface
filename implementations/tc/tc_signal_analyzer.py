import dataclasses
import os
from typing import Optional

from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.shortcuts import yes_no_dialog
from pyads import ADSError
from tabulate import tabulate

from implementations.tc import constants
from signal_analyzers.generic_signal_analyzers import SignalAnalyzer
from utilities.ads import print_out_symbols, get_symbol_str, print_out_symbol, get_ads_symbol, add_notification
from utilities.functions import add_to_file, remove_from_file, get_list_from_file
from signals.generic_signals import Signal
import pyads

from implementations.tc.tc_signals import TCSignal


class TCSignalAnalyzer(SignalAnalyzer):

    def __init__(self, ams_net_id='127.0.0.1.1.1', port=pyads.PORT_TC3PLC1):
        super().__init__()
        self._plc = pyads.Connection(ams_net_id, port)
        self._plc.open()
        self._ignore_list_path = constants.IGNORE_ADS_SYMBOLS_FILE_PATH
        self._watchlist_path = constants.WATCHLIST_FILE_PATH
        self._notification_list_path = constants.NOTIFICATION_FILE_PATH
        self._notification_dict = {}

    def cleanup(self):
        for notification in self._notification_dict.values():
            notification.clear_device_notifications()

    async def eval(self, signal: Signal):
        tc_signal = TCSignal(**dataclasses.asdict(signal))
        try:
            if tc_signal.all_symbols:
                ignore_symbols: Optional[list] = get_list_from_file(self._ignore_list_path)

                symbols = self._plc.get_all_symbols()
                filtered_symbols = []
                for symbol in symbols:
                    if ignore_symbols and symbol.name in ignore_symbols:
                        continue
                    filtered_symbols.append(symbol)
                    if symbol.plc_type:
                        symbol.read()

                print_out_symbols(filtered_symbols)

            elif tc_signal.get_symbol:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    print_out_symbol(self._plc, symbol_str)

            elif tc_signal.add_to_ignore:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    add_to_file(self._ignore_list_path, symbol_str)

            elif tc_signal.add_to_watchlist:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    add_to_file(self._watchlist_path, symbol_str)
                    print_out_symbol(self._plc, symbol_str)

            elif tc_signal.remove_from_ignore:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    remove_from_file(self._ignore_list_path, symbol_str)

            elif tc_signal.remove_from_watchlist:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    remove_from_file(self._watchlist_path, symbol_str)

            elif tc_signal.ignore_list:
                if os.path.isfile(self._ignore_list_path):
                    ignore_list = get_list_from_file(self._ignore_list_path)
                    tabulate_data = [[value] for value in ignore_list]
                    print(tabulate(tabulate_data, headers=['ADS Symbols in ignore list']))

            elif tc_signal.watchlist:
                if os.path.isfile(self._watchlist_path):
                    watchlist = get_list_from_file(self._watchlist_path)
                    if watchlist:
                        watchlist_symbols = []
                        for watchlist_symbol in watchlist:
                            symbol = get_ads_symbol(self._plc, watchlist_symbol)
                            watchlist_symbols.append(symbol)
                        print_out_symbols(watchlist_symbols)

            elif tc_signal.clear_ignore_list:
                if os.path.isfile(self._ignore_list_path):
                    result = await yes_no_dialog(
                        title='Clear Ignore list',
                        text='Are you sure you want to clear the ignore list?',
                    ).run_async()
                    if result:
                        os.remove(self._ignore_list_path)

            elif tc_signal.clear_watchlist:
                if os.path.isfile(self._watchlist_path):
                    result = await yes_no_dialog(
                        title='Clear Watchlist',
                        text='Are you sure you want to clear the Watchlist?',
                    ).run_async()
                    if result:
                        os.remove(self._watchlist_path)

            elif tc_signal.notify:
                if tc_signal.payload:
                    symbol_str = get_symbol_str(tc_signal)
                    target_symbol = get_ads_symbol(self._plc, symbol_str)

                    add_notification(target_symbol, self._notification_dict)

            elif tc_signal.stop_notification:
                if tc_signal.payload:
                    symbol_str = get_symbol_str(tc_signal)
                    if symbol_str in self._notification_dict:
                        self._notification_dict[symbol_str].clear_device_notifications()
                        del self._notification_dict[symbol_str]
                        print("Done")
                    else:
                        print("Nothing to do")

            elif tc_signal.notification_list:
                if os.path.isfile(self._notification_list_path):
                    notification_list = get_list_from_file(self._notification_list_path)
                    if notification_list:
                        for notification_str in notification_list:
                            symbol = get_ads_symbol(self._plc, notification_str)
                            add_notification(symbol, notification_dict=self._notification_dict)

            elif tc_signal.add_to_notification_list:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    add_to_file(self._notification_list_path, symbol_str)

            elif tc_signal.remove_from_notification_list:
                if signal.payload:
                    symbol_str = get_symbol_str(signal)
                    remove_from_file(self._notification_list_path, symbol_str)

            elif tc_signal.clear_notification_list:
                if os.path.isfile(self._notification_list_path):
                    result = await yes_no_dialog(
                        title='Clear Watchlist',
                        text='Are you sure you want to clear the Watchlist?',
                    ).run_async()
                    if result:
                        os.remove(self._notification_list_path)

            elif tc_signal.stop_notifications:
                if os.path.isfile(self._notification_list_path):
                    notification_list = get_list_from_file(self._notification_list_path)
                    if notification_list:
                        for notification in notification_list:
                            if notification in self._notification_dict:
                                self._notification_dict[notification].clear_device_notifications()
                                del self._notification_dict[notification]
                                print(f"Notification for {notification} symbol stopped")

        except ADSError as e:
            print_formatted_text(HTML(f'<red>ERR: {e}</red>'))
