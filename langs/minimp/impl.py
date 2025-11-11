from __future__ import annotations

from abc import abstractmethod
from typing import Any

from tree_sitter import Node as TNode

import mast.attr as attr
import mast.behavior as behavior
from mast.container import LabeledContainer
from mast.node import ConcreteNode, AbstractNode, RootNode

import langs.minimp.base as base


@attr.root_node()
@attr.node_type_name('Program')
@attr.tree_sitter_rule('source_file')
class Program(ConcreteNode, RootNode, base.ProgramBase):
    def __init__(self, body: base.AExprBase):
        super().__init__()
        self.subtrees = LabeledContainer[AbstractNode](['body'])
        self.subtrees['body'] = body
        body.parent = self

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            return None
        body: AExpr | None = AExpr.from_tsn(node.child(0))
        return cls(body)

    def body(self) -> AExpr:
        return self.subtrees['body']

    def to_source(self) -> str:
        return self.body().to_source()


@attr.node_type_name('A.Expr.')
@attr.tree_sitter_rule('_aexpr')
class AExpr(ConcreteNode, base.AExprBase):
    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type == IntLiteral.tree_sitter_rule():
            return IntLiteral.from_tsn(node)
        elif node.type == Identifier.tree_sitter_rule():
            return Identifier.from_tsn(node)
        elif node.type == DivExpr.tree_sitter_rule():
            return DivExpr.from_tsn(node)
        elif node.type == AddExpr.tree_sitter_rule():
            return AddExpr.from_tsn(node)
        elif node.type == BracketedAExpr.tree_sitter_rule():
            return BracketedAExpr.from_tsn(node)
        else:
            return None

    @abstractmethod
    def to_source(self) -> str:
        pass


@attr.node_type_name('Id')
@attr.tree_sitter_rule('id')
class Identifier(ConcreteNode, base.IdentifierBase):
    def __init__(self, name: str):
        super().__init__()
        self.attributes = LabeledContainer[Any](['name'])
        self.attributes['name'] = name

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            return None
        return cls(node.text.decode('utf-8'))

    def name(self):
        return self.attributes['name']

    def to_source(self) -> str:
        return self.name()


@attr.node_type_name('Int')
@attr.tree_sitter_rule('int')
class IntLiteral(ConcreteNode, base.IntLiteralBase):
    def __init__(self, value: int):
        super().__init__()
        self.attributes = LabeledContainer[Any](['value'])
        self.attributes['value'] = value

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            return None
        return cls(int(node.text))

    def value(self):
        return self.attributes['value']

    def to_source(self) -> str:
        return str(self.value())


@attr.node_type_name('Div.Exp.')
@attr.tree_sitter_rule('div_exp')
@behavior.can_binop_swap('left', 'right')
class DivExpr(ConcreteNode, base.DivExprBase):
    def __init__(self, left: base.AExprBase, right: base.AExprBase):
        super().__init__()
        self.subtrees = LabeledContainer[AbstractNode](['left', 'right'])
        self.subtrees['left'] = left
        self.subtrees['right'] = right
        left.parent = self
        right.parent = self

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            return None
        left: AExpr | None = AExpr.from_tsn(node.child(0))
        right: AExpr | None = AExpr.from_tsn(node.child(2))
        if left is None or right is None:
            return None
        return cls(left, right)

    def left(self):
        return self.subtrees['left']

    def right(self):
        return self.subtrees['right']

    def to_source(self) -> str:
        return f'{self.left().to_source()} / {self.right().to_source()}'


@attr.node_type_name('Add.Exp.')
@attr.tree_sitter_rule('add_exp')
@behavior.can_binop_swap('left', 'right')
class AddExpr(ConcreteNode, base.AddExprBase):
    def __init__(self, left: base.AExprBase, right: base.AExprBase):
        super().__init__()
        self.subtrees = LabeledContainer[AbstractNode](['left', 'right'])
        self.subtrees['left'] = left
        self.subtrees['right'] = right
        left.parent = self
        right.parent = self

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            return None
        left: AExpr | None = AExpr.from_tsn(node.child(0))
        right: AExpr | None = AExpr.from_tsn(node.child(2))
        if left is None or right is None:
            return None
        return cls(left, right)

    def left(self):
        return self.subtrees['left']

    def right(self):
        return self.subtrees['right']

    def to_source(self) -> str:
        return f'{self.left().to_source()} + {self.right().to_source()}'


@attr.node_type_name('Brc.A.Exp.')
@attr.tree_sitter_rule('brc_a_exp')
class BracketedAExpr(ConcreteNode, base.BracketedAExprBase):
    def __init__(self, expr: base.AExprBase):
        super().__init__()
        self.subtrees = LabeledContainer[AbstractNode](['expr'])
        self.subtrees['expr'] = expr
        expr.parent = self

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            return None
        expr: AExpr | None = AExpr.from_tsn(node.child(1))
        if expr is None:
            return None
        return cls(expr)

    def expr(self):
        return self.subtrees['expr']

    def to_source(self) -> str:
        return f'({self.expr().to_source()})'