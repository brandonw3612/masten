from diffusion.linearized.preserved_tokens import PreservedTokens


class ProgramTokenizer:
    def __init__(self, vocab: list[str], max_len: int) -> None:
        self.vocab = vocab
        self.vocab_size = len(self.vocab)
        self.token_to_index = {w: i for i, w in enumerate(self.vocab)}
        self.index_to_token = {i: w for i, w in enumerate(self.vocab)}
        self.max_len = max_len
        print(f'Total tokens: {self.vocab_size}, Max program length: {self.max_len}')

    @classmethod
    def from_programs(cls, programs: list[list[str]]) -> ProgramTokenizer:
        unique_tokens: set[str] = set()
        for program in programs:
            unique_tokens.update(program)
        sorted_tokens = sorted(unique_tokens)
        preserved_tokens: list[str] = PreservedTokens.all()
        vocab = preserved_tokens + sorted_tokens
        max_length = max(len(program) for program in programs) + 1  # +1 for <EOS>
        return cls(vocab, max_length)

    @classmethod
    def from_vocab(cls, vocab: list[str], max_len: int) -> ProgramTokenizer:
        return cls(vocab, max_len)

    def encode(self, p: list[str]) -> list[int]:
        ids = [self.token_to_index[token] for token in p]
        ids.append(self.token_to_index[PreservedTokens.EOS])
        if len(ids) < self.max_len:
            ids += [self.token_to_index[PreservedTokens.PAD]] * (self.max_len - len(ids))
        return ids

    def decode(self, ids: list[int]) -> list[str]:
        # eos_pos = ids.index(self.token_to_index[PreservedTokens.EOS])
        # ids = ids[:eos_pos]
        return [self.index_to_token[i] for i in ids]