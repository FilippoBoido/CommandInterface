import asyncio
from dataclasses import dataclass


import httpx
from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.completion import WordCompleter
from tabulate import tabulate

from constants import SERVER_URL


@dataclass
class Signal:
    stop: bool = False
    tags: bool = False


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


SignalDict = {
    "Tags": Signal(tags=True),
    "Quit": Signal(stop=True)

}


async def input_controller(queue):
    while True:
        completer = WordCompleter(SignalDict.keys())
        session = PromptSession(completer=completer, multiline=False)
        user_input = await session.prompt_async()
        if user_input in SignalDict:
            signal = SignalDict[user_input]
            queue.put_nowait(signal)
            if signal.stop:
                break


async def app_loop(queue):
    tags = []

    while True:
        if queue.empty():
            await asyncio.sleep(0.1)
        else:
            sig: Signal = queue.get_nowait()
            if sig.stop:
                break
            elif sig.tags:
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.get(SERVER_URL + '/api/tags')
                        if response.status_code == 200:
                            payload = response.json()
                            tags.clear()
                            for tag in payload:
                                tags.append(Tag(**tag))
                            table_data = [['Name', 'Address', 'Type', 'Value']]

                            for tag in tags:
                                table_data.append([tag.name, tag.address, tag.type, tag.value])
                            print(tabulate(table_data, headers='firstrow'))
                        else:
                            print_formatted_text(
                                HTML(f'<red>ERR: Response status code is: {response.status_code}</red>'))
                    except httpx.ConnectError as e:
                        print_formatted_text(HTML(f'<red>ERR: {e}</red>'))


async def main():
    queue = asyncio.Queue()
    await asyncio.gather(input_controller(queue), app_loop(queue))


if __name__ == '__main__':
    asyncio.run(main())
