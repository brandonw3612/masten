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
    behavior.can_mask(mask_type)(node_type)
    behavior.can_unmask(node_type)(mask_type)

# apply masked node type hierarchy
behavior.can_mask_up([AExprMask])(IdentifierMask)
behavior.can_mask_up([AExprMask])(IntLiteralMask)
behavior.can_mask_up([AExprMask])(DivExprMask)
behavior.can_mask_up([AExprMask])(AddExprMask)
behavior.can_mask_up([AExprMask])(BracketedAExprMask)
behavior.can_mask_down([IdentifierMask, IntLiteralMask, DivExprMask, AddExprMask, BracketedAExprMask])(AExprMask)
behavior.can_mask_up([BExprMask])(BoolLiteralMask)
behavior.can_mask_up([BExprMask])(LeqExprMask)
behavior.can_mask_up([BExprMask])(NotExprMask)
behavior.can_mask_up([BExprMask])(LandExprMask)
behavior.can_mask_up([BExprMask])(BracketedBExprMask)
behavior.can_mask_down([BoolLiteralMask, LeqExprMask, NotExprMask, LandExprMask, BracketedBExprMask])(BExprMask)
behavior.can_mask_up([StmtMask])(AsnStmtMask)
behavior.can_mask_up([StmtMask])(IfStmtMask)
behavior.can_mask_up([StmtMask])(WhileStmtMask)
behavior.can_mask_up([StmtMask])(BlockMask)
behavior.can_mask_down([AsnStmtMask, IfStmtMask, WhileStmtMask, BlockMask])(StmtMask)

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