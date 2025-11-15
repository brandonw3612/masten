from abc import ABC, abstractmethod

from mast.node import MaskedNode, ConcreteNode


class Decorruptor(ABC):
    @abstractmethod
    def decorrupt(self, tree: MaskedNode):
        pass