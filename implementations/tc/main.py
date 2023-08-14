import asyncio

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter

from implementations.tc.data_classes import ConsoleArgs
from signal_analyzers.generic_signal_analyzers import SignalAnalyzer
from implementations.tc.tc_signal_analyzer import TCSignalAnalyzer
from signals.generic_signals import SignalDict, Signal
from implementations.tc.tc_signals import TCSignalDict, TCSignal


async def input_controller(queue, signal_dict: SignalDict):
    while True:
        signal: TCSignal
        completer_dict = dict([(key, signal.nested_completer_dict) for key, signal in signal_dict.items()])
        completer = NestedCompleter.from_nested_dict(completer_dict)

        session = PromptSession(completer=completer)
        user_input: str = await session.prompt_async()
        user_input_list = user_input.split(' ')
        command = user_input_list[0]
        del user_input_list[0]
        if command in signal_dict:
            signal = signal_dict[command]
            signal.payload = user_input_list
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


async def main(args: ConsoleArgs):
    queue = asyncio.Queue()
    tc_signal_dict = TCSignalDict()
    tc_signal_analyzer = TCSignalAnalyzer(args)
    await asyncio.gather(input_controller(queue, tc_signal_dict), app_loop(queue, tc_signal_analyzer))


@click.command()
@click.option('--ams-net-id', default='127.0.0.1.1.1', help='Target AMS Net ID')
@click.option('--config-path', default='', help='Optional path to a configuration file')
def console_args(ams_net_id, config_path):
    asyncio.run(main(ConsoleArgs(ams_net_id, config_path)))


if __name__ == '__main__':
    console_args()
