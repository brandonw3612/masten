from __future__ import annotations

from abc import abstractmethod
from typing import Any

from tree_sitter import Node as TNode

import mast.attr as attr
import mast.transition_kernel as behavior
from mast import Terminal
from mast.container import LabeledContainer, ChildrenContainer
from mast.node import ConcreteNode, AbstractNode, RootNode

import langs.imp.base as base
import langs.imp.mask as mask


@attr.is_root_node()
@attr.node_type_name('Program')
@attr.tree_sitter_rule('source_file')
@attr.is_non_terminal_node([mask.AExprMask])
class Program(ConcreteNode, RootNode, base.ProgramBase):
    def __init__(self, body: base.StmtBase):
        super().__init__()
        self.subtrees = LabeledContainer[AbstractNode](['body'])
        self.subtrees['body'] = body
        body.parent = self

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        body: Stmt | None = Stmt.from_tsn(node.child(0))
        if body is None:
            raise SyntaxError('Expected a valid statement')
        return cls(body)

    def body(self) -> AExpr:
        return self.subtrees['body']

    def to_tokens(self) -> list[str]:
        return self.body().to_tokens()

    def to_source(self) -> str:
        return self.body().to_source()


@attr.node_type_name('A.Expr.')
@attr.tree_sitter_rule('_aexpr')
class AExpr(ConcreteNode, base.AExprBase):
    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        for node_type in [IntLiteral, Identifier, DivExpr, AddExpr, BracketedAExpr]:
            if node.type == node_type.tree_sitter_rule():
                return node_type.from_tsn(node)
        raise SyntaxError(f'Unrecognized statement type: {node.type}')

    @abstractmethod
    def to_source(self) -> str:
        pass


@attr.node_type_name('Id')
@attr.tree_sitter_rule('id')
@attr.is_terminal_node(Terminal.IDENTIFIER)
class Identifier(ConcreteNode, base.IdentifierBase):
    def __init__(self, name: str):
        super().__init__()
        self.attributes = LabeledContainer[Any](['name'])
        self.attributes['name'] = name

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        return cls(node.text.decode('utf-8'))

    def name(self):
        return self.attributes['name']

    def to_tokens(self) -> list[str]:
        return [self.name()]

    def to_source(self) -> str:
        return self.name()


@attr.node_type_name('Int')
@attr.tree_sitter_rule('int')
@attr.is_terminal_node(Terminal.NUMBER)
class IntLiteral(ConcreteNode, base.IntLiteralBase):
    def __init__(self, value: int):
        super().__init__()
        self.attributes = LabeledContainer[Any](['value'])
        self.attributes['value'] = value

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        return cls(int(node.text))

    def value(self):
        return self.attributes['value']

    def to_tokens(self) -> list[str]:
        return [str(self.value())]

    def to_source(self) -> str:
        return str(self.value())


@attr.node_type_name('Div.Exp.')
@attr.tree_sitter_rule('div_exp')
@behavior.can_binop_swap('left', 'right')
@attr.is_non_terminal_node([mask.AExprMask, mask.AExprMask])
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
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        left: AExpr | None = AExpr.from_tsn(node.child(0))
        right: AExpr | None = AExpr.from_tsn(node.child(2))
        if left is None or right is None:
            raise SyntaxError('Expected 2 valid arithmatic expressions')
        return cls(left, right)

    def left(self):
        return self.subtrees['left']

    def right(self):
        return self.subtrees['right']

    def to_tokens(self) -> list[str]:
        return self.left().to_tokens() + ['/'] + self.right().to_tokens()

    def to_source(self) -> str:
        return f'{self.left().to_source()} / {self.right().to_source()}'


@attr.node_type_name('Add.Exp.')
@attr.tree_sitter_rule('add_exp')
@behavior.can_binop_swap('left', 'right')
@attr.is_non_terminal_node([mask.AExprMask, mask.AExprMask])
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
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        left: AExpr | None = AExpr.from_tsn(node.child(0))
        right: AExpr | None = AExpr.from_tsn(node.child(2))
        if left is None or right is None:
            raise SyntaxError('Expected 2 valid arithmatic expressions')
        return cls(left, right)

    def left(self):
        return self.subtrees['left']

    def right(self):
        return self.subtrees['right']

    def to_tokens(self) -> list[str]:
        return self.left().to_tokens() + ['+'] + self.right().to_tokens()

    def to_source(self) -> str:
        return f'{self.left().to_source()} + {self.right().to_source()}'


