from __future__ import annotations

import argparse, json, os
from typing import Any, Generator
from datetime import datetime

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

def sample_from_dataset(path: str) -> Generator[tuple[str, int], Any, None]:
    ds = dl.LinearizedDataset.from_checkpoint(path)
    for s in ds.samples:
        p = ds.tokenizer.decode(s.tolist())
        eos_pos = p.index('<EOS>')
        p = p[:eos_pos]
        yield str.join(' ', p), len(p)

def sample_from_model(path: str, steps: int, bs: int, temp: float) -> Generator[tuple[str, int], Any, None]:
    device = torch.accelerator.current_accelerator()
    g = dl.inference(path, device, steps=steps, batch_size=bs, temperature=temp)
    for prog in g:
        if '<EOS>' in prog:
            eos_pos = prog.index('<EOS>')
            prog = prog[:eos_pos]
        prog = [t for t in prog if t != '<PAD>']
        src = str.join(' ', prog)
        yield src, len(prog)


def assess_dataset(cp_path: str, parser: Parser) -> dict:
    samples = sample_from_dataset(cp_path)

    depths = dict()
    lens = 0
    node_type_dist = dict()
    for s, l in samples:
        tree = parser.parse(bytes(s, 'utf-8'))
        program: minimp.Program | None = minimp.Program.from_tree_sitter(tree)
        lens += l
        d = depth(program)
        depths[d] = depths.get(d, 0) + 1
        count_node_type(program, node_type_dist)
    total_count = sum(depths.values())

    logs = dict()
    logs['size'] = total_count
    logs['avg_depth'] = sum([d * n for d, n in depths.items()]) / total_count
    logs['avg_len'] = lens / total_count
    logs['depth_dist'] = depths
    logs['node_type_dist'] = node_type_dist

    return logs


def assess_model(cp_path: str, parser: Parser, batch_size: int, steps: int = 20, temperature: float = 1.0) -> dict:
    samples = sample_from_model(cp_path, steps, batch_size, temperature)

    depths = dict()
    node_type_dist = dict()
    gen_src = set()
    lens = 0

    for s, l in samples:
        try:
            tree = parser.parse(bytes(s, 'utf-8'))
            program: minimp.Program | None = minimp.Program.from_tree_sitter(tree)
            lens += l
            d = depth(program)
            gen_src.add(program.to_source())
            depths[d] = depths.get(d, 0) + 1
            count_node_type(program, node_type_dist)
        except:
            depths[-1] = depths.get(-1, 0) + 1

    logs = dict()
    logs['parse_rate'] = 1 - depths.get(-1, 0) / sum(depths.values())
    if -1 in depths.keys():
        depths.pop(-1)
    total_count = sum(depths.values())
    logs['diversity'] = len(gen_src) / total_count if total_count > 0 else 0
    logs['avg_depth'] = sum([d * n for d, n in depths.items()]) / total_count if total_count > 0 else 0
    logs['avg_len'] = lens / total_count if total_count > 0 else 0
    logs['depth_dist'] = depths
    logs['node_type_dist'] = node_type_dist

    return logs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifacts', type=str, required=True)
    parser.add_argument('--logs', type=str, required=True)
    parser.add_argument('--steps', type=int, default=20)
    parser.add_argument('--batch-size', type=int, default=10)
    parser.add_argument('--temperature', type=float, default=1.0)
    args = parser.parse_args()

    parser = Parser(Language(tree_sitter_minimp.language()))

    if not os.path.isdir(args.artifacts) or not os.path.isdir(args.logs):
        raise ValueError('Invalid artifacts or logs directory')

    logs_root = os.path.join(args.logs, datetime.now().strftime('%Y%m%d_%H%M%S'))
    os.mkdir(logs_root)

    for dataset in os.listdir(args.artifacts):
        ds_root = os.path.join(args.artifacts, dataset)
        ds_logs_root = os.path.join(logs_root, dataset)
        os.mkdir(ds_logs_root)

        dataset_cp = os.path.join(ds_root, 'dataset.pt')
        if not os.path.isfile(dataset_cp):
            continue

        print(f'Assessing dataset {dataset}')
        result = assess_dataset(dataset_cp, parser)
        with open(os.path.join(ds_logs_root, 'dataset.log'), 'w') as f:
            f.write(json.dumps(result, indent=4))
        print(f'Dataset {dataset}: assessment completed')

        for model in os.listdir(ds_root):
            model_root = os.path.join(ds_root, model)
            if not os.path.isdir(model_root):
                continue
            model_logs_root = os.path.join(ds_logs_root, model)
            os.mkdir(model_logs_root)
            print(f'Assessing model {model}')
            for epoch in os.listdir(model_root):
                print(f'Assessing epoch {epoch}')
                model_cp = os.path.join(model_root, epoch)
                result = assess_model(model_cp, parser, args.batch_size, args.steps, args.temperature)
                epoch_log = os.path.join(model_logs_root, epoch.replace('.pt', '.log'))
                with open(epoch_log, 'w') as f:
                    f.write(json.dumps(result, indent=4))
                print(f'Epoch {epoch} assessment completed')
            print(f'Model {model}: assessment completed')