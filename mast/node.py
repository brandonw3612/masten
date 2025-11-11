from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Type
from uuid import uuid4

from tree_sitter import Node as TNode
from tree_sitter import Tree

from mast import Corruption
from mast.container import LabeledContainer, ChildrenContainer


class AbstractNode(ABC):
    def __init__(self):
        self.id = uuid4()
        self.parent : ConcreteNode | None = None
        self.attributes : LabeledContainer[Any] | None = None
        self.subtrees : LabeledContainer[AbstractNode] | ChildrenContainer | None = None

    def enumerate_attributes(self) -> list[tuple[str, Any]]:
        if self.attributes is None:
            return []
        return self.attributes.enumerate()

    def enumerate_nodes(self) -> list[tuple[str, AbstractNode]]:
        if self.subtrees is None:
            return []
        return self.subtrees.enumerate()

    # @abstractmethod
    # def corrupt(self, crp: Corruption, args: list[Any]):
    #     pass

    @abstractmethod
    def to_source(self) -> str:
        pass

    @classmethod
    def get_type_name(cls) -> str:
        return 'Node'

    @classmethod
    def get_supported_corruptions(cls) -> list[Corruption]:
        corruptions = list[Corruption]()
        if hasattr(cls, 'mask'):
            corruptions.append(Corruption.MASK)
        if hasattr(cls, 'unmask'):
            corruptions.append(Corruption.UNMASK)
        if hasattr(cls, 'mask_up'):
            corruptions.append(Corruption.MASK_UP)
        if hasattr(cls, 'mask_down'):
            corruptions.append(Corruption.MASK_DOWN)
        if hasattr(cls, 'binop_swap'):
            corruptions.append(Corruption.BINOP_SWAP)
        return corruptions

    def corrupt(self, crpt: Corruption, args: list[Any]):
        if crpt == Corruption.MASK and hasattr(self, 'mask'):
            self.mask()
        elif crpt == Corruption.UNMASK and hasattr(self, 'unmask'):
            if len(args) != 1:
                raise ValueError('UNMASK requires one argument: the concrete node to unmask to.')
            self.unmask(args[0])
        elif crpt == Corruption.BINOP_SWAP and hasattr(self, 'binop_swap'):
            self.binop_swap()
        else:
            raise ValueError(f'Corruption {crpt} not supported for node type {self.get_type_name()}.')


class ConcreteNode(AbstractNode):
    @classmethod
    @abstractmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        pass

    @classmethod
    def tree_sitter_rule(cls) -> str:
        return 'rule'


class MaskedNode(AbstractNode):
    def __init__(self):
        super().__init__()
        self._node_type = AbstractNode

    def get_type_name(self) -> str:
        return f'{self._node_type.__name__} MASK'

    def to_source(self) -> str:
        return f'[{self._node_type.__name__} MASK]'


class RootNode(ABC):
    @classmethod
    def from_tree_sitter(cls, tree: Tree) -> ConcreteNode | None:
        pass