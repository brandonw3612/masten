from mast.node import MaskedNode

import langs.imp.base as base
import langs.imp.impl as impl


class AExprMask(MaskedNode, base.AExprBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.AExpr


class IdentifierMask(MaskedNode, base.IdentifierBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.Identifier


class IntLiteralMask(MaskedNode, base.IntLiteralBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.IntLiteral


class DivExprMask(MaskedNode, base.DivExprBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.DivExpr


class AddExprMask(MaskedNode, base.AddExprBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.AddExpr


class BracketedAExprMask(MaskedNode, base.BracketedAExprBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.BracketedAExpr


class BExprMask(MaskedNode, base.BExprBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.BExpr


class BoolLiteralMask(MaskedNode, base.BoolLiteralBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.BoolLiteral


class LeqExprMask(MaskedNode, base.LeqExprBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.LeqExpr


class NotExprMask(MaskedNode, base.NotExprBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.NotExpr


class LandExprMask(MaskedNode, base.LandExprBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.LandExpr


class BracketedBExprMask(MaskedNode, base.BracketedBExprBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.BracketedBExpr


class StmtMask(MaskedNode, base.StmtBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.Stmt


class AsnStmtMask(MaskedNode, base.AsnStmtBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.AsnStmt


class IfStmtMask(MaskedNode, base.IfStmtBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.IfStmt


class WhileStmtMask(MaskedNode, base.WhileStmtBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.WhileStmt


class BlockMask(MaskedNode, base.BlockBase):
    def __init__(self):
        super().__init__()
        self._node_type = impl.Block