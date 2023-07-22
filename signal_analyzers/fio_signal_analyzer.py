from dataclasses import dataclass

import httpx
from prompt_toolkit import print_formatted_text, HTML
from tabulate import tabulate

from constants import SERVER_URL
from signal_analyzers.generic_signal_analyzers import SignalAnalyzer
from signals.generic_signals import Signal


@dataclass
class Tag:
    name: str
    id: str
    address: int
    type: str
    kind: str
    value: bool
    openCircuit: bool
    shortCircuit: bool
    isForced: bool
    forcedValue: bool


class FIOSignalAnalyzer(SignalAnalyzer):

    def __init__(self):
        super().__init__()
        self.tags = []

    async def eval(self, signal: Signal):
        if signal.tags:
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(SERVER_URL + '/api/tags')
                    if response.status_code == 200:
                        payload = response.json()
                        self.tags.clear()
                        for tag in payload:
                            self.tags.append(Tag(**tag))
                        table_data = [['Name', 'Address', 'Type', 'Value']]

                        for tag in self.tags:
                            table_data.append([tag.name, tag.address, tag.type, tag.value])
                        print(tabulate(table_data, headers='firstrow'))
                    else:
                        print_formatted_text(
                            HTML(f'<red>ERR: Response status code is: {response.status_code}</red>'))
                except httpx.ConnectError as e:
                    print_formatted_text(HTML(f'<red>ERR: {e}</red>'))
