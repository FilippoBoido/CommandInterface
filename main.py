import asyncio
from dataclasses import dataclass

import click
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


@dataclass
class ConsoleArgs:
    ams_net_id: str


async def main(args: ConsoleArgs):
    queue = asyncio.Queue()
    tc_signal_dict = TCSignalDict()
    tc_signal_analyzer = TCSignalAnalyzer(args.ams_net_id)
    await asyncio.gather(input_controller(queue, tc_signal_dict), app_loop(queue, tc_signal_analyzer))


@click.command()
@click.option('--ams-net-id', default='127.0.0.1.1.1', help='Target AMS Net ID')
def console_args(ams_net_id):
    asyncio.run(main(ConsoleArgs(ams_net_id)))


if __name__ == '__main__':
    console_args()
