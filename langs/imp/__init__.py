from .impl import *
from .mask import *

import mast.transition_kernel as behavior

# connect masked node types and concrete node types
for node_type, mask_type in [
    [AExpr, AExprMask],
    [Identifier, IdentifierMask],
    [IntLiteral, IntLiteralMask],
    [DivExpr, DivExprMask],
    [AddExpr, AddExprMask],
    [BracketedAExpr, BracketedAExprMask],
    [BExpr, BExprMask],
    [BoolLiteral, BoolLiteralMask],
    [LeqExpr, LeqExprMask],
    [NotExpr, NotExprMask],
    [LandExpr, LandExprMask],
    [BracketedBExpr, BracketedBExprMask],
    [Stmt, StmtMask],
    [AsnStmt, AsnStmtMask],
    [IfStmt, IfStmtMask],
    [WhileStmt, WhileStmtMask],
    [Block, BlockMask]
]:
    behavior.kernel_mask(mask_type)(node_type)
    behavior.kernel_unmask(node_type)(mask_type)

# apply masked node type hierarchy
behavior.kernel_mask_up([AExprMask])(IdentifierMask)
behavior.kernel_mask_up([AExprMask])(IntLiteralMask)
behavior.kernel_mask_up([AExprMask])(DivExprMask)
behavior.kernel_mask_up([AExprMask])(AddExprMask)
behavior.kernel_mask_up([AExprMask])(BracketedAExprMask)
behavior.kernel_mask_down([IdentifierMask, IntLiteralMask, DivExprMask, AddExprMask, BracketedAExprMask])(AExprMask)
behavior.kernel_mask_up([BExprMask])(BoolLiteralMask)
behavior.kernel_mask_up([BExprMask])(LeqExprMask)
behavior.kernel_mask_up([BExprMask])(NotExprMask)
behavior.kernel_mask_up([BExprMask])(LandExprMask)
behavior.kernel_mask_up([BExprMask])(BracketedBExprMask)
behavior.kernel_mask_down([BoolLiteralMask, LeqExprMask, NotExprMask, LandExprMask, BracketedBExprMask])(BExprMask)
behavior.kernel_mask_up([StmtMask])(AsnStmtMask)
behavior.kernel_mask_up([StmtMask])(IfStmtMask)
behavior.kernel_mask_up([StmtMask])(WhileStmtMask)
behavior.kernel_mask_up([StmtMask])(BlockMask)
behavior.kernel_mask_down([AsnStmtMask, IfStmtMask, WhileStmtMask, BlockMask])(StmtMask)

__all__ = [
    'Program',
    'AExpr', 'AExprMask',
    'Identifier', 'IdentifierMask',
    'IntLiteral', 'IntLiteralMask',
    'DivExpr', 'DivExprMask',
    'AddExpr', 'AddExprMask',
    'BracketedAExpr', 'BracketedAExprMask',
    'BExpr', 'BExprMask',
    'BoolLiteral', 'BoolLiteralMask',
    'LeqExpr', 'LeqExprMask',
    'NotExpr', 'NotExprMask',
    'LandExpr', 'LandExprMask',
    'BracketedBExpr', 'BracketedBExprMask',
    'Stmt', 'StmtMask',
    'AsnStmt', 'AsnStmtMask',
    'IfStmt', 'IfStmtMask',
    'WhileStmt', 'WhileStmtMask',
    'Block', 'BlockMask'
]