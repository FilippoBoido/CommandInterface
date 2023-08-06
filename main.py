import asyncio

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter

from signal_analyzers.generic_signal_analyzers import SignalAnalyzer
from implementations.tc.tc_signal_analyzer import TCSignalAnalyzer
from signals.generic_signals import SignalDict, Signal
from implementations.tc.tc_signals import TCSignalDict


async def input_controller(queue, signal_dict: SignalDict):
    while True:
        completer = NestedCompleter.from_nested_dict(dict([(key, None) for key in signal_dict.keys()]))

        session = PromptSession(completer=completer, multiline=False)
        user_input: str = await session.prompt_async()
        user_input_list = user_input.split(':')
        command = user_input_list[0] + ':'
        if command in signal_dict:
            signal = signal_dict[command]
            signal.payload = user_input_list[1]
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
    # fio_signal_dict = FIOSignalDict()
    # fio_signal_analyzer = FIOSignalAnalyzer()
    tc_signal_dict = TCSignalDict()
    tc_signal_analyzer = TCSignalAnalyzer('192.168.2.115.1.1')
    await asyncio.gather(input_controller(queue, tc_signal_dict), app_loop(queue, tc_signal_analyzer))


if __name__ == '__main__':
    asyncio.run(main())
