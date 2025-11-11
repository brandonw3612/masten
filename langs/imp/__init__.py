from .impl import *
from .mask import *

import mast.behavior as behavior

# connect masked node types and concrete node types
for node_type, mask_type in [
    [AExpr, AExprMask],
    [Identifier, IdentifierMask],
    [IntLiteral, IntLiteralMask],
    [DivExpr, DivExprMask],
    [AddExpr, AddExprMask],
    [BracketedAExpr, BracketedAExprMask]
]:
    behavior.can_mask(mask_type)(node_type)
    behavior.can_unmask(node_type)(mask_type)

# apply masked node type hierarchy
behavior.can_mask_up([AExprMask])(IdentifierMask)
behavior.can_mask_up([AExprMask])(IntLiteralMask)
behavior.can_mask_up([AExprMask])(DivExprMask)
behavior.can_mask_up([AExprMask])(AddExprMask)
behavior.can_mask_up([AExprMask])(BracketedAExprMask)
behavior.can_mask_down([IdentifierMask, IntLiteralMask, DivExprMask, AddExprMask, BracketedAExprMask])(AExprMask)

__all__ = [
    'Program',
    'AExpr', 'AExprMask',
    'Identifier', 'IdentifierMask',
    'IntLiteral', 'IntLiteralMask',
    'DivExpr', 'DivExprMask',
    'AddExpr', 'AddExprMask',
    'BracketedAExpr', 'BracketedAExprMask'
]