from __future__ import annotations

import os

import torch
import torch.nn as nn
import torch.optim as optim

from diffusion.linearized import DiffusionTransformer
from diffusion.linearized.program_tokenizer import ProgramTokenizer


def save_model_checkpoint(
        model: DiffusionTransformer, optimizer: optim.Optimizer,
        tokenizer: ProgramTokenizer,
        epoch: int,
        filepath: str
) -> None:
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'embed_dim': model.embed_dim,
        'num_heads': model.num_heads,
        'num_layers': model.num_layers,
        'optimizer_state_dict': optimizer.state_dict(),
        'vocab': tokenizer.vocab,
        'max_len': tokenizer.max_len
    }
    if not filepath.endswith('.pt'):
        filepath += '.pt'
    torch.save(checkpoint, filepath)
    print(f"======== Checkpoint saved to {filepath} ========\n")


def load_model_checkpoint_for_training(
        filepath: str,
        model: nn.Module, device: torch.device,
        optimizer
) -> int:
    if not os.path.exists(filepath):
        print(f"No checkpoint found at {filepath}")
        return 0

    checkpoint = torch.load(filepath, map_location=device)

    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    epoch = checkpoint.get('epoch', 0)

    print(f"======== Checkpoint loaded from {filepath} (Epoch {epoch}) ========\n")
    return epoch


def load_model_checkpoint_for_inference(
        filepath: str,
        device: torch.device
) -> tuple[ProgramTokenizer, DiffusionTransformer] | None:
    if not os.path.exists(filepath):
        print(f"No checkpoint found at {filepath}")
        return None

    checkpoint = torch.load(filepath, map_location='cpu')

    vocab = checkpoint.get('vocab', [])
    max_len = checkpoint.get('max_len', 0)
    embed_dim = checkpoint.get('embed_dim', 128)
    num_heads = checkpoint.get('num_heads', 4)
    num_layers = checkpoint.get('num_layers', 2)

    tokenizer = ProgramTokenizer.from_vocab(vocab, max_len)
    model = DiffusionTransformer(len(vocab), max_len, embed_dim, num_heads, num_layers).to(device)

    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)

    print(f"======== Checkpoint loaded from {filepath} ========\n")
    return tokenizer, model