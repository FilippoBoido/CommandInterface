from abc import ABC
from collections import UserDict
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Signal(ABC):
    stop: bool = False
    payload: Optional[Any] = None


_initial_dict = {"Quit": Signal(stop=True)}


class SignalDict(UserDict):
    def __init__(self, initial_data: dict = None):
        if not initial_data:
            initial_data = _initial_dict.copy()
        else:
            initial_data.update(_initial_dict)
        super().__init__(initial_data)
