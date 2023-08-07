from dataclasses import dataclass

from signals.generic_signals import Signal, SignalDict


@dataclass
class TCSignal(Signal):
    all_symbols: bool = False
    get_symbol: bool = False
    ignore_list: bool = False
    add_to_ignore: bool = False
    remove_from_ignore: bool = False
    clear_ignore_list: bool = False
    watchlist: bool = False
    add_to_watchlist: bool = False
    remove_from_watchlist: bool = False
    clear_watchlist: bool = False
    notify: bool = False
    clear_notification: bool = False


class TCSignalDict(SignalDict):
    def __init__(self):
        # Remember the ':' symbol after the name of the signal
        self._tc_signals = {
            "All symbols:": TCSignal(all_symbols=True),
            "Get symbol:": TCSignal(get_symbol=True),
            "Ignore list:": TCSignal(ignore_list=True),
            "Add symbol to ignore list:": TCSignal(add_to_ignore=True),
            "Remove symbol from ignore list:": TCSignal(remove_from_ignore=True),
            "Clear ignore list:": TCSignal(clear_ignore_list=True),
            "Watchlist:": TCSignal(watchlist=True),
            "Add symbol to watchlist:": TCSignal(add_to_watchlist=True),
            "Remove symbol from watchlist:": TCSignal(remove_from_watchlist=True),
            "Clear watchlist:": TCSignal(clear_watchlist=True),
            "Notify:": TCSignal(notify=True),
            "Clear notification:": TCSignal(clear_notification=True)
        }
        super().__init__(self._tc_signals)