@attr.node_type_name('Brc.A.Exp.')
@attr.tree_sitter_rule('brc_a_exp')
@attr.is_non_terminal_node([mask.AExprMask])
class BracketedAExpr(ConcreteNode, base.BracketedAExprBase):
    def __init__(self, expr: base.AExprBase):
        super().__init__()
        self.subtrees = LabeledContainer[AbstractNode](['expr'])
        self.subtrees['expr'] = expr
        expr.parent = self

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        expr: AExpr | None = AExpr.from_tsn(node.child(1))
        if expr is None:
            raise SyntaxError('Expected a valid arithmatic expression')
        return cls(expr)

    def expr(self):
        return self.subtrees['expr']

    def to_tokens(self) -> list[str]:
        return ['('] + self.expr().to_tokens() + [')']

    def to_source(self) -> str:
        return f'({self.expr().to_source()})'


@attr.node_type_name('B.Expr.')
@attr.tree_sitter_rule('_bexpr')
class BExpr(ConcreteNode, base.BExprBase):
    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        for node_type in [BoolLiteral, LeqExpr, NotExpr, LandExpr, BracketedBExpr]:
            if node.type == node_type.tree_sitter_rule():
                return node_type.from_tsn(node)
        raise SyntaxError(f'Unrecognized statement type: {node.type}')

    @abstractmethod
    def to_source(self) -> str:
        pass


@attr.node_type_name('Bool')
@attr.tree_sitter_rule('bool')
# TODO: Terminal type not defined yet
class BoolLiteral(ConcreteNode, base.BoolLiteralBase):
    def __init__(self, value: int):
        super().__init__()
        self.attributes = LabeledContainer[Any](['value'])
        self.attributes['value'] = value

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        if node.text == 'true':
            return cls(True)
        if node.text == 'false':
            return cls(False)
        raise SyntaxError(f'Expected "true" or "false", but got {node.text}')

    def value(self):
        return self.attributes['value']

    def to_tokens(self) -> list[str]:
        return [str(self.value()).lower()]

    def to_source(self) -> str:
        return str(self.value())


@attr.node_type_name('L.Eq.Exp.')
@attr.tree_sitter_rule('leq_exp')
@behavior.can_binop_swap('left', 'right')
@attr.is_non_terminal_node([mask.BExprMask, mask.BExprMask])
class LeqExpr(ConcreteNode, base.LeqExprBase):
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
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        left: AExpr | None = AExpr.from_tsn(node.child(0))
        right: AExpr | None = AExpr.from_tsn(node.child(2))
        if left is None or right is None:
            raise SyntaxError('Expected 2 valid arithmatic expressions')
        return cls(left, right)

    def left(self):
        return self.subtrees['left']

    def right(self):
        return self.subtrees['right']

    def to_tokens(self) -> list[str]:
        return self.left().to_tokens() + ['<='] + self.right().to_tokens()

    def to_source(self) -> str:
        return f'{self.left().to_source()} <= {self.right().to_source()}'


@attr.node_type_name('Not.Exp.')
@attr.tree_sitter_rule('not_exp')
@attr.is_non_terminal_node([mask.BExprMask])
class NotExpr(ConcreteNode, base.NotExprBase):
    def __init__(self, expr: base.BExprBase):
        super().__init__()
        self.subtrees = LabeledContainer[AbstractNode](['expr'])
        self.subtrees['expr'] = expr
        expr.parent = self

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        expr: BExpr | None = BExpr.from_tsn(node.child(1))
        if expr is None:
            raise SyntaxError('Expected a valid boolean expression')
        return cls(expr)

    def expr(self):
        return self.subtrees['expr']

    def to_tokens(self) -> list[str]:
        return ['!'] + self.expr().to_tokens()

    def to_source(self) -> str:
        return f'!({self.expr().to_source()})'


