from dataclasses import dataclass

from implementations.tc.data_classes import Paths
from signals.generic_signals import Signal, SignalDict
from implementations.tc.console_hints import symbol_hint_callback, rpc_hint_callback


@dataclass
class TCSignal(Signal):
    get_all_symbols: bool = False
    get_symbol: bool = False
    set_symbol: bool = False
    ignore_list: bool = False
    add_to_ignore: bool = False
    remove_from_ignore: bool = False
    clear_ignore_list: bool = False
    watchlist: bool = False
    add_to_watchlist: bool = False
    remove_from_watchlist: bool = False
    clear_watchlist: bool = False
    notify: bool = False
    stop_notification: bool = False
    start_notifications: bool = False
    show_notifications: bool = False
    add_to_notification_list: bool = False
    remove_from_notification_list: bool = False
    clear_notification_list: bool = False
    stop_notifications: bool = False
    add_to_hint_list: bool = False
    remove_from_hint_list: bool = False
    clear_hint_list: bool = False
    rpc: bool = False
    download_recipe: bool = False
    upload_recipe: bool = False


class TCSignalDict(SignalDict):
    def __init__(self, paths: Paths):
        self.paths = paths
        self._tc_signals = {
            "GetAllSymbols": TCSignal(get_all_symbols=True),
            "GetSymbol": TCSignal(get_symbol=True, nested_completer_func=symbol_hint_callback(paths)),
            "SetSymbol": TCSignal(set_symbol=True, nested_completer_func=symbol_hint_callback(paths)),
            "IgnoreList": TCSignal(ignore_list=True),
            "AddToIgnore": TCSignal(add_to_ignore=True, nested_completer_func=symbol_hint_callback(paths)),
            "RemoveFromIgnore": TCSignal(remove_from_ignore=True),
            "ClearIgnoreList": TCSignal(clear_ignore_list=True),
            "Watchlist": TCSignal(watchlist=True),
            "AddToWatchlist": TCSignal(add_to_watchlist=True, nested_completer_func=symbol_hint_callback(paths)),
            "RemoveFromWatchlist": TCSignal(remove_from_watchlist=True),
            "ClearWatchlist": TCSignal(clear_watchlist=True),
            "Notify": TCSignal(notify=True, nested_completer_func=symbol_hint_callback(paths)),
            "StopNotification": TCSignal(stop_notification=True),
            "StartNotifications": TCSignal(start_notifications=True),
            "ShowNotifications": TCSignal(show_notifications=True),
            "AddToNotificationList": TCSignal(add_to_notification_list=True,
                                              nested_completer_func=symbol_hint_callback(paths)),
            "RemoveFromNotificationList": TCSignal(remove_from_notification_list=True),
            "ClearNotificationList": TCSignal(clear_notification_list=True),
            "StopNotifications": TCSignal(stop_notifications=True),
            "AddToHintList": TCSignal(add_to_hint_list=True),
            "RemoveFromHintList": TCSignal(remove_from_hint_list=True),
            "ClearHintList": TCSignal(clear_hint_list=True),
            "RPC": TCSignal(rpc=True, nested_completer_func=rpc_hint_callback(paths)),
            "DownloadRecipe": TCSignal(download_recipe=True),
            "UploadRecipe": TCSignal(upload_recipe=True)
        }
        super().__init__(self._tc_signals)
