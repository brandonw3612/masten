from mast.node import MaskedNode

import langs.minimp.base as base
import langs.minimp.impl as impl


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