@attr.node_type_name("L.And.Exp.")
@attr.tree_sitter_rule('land_exp')
@behavior.can_binop_swap('left', 'right')
@attr.is_non_terminal_node([mask.BExprMask])
class LandExpr(ConcreteNode, base.LandExprBase):
    def __init__(self, left: base.BExprBase, right: base.BExprBase):
        super().__init__()
        self.subtrees = LabeledContainer[AbstractNode](['left', 'right'])
        self.subtrees['left'] = left
        self.subtrees['right'] = right
        left.parent = self
        right.parent = self

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        left: BExpr | None = BExpr.from_tsn(node.child(0))
        right: BExpr | None = BExpr.from_tsn(node.child(2))
        if left is None or right is None:
            raise SyntaxError('Expected 2 valid boolean expressions')
        return cls(left, right)

    def left(self):
        return self.subtrees['left']

    def right(self):
        return self.subtrees['right']

    def to_tokens(self) -> list[str]:
        return self.left().to_tokens() + ['&&'] + self.right().to_tokens()

    def to_source(self) -> str:
        return f'{self.left().to_source()} <= {self.right().to_source()}'


@attr.node_type_name('Brc.B.Exp.')
@attr.tree_sitter_rule('brc_b_exp')
@attr.is_non_terminal_node([mask.BExprMask])
class BracketedBExpr(ConcreteNode, base.BracketedBExprBase):
    def __init__(self, expr: base.BExprBase):
        super().__init__()
        self.subtrees = LabeledContainer[AbstractNode](['expr'])
        self.subtrees['expr'] = expr
        expr.parent = self

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        expr: BExpr | None = BExpr.from_tsn(node.child(1))
        if expr is None:
            raise SyntaxError('Expected a valid boolean expression')
        return cls(expr)

    def expr(self):
        return self.subtrees['expr']

    def to_tokens(self) -> list[str]:
        return ['('] + self.expr().to_tokens() + [')']

    def to_source(self) -> str:
        return f'({self.expr().to_source()})'


@attr.node_type_name('Stmt.')
@attr.tree_sitter_rule('_stmt')
class Stmt(ConcreteNode, base.StmtBase):
    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        for node_type in [AsnStmt, IfStmt, WhileStmt, Block]:
            if node.type == node_type.tree_sitter_rule():
                return node_type.from_tsn(node)
        raise SyntaxError(f'Unrecognized statement type: {node.type}')

    @abstractmethod
    def to_source(self) -> str:
        pass


@attr.node_type_name('Asn.Stmt.')
@attr.tree_sitter_rule('asn_stmt')
@attr.is_non_terminal_node([mask.IdentifierMask, mask.StmtMask])
class AsnStmt(ConcreteNode, base.AsnStmtBase):
    def __init__(self, target: base.IdentifierBase, expr: base.AExprBase):
        super().__init__()
        self.subtrees = LabeledContainer[AbstractNode](['target', 'expr'])
        self.subtrees['target'] = target
        self.subtrees['expr'] = expr
        target.parent = self
        expr.parent = self

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        target: Identifier | None = Identifier.from_tsn(node.child(0))
        expr: AExpr | None = AExpr.from_tsn(node.child(2))
        if target is None or expr is None:
            raise SyntaxError('Expected a valid identifier and a valid arithmatic expression')
        return cls(target, expr)

    def target(self):
        return self.subtrees['target']

    def expr(self):
        return self.subtrees['expr']

    def to_tokens(self) -> list[str]:
        return self.target().to_tokens() + ['='] + self.expr().to_tokens() + [';']

    def to_source(self) -> str:
        return f'{self.target().to_source()} = {self.expr().to_source()};\n'


