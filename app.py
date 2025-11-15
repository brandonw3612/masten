from __future__ import annotations

import math

import langs.minimp as minimp
from diffusion.dumb import DumbDecorruptor, DumbDecorruptorConfig, DumbTerminalGenerator

dtg = DumbTerminalGenerator()

k = 0.25

def bracketed_dist(_: int) -> float:
    return 0

def non_terminal_dist(depth: int) -> float:
    return 1 - math.tanh(depth * k)

def terminal_dist(depth: int) -> float:
    return math.tanh(depth * k)

ddc = DumbDecorruptorConfig({
    minimp.AExprMask: {
        minimp.AddExprMask: non_terminal_dist,
        minimp.DivExprMask: non_terminal_dist,
        minimp.BracketedAExprMask: bracketed_dist,
        minimp.IdentifierMask: terminal_dist,
        minimp.IntLiteralMask: terminal_dist
    }
})

dd = DumbDecorruptor(ddc, dtg)

def fix(n: minimp.Program | minimp.base.AExprBase):
    if isinstance(n, minimp.Program):
        fix(n.body())
        return
    if isinstance(n, minimp.AddExpr):
        fix(n.left())
        fix(n.right())
        return
    if isinstance(n, minimp.DivExpr):
        fix(n.left())
        fix(n.right())
        if isinstance(n.left(), minimp.AddExpr):
            n.subtrees.replace(n.left(), minimp.BracketedAExpr(n.left()))
        elif isinstance(n.right(), minimp.AddExpr) or isinstance(n.right(), minimp.DivExpr):
            n.subtrees.replace(n.right(), minimp.BracketedAExpr(n.right()))
        return

for _ in range(100):
    body = minimp.AExprMask()
    program = minimp.Program(body)
    dd.decorrupt(body)
    fix(program)
    print(program.to_source())