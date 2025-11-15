from __future__ import annotations

from typing import Callable, Type, Any, TypeVar

from tree_sitter import Tree

from mast import Terminal
from mast.node import ConcreteNode, MaskedNode

TCN = TypeVar('TCN', bound='ConcreteNode')
TMN = TypeVar('TMN', bound='MaskedNode')


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
        setattr(clss, 'get_type_name', classmethod(get_type_name))
        return clss
    return decorator


def is_root_node() -> Callable:
    def decorator(clss: Type[TCN]) -> Type[TCN]:
        def fts(cls: Type[TCN], tree: Tree) -> ConcreteNode | None:
            return cls.from_tsn(tree.root_node)
        setattr(clss, 'from_tree_sitter', classmethod(fts))
        return clss
    return decorator


def is_non_terminal_node(param_types: list[Type[TMN]]) -> Callable:
    def decorator(clss: Type[TCN]) -> Type[TCN]:
        def ce(cls: Type[TCN]) -> TCN:
            args = [t() for t in param_types]
            return cls(*args)
        setattr(clss, 'create_empty', classmethod(ce))
        return clss
    return decorator


def is_terminal_node(t: Terminal) -> Callable:
    def decorator(cls: Type[TCN]) -> Type[TCN]:
        def gtt(_: Type[TCN]) -> Terminal:
            return t
        setattr(cls, 'get_terminal_type', classmethod(gtt))
        return cls
    return decorator