from abc import ABC, abstractmethod

from mast.node import MaskedNode


class Decorruptor(ABC):
    @abstractmethod
    def decorrupt(self, tree: MaskedNode):
        pass