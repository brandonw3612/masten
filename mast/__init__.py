from enum import Enum


class TransitionKernels(Enum):
    MASK = 1
    UNMASK = 2
    MASK_UP = 3
    MASK_DOWN = 4
    BINOP_SWAP = 5

class Terminal(Enum):
    IDENTIFIER = 1
    NUMBER = 2
    STRING = 3