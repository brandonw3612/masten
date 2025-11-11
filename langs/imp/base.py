from abc import ABC

from mast.node import AbstractNode


class ProgramBase(AbstractNode, ABC):
    pass


class AExprBase(AbstractNode, ABC):
    pass


class IdentifierBase(AExprBase, ABC):
    pass


class IntLiteralBase(AExprBase, ABC):
    pass


class DivExprBase(AExprBase, ABC):
    pass


class AddExprBase(AExprBase, ABC):
    pass


class BracketedAExprBase(AExprBase, ABC):
    pass


class BExprBase(AbstractNode, ABC):
    pass


class BoolLiteralBase(BExprBase, ABC):
    pass


class LeqExprBase(BExprBase, ABC):
    pass


class NotExprBase(BExprBase, ABC):
    pass


class LandExprBase(BExprBase, ABC):
    pass


class BracketedBExprBase(BExprBase, ABC):
    pass


class StmtBase(AbstractNode, ABC):
    pass


class AsnStmtBase(StmtBase, ABC):
    pass


class IfStmtBase(StmtBase, ABC):
    pass


class WhileStmtBase(StmtBase, ABC):
    pass


class BlockBase(StmtBase, ABC):
    pass