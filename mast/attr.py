from __future__ import annotations

from typing import Callable, Type, Any, TypeVar

from tree_sitter import Tree

from mast.node import ConcreteNode


TCN = TypeVar('TCN', bound='ConcreteNode')


def tree_sitter_rule(rule: str) -> Callable:
    def decorator(clss: Type[Any]) -> Type[Any]:
        def tsr(cls) -> str:
            return rule
        class_method = classmethod(tsr)
        setattr(clss, 'tree_sitter_rule', class_method)
        return clss
    return decorator

def node_type_name(name: str | None = None) -> Callable:
    def decorator(clss: Type[Any]) -> Type[Any]:
        def get_type_name(cls) -> str:
            return name or cls.__name__
        class_method = classmethod(get_type_name)
        setattr(clss, 'get_type_name', class_method)
        return clss
    return decorator

def root_node() -> Callable:
    def decorator(clss: Type[TCN]) -> Type[TCN]:
        def fts(cls: Type[TCN], tree: Tree) -> ConcreteNode | None:
            return cls.from_tsn(tree.root_node)
        class_method = classmethod(fts)
        setattr(clss, 'from_tree_sitter', class_method)
        return clss
    return decorator