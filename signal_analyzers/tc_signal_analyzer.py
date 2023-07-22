import dataclasses
from dataclasses import dataclass

from prompt_toolkit import print_formatted_text, HTML
from pyads import ADSError

from signal_analyzers.generic_signal_analyzers import SignalAnalyzer, fill_table, payload_to_dataclass
from signals.generic_signals import Signal
import pyads

from signals.tc_signals import TCSignal


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


# TODO: Add list of symbols to ignore
class TCSignalAnalyzer(SignalAnalyzer):

    def __init__(self):
        super().__init__()
        self._plc = pyads.Connection('127.0.0.1.1.1', pyads.PORT_TC3PLC1)
        self._plc.open()
        self._symbols = []

    async def eval(self, signal: Signal):
        tc_signal = TCSignal(**dataclasses.asdict(signal))
        try:
            if tc_signal.all_symbols:
                symbols = self._plc.get_all_symbols()
                for symbol in symbols:
                    if symbol.plc_type:
                        symbol.read()

                self._symbols = payload_to_dataclass(symbols, Symbol)

                table = fill_table(self._symbols, Symbol)
                print(table)

            elif tc_signal.get_symbol:
                if signal.payload:
                    symbol_str = signal.payload
                    signal.payload = None
                    symbol = self._plc.get_symbol(symbol_str)
                    if symbol.plc_type:
                        symbol.read()
                    table_list = payload_to_dataclass([symbol], Symbol)
                    print(fill_table(table_list, Symbol))

        except ADSError as e:
            print_formatted_text(HTML(f'<red>ERR: {e}</red>'))
