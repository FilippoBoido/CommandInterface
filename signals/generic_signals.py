from abc import ABC
from collections import UserDict
from dataclasses import dataclass
from typing import Any, Optional, Callable


@dataclass
class Signal(ABC):
    stop: bool = False
    payload: Optional[Any] = None
    nested_completer_func: Optional[Callable[[], dict]] = None

    @property
    def nested_completer_dict(self) -> Optional[dict]:
        if self.nested_completer_func:
            return self.nested_completer_func()

    @nested_completer_dict.setter
    def nested_completer_dict(self, getter_func: Callable[[], dict]):
        self.nested_completer_func = getter_func


_initial_dict = {"Quit": Signal(stop=True)}


class SignalDict(UserDict):
    def __init__(self, initial_data: dict = None):
        if not initial_data:
            initial_data = _initial_dict.copy()
        else:
            initial_data.update(_initial_dict)
        super().__init__(initial_data)
