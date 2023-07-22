import asyncio

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

from signal_analyzers.fio_signal_analyzer import FIOSignalAnalyzer
from signal_analyzers.generic_signal_analyzers import SignalAnalyzer
from signals.fio_signals import FIOSignalDict
from signals.generic_signals import SignalDict, Signal


async def input_controller(queue, signal_dict: SignalDict):
    while True:
        completer = WordCompleter(list(signal_dict.keys()))
        session = PromptSession(completer=completer, multiline=False)
        user_input = await session.prompt_async()
        if user_input in signal_dict:
            signal = signal_dict[user_input]
            queue.put_nowait(signal)
            if signal.stop:
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
    signal_dict = FIOSignalDict()
    signal_analyzer = FIOSignalAnalyzer()

    await asyncio.gather(input_controller(queue, signal_dict), app_loop(queue, signal_analyzer))


if __name__ == '__main__':
    asyncio.run(main())
