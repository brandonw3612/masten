import random
import string
from collections.abc import Callable
from queue import Queue
from typing import TypeVar, Type, Any

from diffusion.decorruptor import Decorruptor
from diffusion.terminal_generator import TerminalGenerator
from mast import TransitionKernels as TK
from mast import Terminal
from mast.node import MaskedNode, AbstractNode, ConcreteNode

TMN = TypeVar('TMN', bound='MaskedNode')
TMN2 = TypeVar('TMN2', bound='MaskedNode')


class DumbDecorruptorConfig:
    def __init__(
            self,
            mask_down_weights: dict[Type[TMN], dict[Type[TMN2], Callable[[int], float]]]
    ):
        self.allowed_transition_kernels = {TK.UNMASK, TK.MASK_DOWN}
        self.mask_down_weights = mask_down_weights


class DumbDecorruptor(Decorruptor):
    def __init__(self, config: DumbDecorruptorConfig, tg: TerminalGenerator):
        self.config = config
        self.tg = tg

    def decorrupt(self, tree: AbstractNode):
        if not isinstance(tree, MaskedNode):
            raise ValueError(f'Expected an instance of MaskedNode, got {type(tree)}')
        q: Queue[tuple[int, MaskedNode]] = Queue()
        q.put((1, tree))
        while not q.empty():
            depth, n = q.get()
            tks = n.get_supported_transition_kernels().intersection(self.config.allowed_transition_kernels)
            if len(tks) == 0:
                continue
            if len(tks) > 1:
                raise ValueError(f'Multiple transition kernels supported for node type {n.get_type_name()}: {tks}')
            tk = [t for t in tks][0]
            if tk == TK.UNMASK:
                concrete_node = self.decorrupt_unmask(n)
                for _, c in concrete_node.enumerate_nodes():
                    if isinstance(c, MaskedNode):
                        q.put((depth + 1, c))
            elif tk == TK.MASK_DOWN:
                masked_node = self.decorrupt_mask_down(n, depth)
                q.put((depth, masked_node))

    def decorrupt_unmask(self, node: MaskedNode) -> ConcreteNode:
        if not hasattr(type(node), 'unmask') or not hasattr(type(node), 'unmask_target'):
            raise ValueError(f'Node type {node.get_type_name()} does not support UNMASK.')
        concrete_type = type(node).unmask_target()
        if hasattr(concrete_type, 'create_empty'):
            return node.unmask(concrete_type.create_empty())
        if hasattr(concrete_type, 'get_terminal_type'):
            terminal_type: Terminal = concrete_type.get_terminal_type()
            terminal = self.tg.generate(None, terminal_type)
            return node.unmask(concrete_type(terminal))
        raise TypeError(f'Cannot unmask node of type {node.get_type_name()} to {concrete_type.get_type_name()}: Concrete node is neither a terminal nor non-terminal.')

    def decorrupt_mask_down(self, node: MaskedNode, depth: int) -> MaskedNode:
        if not hasattr(type(node), 'mask_down') or not hasattr(type(node), 'get_descendant_mask_types'):
            raise ValueError(f'Node type {node.get_type_name()} does not support MASK_DOWN.')
        if type(node) in self.config.mask_down_weights:
            weights = self.config.mask_down_weights[type(node)]
        else:
            # print(f'Warning: no mask-down weights specified for node type {type(node)}')
            possible_descendants: set[Type[TMN]] = type(node).get_descendant_mask_types()
            def default_weight(_: int) -> float:
                return 1.0
            weights = {d: default_weight for d in possible_descendants}
        weights = {d: w(depth) for d, w in weights.items()}
        sum_weights = sum(weights.values())
        weights = {d: w / sum_weights for d, w in weights.items()}
        # print(f'On depth {depth}, weights of mask-down for {type(node)}:\n{weights}')
        rand = random.random()
        for d, w in weights.items():
            if rand <= w:
                return node.mask_down(d)
            rand -= w
        raise ValueError(f'Failed to mask down node of type {type(node)}')


class DumbTerminalGenerator(TerminalGenerator):
    def generate(self, ctx: Any, task_type: Terminal) -> Any:
        if task_type == Terminal.IDENTIFIER:
            return random.choice(string.ascii_lowercase)
        if task_type == Terminal.STRING:
            return random.choice(string.ascii_lowercase)
        if task_type == Terminal.NUMBER:
            return random.randint(0, 100)
        raise ValueError(f'Unsupported terminal type: {task_type}')