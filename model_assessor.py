from __future__ import annotations

import argparse, json
from typing import Any, Generator

import torch
import diffusion.linearized as dl
import langs.minimp as minimp
from tree_sitter import Parser, Language
from parsers import tree_sitter_minimp

def depth(n: minimp.Program | minimp.base.AExprBase) -> int:
    if isinstance(n, minimp.Program):
        return depth(n.body())
    if isinstance(n, minimp.AddExpr) or isinstance(n, minimp.DivExpr):
        return max(depth(n.left()), depth(n.right())) + 1
    if isinstance(n, minimp.BracketedAExpr):
        return depth(n.expr()) + 1
    return 1

def count_node_type(n: minimp.Program | minimp.base.AExprBase, result: dict):
    if isinstance(n, minimp.Program):
        count_node_type(n.body(), result)
        return
    result[n.get_type_name()] = result.get(n.get_type_name(), 0) + 1
    if isinstance(n, minimp.AddExpr) or isinstance(n, minimp.DivExpr):
        count_node_type(n.left(), result)
        count_node_type(n.right(), result)
        return
    if isinstance(n, minimp.BracketedAExpr):
        count_node_type(n.expr(), result)
        return

def sample_from_dataset(path: str) -> Generator[str, Any, None]:
    ds = dl.LinearizedDataset.from_checkpoint(path)
    for s in ds.samples:
        p = ds.tokenizer.decode(s.tolist())
        eos_pos = p.index('<EOS>')
        p = p[:eos_pos]
        yield str.join(' ', p)

def sample_from_model(path: str, steps: int, bs: int, temp: float) -> Generator[str, Any, None]:
    device = torch.accelerator.current_accelerator()
    g = dl.inference(path, device, steps=steps, batch_size=bs, temperature=temp)
    for prog in g:
        if '<EOS>' in prog:
            eos_pos = prog.index('<EOS>')
            prog = prog[:eos_pos]
        src = str.join(' ', [t for t in prog if t != '<PAD>'])
        yield src

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str)
    parser.add_argument('--dataset', type=str)
    parser.add_argument('--steps', type=int, default=20)
    parser.add_argument('--batch-size', type=int, default=10)
    parser.add_argument('--temperature', type=float, default=1.0)
    parser.add_argument('--log', type=str, required=True)
    args = parser.parse_args()

    if args.model:
        samples = sample_from_model(args.model, args.steps, args.batch_size, args.temperature)
    elif args.dataset:
        samples = sample_from_dataset(args.dataset)
    else:
        raise ValueError('Either --model or --dataset must be specified')

    parser = Parser(Language(tree_sitter_minimp.language()))

    depths = dict()
    node_type_dist = dict()

    for s in samples:
        try:
            tree = parser.parse(bytes(s, 'utf-8'))
            program: minimp.Program | None = minimp.Program.from_tree_sitter(tree)
            d = depth(program)
            depths[d] = depths.get(d, 0) + 1
            count_node_type(program, node_type_dist)
        except:
            depths[-1] = depths.get(-1, 0) + 1

    logs = dict()
    if args.model:
        logs['model'] = args.model
    elif args.dataset:
        logs['dataset'] = args.dataset
    logs['parse_rate'] = 1 - depths.get(-1, 0) / sum(depths.values())
    if -1 in depths.keys():
        depths.pop(-1)
    logs['avg_depth'] = sum([d * n for d, n in depths.items()]) / sum(depths.values())
    logs['depth_dist'] = depths
    logs['node_type_dist'] = node_type_dist
    with open(args.log, 'w') as f:
        f.write(json.dumps(logs, indent=4))