import torch
from torch import Tensor
from torch.utils.data import Dataset

from diffusion.linearized.program_tokenizer import ProgramTokenizer


class LinearizedDataset(Dataset):
    def __init__(self, tokenizer: ProgramTokenizer, samples: list[Tensor]) -> None:
        self.tokenizer = tokenizer
        self.samples = samples

    @classmethod
    def from_raw_samples(cls, raw_samples: list[list[str]]) -> LinearizedDataset:
        tokenizer = ProgramTokenizer.from_programs(raw_samples)
        samples = [torch.tensor(tokenizer.encode(sample)) for sample in raw_samples]
        return cls(tokenizer, samples)

    def to(self, device: torch.device) -> LinearizedDataset:
        return LinearizedDataset(
            self.tokenizer, [sample.to(device) for sample in self.samples]
        )

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> torch.Tensor:
        return self.samples[idx]

    def save_checkpoint(self, filepath: str) -> None:
        torch.save({
            'vocab': self.tokenizer.vocab,
            'max_len': self.tokenizer.max_len,
            'samples': self.samples
        }, filepath)
        print(f"======== Dataset checkpoint saved to {filepath}")

    @classmethod
    def from_checkpoint(cls, filepath: str) -> LinearizedDataset:
        checkpoint = torch.load(filepath)
        tokenizer = ProgramTokenizer.from_vocab(
            checkpoint['vocab'],
            checkpoint['max_len']
        )
        samples = checkpoint['samples']
        print(f"======== Dataset checkpoint loaded from {filepath}")
        return cls(tokenizer, samples)