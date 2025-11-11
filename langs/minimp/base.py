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