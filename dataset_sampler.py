from __future__ import annotations

import string, math, argparse

import diffusion.linearized as dl
from diffusion.dumb import DumbTerminalGenerator, DumbDecorruptorConfig, DumbDecorruptor
from langs import minimp


k = 0.15


def bracketed_dist(_1: int) -> float:
    return 0


def non_terminal_dist(_depth: int) -> float:
    return 1 - math.tanh(_depth * k)


def terminal_dist(_depth: int) -> float:
    return math.tanh(_depth * k)


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


def depth(n: minimp.Program | minimp.base.AExprBase) -> int:
    if isinstance(n, minimp.Program):
        return depth(n.body())
    if isinstance(n, minimp.AddExpr) or isinstance(n, minimp.DivExpr):
        return max(depth(n.left()), depth(n.right())) + 1
    if isinstance(n, minimp.BracketedAExpr):
        return depth(n.expr()) + 1
    return 1


def sample_dataset(
        dataset_size: int,
        depth_lim: tuple[int, int] = (1, -1),
        alphabet: str = string.ascii_lowercase,
        max_int: int = 10
) -> dl.LinearizedDataset:

    min_depth, max_depth = depth_lim

    dtg = DumbTerminalGenerator(alphabet, (0, max_int))

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

    raw_programs: list[minimp.Program] = []

    while True:
        if len(raw_programs) >= dataset_size:
            break
        body = minimp.AExprMask()
        program = minimp.Program(body)
        dd.decorrupt(body)
        # fix(program)
        if min_depth > depth(program) or depth(program) > max_depth:
            continue
        raw_programs.append(program)

    return dl.LinearizedDataset.from_raw_samples([p.to_tokens() for p in raw_programs])


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Dataset Sampler')
    parser.add_argument('--dataset-size', type=int, default=10000)
    parser.add_argument('--min-depth', type=int, default=1)
    parser.add_argument('--max-depth', type=int, default=-1)
    parser.add_argument('--alphabet', type=str, default=string.ascii_lowercase)
    parser.add_argument('--max-int', type=int, default=10)
    parser.add_argument('--output', type=str, default=None)
    args = parser.parse_args()
    dataset = sample_dataset(args.dataset_size, (args.min_depth, args.max_depth), args.alphabet, args.max_int)
    if args.output is not None:
        dataset.save_checkpoint(args.output)