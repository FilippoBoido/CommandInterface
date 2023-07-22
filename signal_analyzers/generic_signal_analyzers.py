from abc import abstractmethod, ABC

from signals.generic_signals import Signal


class SignalAnalyzer(ABC):
    @abstractmethod
    async def eval(self, signal: Signal): ...
