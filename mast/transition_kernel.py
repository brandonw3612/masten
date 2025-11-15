from typing import TypeVar, Type, Callable

from mast.node import ConcreteNode, MaskedNode


TM = TypeVar('TM', bound='MaskedNode')
TN = TypeVar('TN', bound='ConcreteNode')

def kernel_mask(masked_node_type: Type[TM]) -> Callable:
    def decorator(cls: Type[TN]) -> Type[TN]:
        def mask(self: TN):
            masked_node = masked_node_type()
            self.parent.subtrees.replace(self, masked_node)
            masked_node.parent = self.parent
            return masked_node
        setattr(cls, 'mask', mask)
        return cls
    return decorator

def kernel_unmask(unmasked_node_type: Type[TN]) -> Callable:
    def decorator(cls: Type[TM]) -> Type[TM]:
        def unmask(self: TM, concrete_node: TN):
            if not isinstance(concrete_node, unmasked_node_type):
                raise ValueError(f'Expected {unmasked_node_type.__name__}, got {concrete_node.__class__.__name__}')
            self.parent.subtrees.replace(self, concrete_node)
            concrete_node.parent = self.parent
            return concrete_node
        setattr(cls, 'unmask', unmask)
        def unmask_target(_: Type[TM]) -> Type[TN]:
            return unmasked_node_type
        setattr(cls, 'unmask_target', classmethod(unmask_target))
        return cls
    return decorator

def kernel_mask_up(ancestor_mask_types: set[Type[TM]]) -> Callable:
    def decorator(cls: Type[TM]) -> Type[TM]:
        def mask_up(self: TM, ancestor_type: Type[TN]):
            if ancestor_type not in ancestor_mask_types:
                raise TypeError(f'Cannot mask up "{cls.get_type_name()}" to "{ancestor_type.get_type_name()}".')
            ancestor_mask = ancestor_type()
            self.parent.subtrees.replace(self, ancestor_mask)
            ancestor_mask.parent = self.parent
            return ancestor_mask
        setattr(cls, 'mask_up', mask_up)
        def gamt(_: Type[TN]) -> set[Type[TM]]:
            return ancestor_mask_types
        setattr(cls, 'get_ancestor_mask_types', classmethod(gamt))
        return cls
    return decorator

def kernel_mask_down(descendant_mask_types: set[Type[TM]]) -> Callable:
    def decorator(cls: Type[TM]) -> Type[TM]:
        def mask_down(self: TN, descendant_type: Type[TM]):
            if descendant_type not in descendant_mask_types:
                raise TypeError(f'Cannot mask down "{descendant_type.get_type_name()}" to "{cls.get_type_name()}".')
            descendant_mask = descendant_type()
            self.parent.subtrees.replace(self, descendant_mask)
            descendant_mask.parent = self.parent
            return descendant_mask
        setattr(cls, 'mask_down', mask_down)
        def gdmt(_: Type[TN]) -> set[Type[TM]]:
            return descendant_mask_types
        setattr(cls, 'get_descendant_mask_types', classmethod(gdmt))
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