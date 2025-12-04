class PreservedTokens:
    PAD = "<PAD>"
    MASK = "<MASK>"
    EOS = "<EOS>"

    @classmethod
    def all(cls):
        return [cls.PAD, cls.MASK, cls.EOS]