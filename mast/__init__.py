from enum import Enum


class Corruption(Enum):
    MASK = 1
    UNMASK = 2
    MASK_UP = 3
    MASK_DOWN = 4
    BINOP_SWAP = 5