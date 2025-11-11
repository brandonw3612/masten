from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, TYPE_CHECKING

if TYPE_CHECKING:
    from mast.node import AbstractNode

TC = TypeVar('TC')
class Enumerable(Generic[TC], ABC):
    @abstractmethod
    def enumerate(self) -> list[tuple[str, TC]]:
        pass

    @abstractmethod
    def replace(self, old: TC, new: TC):
        pass


T = TypeVar('T')
class LabeledContainer(Generic[T], Enumerable[T]):
    def __init__(self, labels: list[str] | None = None):
        if labels is None:
            labels = list[str]()
        self._labels = labels
        self._items : list[T] = [None] * len(labels)

    def __getitem__(self, key: str):
        return self._items[self._labels.index(key)]

    def __setitem__(self, key: str, value: T):
        self._items[self._labels.index(key)] = value

    def enumerate(self) -> list[tuple[str, T]]:
        return list(zip(self._labels, self._items))

    def replace(self, old: T, new: T):
        self._items[self._items.index(old)] = new


class ChildrenContainer(Enumerable['AbstractNode']):
    def __init__(self):
        self._children: list['AbstractNode'] = []

    def __getitem__(self, index: int):
        return self._children[index]

    def append(self, child: 'AbstractNode'):
        self._children.append(child)

    def insert(self, index: int, child: 'AbstractNode'):
        self._children.insert(index, child)

    def exchange(self, child1: 'AbstractNode', child2: 'AbstractNode'):
        i1 = self._children.index(child1)
        i2 = self._children.index(child2)
        self._children[i1], self._children[i2] = self._children[i2], self._children[i1]

    def replace(self, child1: 'AbstractNode', child2: 'AbstractNode'):
        self._children[self._children.index(child1)] = child2

    def remove(self, child: 'AbstractNode'):
        self._children.remove(child)

    def enumerate(self) -> list[tuple[str, 'AbstractNode']]:
        return [('child', child) for child in self._children]