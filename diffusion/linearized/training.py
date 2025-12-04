from __future__ import annotations

import os

import torch
from torch import nn, optim
from torch.utils.data import DataLoader

from diffusion.linearized import LinearizedDataset, DiffusionTransformer, StructuredDiffusionLoss
from diffusion.linearized.io import load_model_checkpoint_for_training, save_model_checkpoint
from diffusion.linearized.preserved_tokens import PreservedTokens
from diffusion.linearized.program_tokenizer import ProgramTokenizer


def train_one_batch(
        model: nn.Module,
        batch_tokens: torch.Tensor,
        tokenizer: ProgramTokenizer,
        structure_loss: StructuredDiffusionLoss,
        optimizer: optim.Optimizer,
        device: torch.device
) -> float:
    model.train()

    x_start = batch_tokens.to(device)
    B, L = x_start.shape

    # 1. random sampling mask ratio: t ~ Uniform(0, 1)
    t = torch.rand(B, 1, device=device)

    # 2. generate mask matrix
    # mask where probability < t
    rand_matrix = torch.rand(B, L, device=device)
    mask_indices = rand_matrix < t

    # 3. construct noisy input
    mask_tid = tokenizer.token_to_index[PreservedTokens.MASK]
    x_noisy = x_start.clone()
    x_noisy[mask_indices] = mask_tid

    # 5. forward
    logits = model(x_noisy, t, pad_mask=None)

    # 6. compute loss where masked
    loss_fct = nn.CrossEntropyLoss(reduction='none')
    # flatten dimensions for loss computation
    ce_loss_raw = loss_fct(logits.view(-1, model.head.out_features), x_start.view(-1))
    ce_loss_raw = ce_loss_raw.view(B, L)

    # pad_tid = tokenizer.token_to_index[PreservedTokens.PAD]
    # eos_tid = tokenizer.token_to_index[PreservedTokens.EOS]
    # weights = torch.ones_like(ce_loss_raw)
    # weights[x_start == eos_tid] = 2.0
    # weights[x_start == pad_tid] = 0.5
    # ce_loss_raw = ce_loss_raw * weights

    # average loss only on masked positions
    masked_ce_loss = (ce_loss_raw * mask_indices.float()).sum() / (mask_indices.sum() + 1e-6)

    struct_loss = structure_loss(logits)

    total_loss = masked_ce_loss + struct_loss

    optimizer.zero_grad()
    total_loss.backward()
    optimizer.step()

    return total_loss.item()


def train(
        dataset: LinearizedDataset,
        model: DiffusionTransformer,
        optimizer: optim.Optimizer,
        structure_loss: StructuredDiffusionLoss,
        device: torch.device,
        epochs: int, batch_size: int,
        model_checkpoint_path: str
) -> None:
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    start_epoch = 0

    if os.path.exists(model_checkpoint_path):
        loaded_epoch = load_model_checkpoint_for_training(model_checkpoint_path, model, device, optimizer)
        start_epoch = loaded_epoch + 1

    for epoch in range(start_epoch, epochs):
        total_loss = 0
        for b_id, batch in enumerate(dataloader):
            loss = train_one_batch(model, batch, dataset.tokenizer, structure_loss, optimizer, device)
            total_loss += loss
            if b_id % 10 == 0:
                print(f"Epoch {epoch + 1} | Batch {b_id} | Loss: {loss:.4f}")
        avg_loss = total_loss / len(dataloader)
        print(f"\n======== Epoch {epoch + 1} completed. Average Loss: {avg_loss:.4f}\n")

        # Save checkpoint
        if (epoch + 1) % 1000 == 0:
            save_model_checkpoint(model, optimizer, dataset.tokenizer, epoch, model_checkpoint_path + f'x{epoch + 1}ep')

    save_model_checkpoint(model, optimizer, dataset.tokenizer, epochs, model_checkpoint_path + f'x{epochs}ep_final')