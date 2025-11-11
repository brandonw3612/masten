from typing import TypeVar, Type, Callable

from mast.node import ConcreteNode, MaskedNode


TM = TypeVar('TM', bound='MaskedNode')
TN = TypeVar('TN', bound='ConcreteNode')

def can_mask(masked_node_type: Type[TM]) -> Callable:
    def decorator(cls: Type[TN]) -> Type[TN]:
        def mask(self: TN):
            masked_node = masked_node_type()
            self.parent.subtrees.replace(self, masked_node)
            return masked_node
        setattr(cls, 'mask', mask)
        return cls
    return decorator

def can_unmask(unmasked_node_type: Type[TN]) -> Callable:
    def decorator(cls: Type[TM]) -> Type[TM]:
        def unmask(self: TM, concrete_node: TN):
            if not isinstance(concrete_node, unmasked_node_type):
                raise ValueError(f'Expected {unmasked_node_type.__name__}, got {concrete_node.__class__.__name__}')
            self.parent.subtrees.replace(self, concrete_node)
            return concrete_node
        setattr(cls, 'unmask', unmask)
        # TODO: How does MASTENN know what type of node needs to be synthesized here? A query is needed.
        return cls
    return decorator

def can_mask_up(ancestor_mask_types: list[Type[TM]]) -> Callable:
    def decorator(cls: Type[TM]) -> Type[TM]:
        def mask_up(self: TM, ancestor_type: Type[TN]):
            if ancestor_type not in ancestor_mask_types:
                raise TypeError(f'Cannot mask up "{cls.get_type_name()}" to "{ancestor_type.get_type_name()}".')
            ancestor_mask = ancestor_type()
            self.parent.subtrees.replace(self, ancestor_mask)
            return ancestor_mask
        setattr(cls, 'mask_up', mask_up)
        return cls
    return decorator

def can_mask_down(descendant_mask_types: list[Type[TM]]) -> Callable:
    def decorator(cls: Type[TM]) -> Type[TM]:
        def mask_down(self: TN, descendant_type: Type[TM]):
            if descendant_type not in descendant_mask_types:
                raise TypeError(f'Cannot mask down "{descendant_type.get_type_name()}" to "{cls.get_type_name()}".')
            descendant_mask = descendant_type()
            self.parent.subtrees.replace(self, descendant_mask)
            return descendant_mask
        setattr(cls, 'mask_down', mask_down)
        return cls
    return decorator

def can_binop_swap(op1: str, op2: str) -> Callable:
    def decorator(cls: Type[TN]) -> Type[TN]:
        def binop_swap(self: TN):
            left = self.subtrees[op1]
            right = self.subtrees[op2]
            self.subtrees[op1] = right
            self.subtrees[op2] = left
        setattr(cls, 'binop_swap', binop_swap)
        return cls
    return decorator