@attr.node_type_name('If.Stmt.')
@attr.tree_sitter_rule('if_stmt')
@attr.is_non_terminal_node([mask.BExprMask, mask.StmtMask, mask.StmtMask])
class IfStmt(ConcreteNode, base.IfStmtBase):
    def __init__(self, cond: base.BExprBase, body: base.StmtBase, else_body: base.StmtBase):
        super().__init__()
        self.subtrees = LabeledContainer[AbstractNode](['cond', 'body', 'else_body'])
        self.subtrees['cond'] = cond
        self.subtrees['body'] = body
        self.subtrees['else_body'] = else_body
        cond.parent = self
        body.parent = self
        else_body.parent = self

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        cond: BExpr | None = BExpr.from_tsn(node.child(2))
        body: Stmt | None = Stmt.from_tsn(node.child(4))
        else_body: Stmt | None = Stmt.from_tsn(node.child(6))
        if cond is None or body is None or else_body is None:
            raise SyntaxError('Expected a valid if-else structure: <condition> <body> <else-body>')
        return cls(cond, body, else_body)

    def cond(self):
        return self.subtrees['cond']

    def body(self):
        return self.subtrees['body']

    def else_body(self):
        return self.subtrees['else_body']

    def to_tokens(self) -> list[str]:
        tokens = ['if', '(', *self.cond().to_tokens(), ')']
        if isinstance(self.body(), base.BlockBase):
            tokens += self.body().to_tokens()
        else:
            tokens += ['{'] + self.body().to_tokens() + ['}']
        tokens += ['else']
        if isinstance(self.else_body(), base.BlockBase):
            tokens += self.else_body().to_tokens()
        else:
            tokens += ['{'] + self.else_body().to_tokens() + ['}']
        return tokens

    def to_source(self) -> str:
        s = f'if ({self.cond().to_source()}) '
        if isinstance(self.body(), base.BlockBase):
            s += self.body().to_source()
        else:
            s += f'{{\n{self.body().to_source()}}}'
        s += f' else '
        if isinstance(self.else_body(), base.BlockBase):
            s += self.else_body().to_source()
        else:
            s += f'{{\n{self.else_body().to_source()}}}'
        s += '\n'
        return s


@attr.node_type_name('While Stmt.')
@attr.tree_sitter_rule('while_stmt')
@attr.is_non_terminal_node([mask.BExprMask, mask.StmtMask])
class WhileStmt(ConcreteNode, base.WhileStmtBase):
    def __init__(self, cond: base.BExprBase, body: base.StmtBase):
        super().__init__()
        self.subtrees = LabeledContainer[AbstractNode](['cond', 'body'])
        self.subtrees['cond'] = cond
        self.subtrees['body'] = body
        cond.parent = self
        body.parent = self

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        cond: BExpr | None = BExpr.from_tsn(node.child(2))
        body: Stmt | None = Stmt.from_tsn(node.child(4))
        if cond is None or body is None:
            raise SyntaxError('Expected a valid while structure: <condition> <body>')
        return cls(cond, body)

    def cond(self):
        return self.subtrees['cond']

    def body(self):
        return self.subtrees['body']

    def to_tokens(self) -> list[str]:
        tokens = ['while', '(', *self.cond().to_tokens(), ')']
        if isinstance(self.body(), base.BlockBase):
            tokens += self.body().to_tokens()
        else:
            tokens += ['{'] + self.body().to_tokens() + ['}']
        return tokens

    def to_source(self) -> str:
        s = f'while ({self.cond().to_source()}) '
        if isinstance(self.body(), base.BlockBase):
            s += self.body().to_source()
        else:
            s += f'{{\n{self.body().to_source()}}}'
        s += '\n'
        return s


@attr.node_type_name('Block')
@attr.tree_sitter_rule('block')
# TODO: How to decorrupt a block?
class Block(ConcreteNode, base.BlockBase):
    def __init__(self, stmts: list[Stmt]):
        super().__init__()
        self.subtrees = ChildrenContainer()
        for stmt in stmts:
            self.subtrees.append(stmt)
            stmt.parent = self

    @classmethod
    def from_tsn(cls, node: TNode) -> ConcreteNode | None:
        if node.type != cls.tree_sitter_rule():
            raise SyntaxError(f'Expected {cls.tree_sitter_rule()}, but got {node.type}')
        stmts: list[Stmt] = []
        for child in node.children[1:-1]:
            stmt: Stmt | None = Stmt.from_tsn(child)
            if stmt is None:
                raise SyntaxError('Expected a valid statement')
            stmts.append(stmt)
        return cls(stmts)

    def child(self, i: int):
        return self.subtrees[i]

    def to_tokens(self) -> list[str]:
        tokens = ['{']
        for stmt in self.subtrees:
            tokens += stmt.to_tokens()
        tokens += ['}']
        return tokens

    def to_source(self) -> str:
        return '{\n' + ''.join(stmt.to_source() for stmt in self.subtrees) + '}'