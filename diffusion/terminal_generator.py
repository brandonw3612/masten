from abc import ABC, abstractmethod
from typing import Any

from mast import Terminal

class TerminalGenerator(ABC):
    @abstractmethod
    def generate(self, ctx: Any, task_type: Terminal) -> Any:
        pass