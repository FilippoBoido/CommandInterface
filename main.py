import asyncio
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter

from signal_analyzers.fio_signal_analyzer import FIOSignalAnalyzer
from signal_analyzers.generic_signal_analyzers import SignalAnalyzer
from signal_analyzers.tc_signal_analyzer import TCSignalAnalyzer
from signals.fio_signals import FIOSignalDict
from signals.generic_signals import SignalDict, Signal
from signals.tc_signals import TCSignalDict


async def input_controller(queue, signal_dict: SignalDict):
    while True:
        completer = NestedCompleter.from_nested_dict(dict([(key, None) for key in signal_dict.keys()]))

        session = PromptSession(completer=completer, multiline=False)
        user_input: str = await session.prompt_async()
        signal: Optional[Signal] = None
        for key, value in signal_dict.items():
            if key in user_input:
                signal: Signal = value
                if key != user_input:
                    signal.payload = user_input.split(key)[1].strip()
                queue.put_nowait(signal)
                break
        if signal and signal.stop:
            break


async def app_loop(queue, signal_analyzer: SignalAnalyzer):
    while True:
        if queue.empty():
            await asyncio.sleep(0.1)
        else:
            sig: Signal = queue.get_nowait()
            await signal_analyzer.eval(sig)
            if sig.stop:
                break


async def main():
    queue = asyncio.Queue()
    # fio_signal_dict = FIOSignalDict()
    # fio_signal_analyzer = FIOSignalAnalyzer()
    tc_signal_dict = TCSignalDict()
    tc_signal_analyzer = TCSignalAnalyzer()
    await asyncio.gather(input_controller(queue, tc_signal_dict), app_loop(queue, tc_signal_analyzer))


if __name__ == '__main__':
    asyncio.run(main())
