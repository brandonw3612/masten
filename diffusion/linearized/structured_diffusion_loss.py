import torch
import torch.nn as nn
import torch.nn.functional as F

class StructuredDiffusionLoss(nn.Module):
    def __init__(self,
                 eos_id: int, pad_id: int,
                 lambda_struct: float = 1.0
                 ) -> None:
        super().__init__()
        self.eos_id = eos_id
        self.pad_id = pad_id
        self.lambda_struct = lambda_struct

    def forward(self, logits):
        # prob dist
        probs = F.softmax(logits, dim=-1)
        p_eos = probs[:, :, self.eos_id]
        p_pad = probs[:, :, self.pad_id]

        # Transition constraint
        # cumulative eos probability
        cum_p_eos = torch.cumsum(p_eos, dim=-1)
        no_eos_yet = F.relu(1.0 - cum_p_eos)
        # (already) terminated here: current == eos or pad
        p_cur_term = p_eos[:, :-1] + p_pad[:, :-1]
        # next is not pad
        p_next_not_pad = 1.0 - p_pad[:, 1:]

        # no pads before eos
        loss_order = torch.mean(p_pad * no_eos_yet)

        # penalty: (already) terminated here * next is not pad
        loss_trans = torch.mean(p_cur_term * p_next_not_pad)

        # count constraint: we expect eos appears exactly once
        eos_count_expected = torch.sum(p_eos, dim=-1)
        loss_count = F.mse_loss(eos_count_expected, torch.ones_like(eos_count_expected))

        return self.lambda_struct * (loss_order + loss_trans + loss_count)