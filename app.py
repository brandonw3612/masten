from tree_sitter import Language, Parser

import langs.imp as imp
import parsers.tree_sitter_imp as tree_sitter_imp
import mast.utils as utils

parser = Parser(Language(tree_sitter_imp.language()))

with open('tests/imp/eg1.imp', 'r') as f:
    src = f.read()
    ts_tree = parser.parse(bytes(src, encoding='utf-8'))
    tree = imp.Program.from_tree_sitter(ts_tree)
    utils.visualize(tree, 'imp')
    print(utils.formatted_source(tree.to_source()))