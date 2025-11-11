import graphviz

from mast.node import AbstractNode
from queue import Queue


def check_equivalence(t1: AbstractNode, t2: AbstractNode) -> bool:
    if t1.get_type_name() != t2.get_type_name():
        return False
    attrs = zip(t1.enumerate_attributes(), t2.enumerate_attributes())
    for (attr_name_1, attr_value_1), (attr_name_2, attr_value_2) in attrs:
        if attr_name_1 != attr_name_2:
            return False
        if attr_value_1 != attr_value_2:
            return False
    en1 = t1.enumerate_nodes()
    en2 = t2.enumerate_nodes()
    if len(en1) != len(en2):
        return False
    for (node_attr_1, nodes_1), (node_attr_2, nodes_2) in zip(en1, en2):
        if node_attr_1 != node_attr_2:
            return False
        if not isinstance(nodes_1, list):
            nodes_1 = [nodes_1]
        if not isinstance(nodes_2, list):
            nodes_2 = [nodes_2]
        if len(nodes_1) != len(nodes_2):
            return False
        for n1, n2 in zip(nodes_1, nodes_2):
            if not check_equivalence(n1, n2):
                return False
    return True


def get_node_label(node: AbstractNode):
    label = f'[{node.get_type_name()}]'
    for attr_name, attr_value in node.enumerate_attributes():
        label += f'\n{attr_name}: {attr_value}'
    return label


def visualize(root: AbstractNode, filename: str):
    dot = graphviz.Digraph()
    q = Queue[AbstractNode]()
    q.put(root)
    dot.node(str(root.id), get_node_label(root), shape='box')
    while not q.empty():
        node = q.get()
        for edge_label, child_node in node.enumerate_nodes():
            dot.node(str(child_node.id), get_node_label(child_node), shape='box')
            dot.edge(str(node.id), str(child_node.id), edge_label)
            q.put(child_node)
    dot.render(filename, format='png')

def formatted_source(src: str) -> str:
    lines = [l.strip() for l in src.split('\n')]
    indent = 0
    for i in range(len(lines)):
        if lines[i].startswith('}'):
            indent -= 4
        lines[i] = ' ' * indent + lines[i]
        if lines[i].endswith('{'):
            indent += 4
    return '\n'.join(lines)