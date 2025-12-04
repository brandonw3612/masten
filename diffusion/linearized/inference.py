import torch
from torch import nn

from diffusion.linearized.io import load_model_checkpoint_for_inference
from diffusion.linearized.preserved_tokens import PreservedTokens
from diffusion.linearized.program_tokenizer import ProgramTokenizer


@torch.no_grad()
def generate(
        model: nn.Module,
        tokenizer: ProgramTokenizer,
        device: torch.device,
        temperature: float = 1,
        steps: int = 10, batch_size: int = 1
) -> list[list[str]]:
    model.eval()
    L = tokenizer.max_len
    pad_id = tokenizer.token_to_index[PreservedTokens.PAD]
    mask_id = tokenizer.token_to_index[PreservedTokens.MASK]

    # 1. initialize fully masked
    x_t = torch.full((batch_size, L), mask_id, device=device, dtype=torch.long)

    # denoise iteratively
    for step in range(steps):
        # time step t from 1.0 to 0.0
        t_val = 1.0 - (step / steps)
        t = torch.full((batch_size, 1), t_val, device=device)

        # prediction
        logits = model(x_t, t, pad_mask=None)
        logits = logits / temperature
        probs = torch.softmax(logits, dim=-1)

        sample_ids = torch.multinomial(probs.view(-1, tokenizer.vocab_size), num_samples=1)  # (1, L)
        sample_ids = sample_ids.view(batch_size, L)
        confidences = probs.gather(2, sample_ids.unsqueeze(-1)).squeeze(-1)

        num_to_keep = int(L * (step + 1) / steps)

        if step < steps - 1:
            threshold_index = torch.topk(confidences, num_to_keep).indices
            mask_indices = torch.ones_like(x_t, dtype=torch.bool)
            mask_indices.scatter_(1, threshold_index, False)

            x_t = sample_ids.clone()
            x_t[mask_indices] = mask_id
        else:
            x_t = sample_ids

    return [tokenizer.decode(x.tolist()) for x in x_t]


def inference(
        model_checkpoint_path: str,
        device: torch.device,
        steps: int = 10,
        batch_size: int = 1,
        temperature: float = 1.0
):
    tokenizer, model = load_model_checkpoint_for_inference(model_checkpoint_path, device)
    model.eval()
    generated_programs = generate(
        model=model,
        tokenizer=tokenizer,
        device=device,
        steps=steps,
        batch_size=batch_size,
        temperature=temperature
    )
    return generated_programs