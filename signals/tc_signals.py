from dataclasses import dataclass

from signals.generic_signals import Signal, SignalDict


@dataclass
class TCSignal(Signal):
    all_symbols: bool = False
    get_symbol: bool = False


class TCSignalDict(SignalDict):
    def __init__(self):
        self._tc_signals = {
            "All Symbols": TCSignal(all_symbols=True),
            "Get Symbol": TCSignal(get_symbol=True)
        }
        super().__init__(self._tc_signals)
