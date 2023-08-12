from dataclasses import dataclass
from signals.generic_signals import Signal, SignalDict
from utilities.functions import symbol_hint


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
    notification_list: bool = False
    add_to_notification_list: bool = False
    remove_from_notification_list: bool = False
    clear_notification_list: bool = False
    stop_notifications: bool = False
    add_to_hint_list: bool = False
    remove_from_hint_list: bool = False
    clear_hint_list: bool = False


class TCSignalDict(SignalDict):
    def __init__(self):
        self._tc_signals = {
            "GetAllSymbols": TCSignal(get_all_symbols=True),
            "GetSymbol": TCSignal(get_symbol=True, nested_completer_func=symbol_hint),
            "SetSymbol": TCSignal(set_symbol=True, nested_completer_func=symbol_hint),
            "IgnoreList": TCSignal(ignore_list=True),
            "AddToIgnore": TCSignal(add_to_ignore=True),
            "RemoveFromIgnore": TCSignal(remove_from_ignore=True),
            "ClearIgnoreList": TCSignal(clear_ignore_list=True),
            "Watchlist": TCSignal(watchlist=True),
            "AddToWatchlist": TCSignal(add_to_watchlist=True),
            "RemoveFromWatchlist": TCSignal(remove_from_watchlist=True),
            "ClearWatchlist": TCSignal(clear_watchlist=True),
            "Notify": TCSignal(notify=True),
            "StopNotification": TCSignal(stop_notification=True),
            "NotificationList": TCSignal(notification_list=True),
            "AddToNotificationList": TCSignal(add_to_notification_list=True),
            "RemoveFromNotificationList": TCSignal(remove_from_notification_list=True),
            "ClearNotificationList": TCSignal(clear_notification_list=True),
            "StopNotifications": TCSignal(stop_notifications=True),
            "AddToHintList": TCSignal(add_to_hint_list=True),
            "RemoveFromHintList": TCSignal(remove_from_hint_list=True),
            "ClearHintList": TCSignal(clear_hint_list=True)
        }
        super().__init__(self._tc_signals)
