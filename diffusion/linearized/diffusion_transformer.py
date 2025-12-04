import torch
import torch.nn as nn


class DiffusionTransformer(nn.Module):
    def __init__(self, vocab_size, max_len, embed_dim=128, num_heads=4, num_layers=10):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.num_layers = num_layers

        self.token_emb = nn.Embedding(vocab_size, embed_dim)
        self.pos_emb = nn.Embedding(max_len, embed_dim)

        self.time_emb = nn.Linear(1, embed_dim)

        encoder_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=num_heads, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.head = nn.Linear(embed_dim, vocab_size)

        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(module):
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=0.02)
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=0.02)

    def forward(self, x, t, pad_mask=None):
        seq_len = x.size(1)
        pos = torch.arange(seq_len, device=x.device).unsqueeze(0)

        if t.dim() == 1:
            t = t.unsqueeze(1)

        # token embedding + position embedding + time embedding
        h = self.token_emb(x) + self.pos_emb(pos) + self.time_emb(t).unsqueeze(1)

        output = self.transformer(h, src_key_padding_mask=pad_mask)

        return self.head(output)