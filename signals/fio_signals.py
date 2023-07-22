from dataclasses import dataclass

from signals.generic_signals import Signal, SignalDict


@dataclass
class FIOSignal(Signal):
    tags: bool = False


class FIOSignalDict(SignalDict):
    def __init__(self):
        self._fio_signals = {
            "Tags": FIOSignal(tags=True),
        }
        super().__init__(self._fio_signals)
