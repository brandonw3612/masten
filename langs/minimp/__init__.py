from .impl import *
from .mask import *

import mast.transition_kernel as tk

# connect masked node types and concrete node types
tk.kernel_mask(AExprMask)(AExpr)
for node_type, mask_type in [
    [Identifier, IdentifierMask],
    [IntLiteral, IntLiteralMask],
    [DivExpr, DivExprMask],
    [AddExpr, AddExprMask],
    [BracketedAExpr, BracketedAExprMask]
]:
    tk.kernel_mask(mask_type)(node_type)
    tk.kernel_unmask(node_type)(mask_type)

# apply masked node type hierarchy
tk.kernel_mask_up([AExprMask])(IdentifierMask)
tk.kernel_mask_up([AExprMask])(IntLiteralMask)
tk.kernel_mask_up([AExprMask])(DivExprMask)
tk.kernel_mask_up([AExprMask])(AddExprMask)
tk.kernel_mask_up([AExprMask])(BracketedAExprMask)
tk.kernel_mask_down([IdentifierMask, IntLiteralMask, DivExprMask, AddExprMask, BracketedAExprMask])(AExprMask)

__all__ = [
    'Program',
    'AExpr', 'AExprMask',
    'Identifier', 'IdentifierMask',
    'IntLiteral', 'IntLiteralMask',
    'DivExpr', 'DivExprMask',
    'AddExpr', 'AddExprMask',
    'BracketedAExpr', 'BracketedAExprMask'
]