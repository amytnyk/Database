import itertools
from typing import List

from core.databases.utils.columns import Columns
from core.databases.utils.frame import Frame
from core.databases.utils.node import Node, BinaryNode, ColumnNode, ValueNode
from core.databases.utils.tokenizer import Tokenizer, ColumnToken


def compile_predicate(expr: str, columns: Columns) -> List[Frame]:
    tokens = list(Tokenizer(expr))
    idx = 0

    def _compile_dynamic() -> Node:
        nonlocal idx
        token = tokens[idx]
        idx += 1

        if token.data in ['or', 'and', 'equals', 'less', 'greater']:
            return BinaryNode(token.data, _compile_dynamic(), _compile_dynamic())
        elif isinstance(token, ColumnToken):
            return ColumnNode(token.data)
        else:
            return ValueNode(token.data)

    def _compile_value() -> Node:
        nonlocal idx
        token = tokens[idx]
        idx += 1

        if isinstance(token, ColumnToken):
            return ColumnNode(token.data)
        else:
            return ValueNode(token.data)

    def _compile_static() -> List[Frame]:
        nonlocal idx
        token = tokens[idx]
        idx += 1
        if token.data == 'or':
            return _compile_static() + _compile_static()
        elif token.data == 'and':
            return list(map(lambda x: x[0] + x[1], itertools.product(_compile_static(), _compile_static())))
        elif token.data == 'equals':
            value1 = _compile_value()
            value2 = _compile_value()
            if isinstance(value1, ValueNode) and isinstance(value2, ColumnNode):
                value1, value2 = value2, value1
            if isinstance(value1, ColumnNode) and isinstance(value2, ValueNode):
                return [Frame(columns, [], {value1.name: value2.data})]
            else:
                return [Frame(columns, [BinaryNode('equals', value1, value2)])]
        elif token.data == 'less':
            return [Frame(columns, [BinaryNode('less', _compile_dynamic(), _compile_dynamic())])]
        elif token.data == 'greater':
            return [Frame(columns, [BinaryNode('greater', _compile_dynamic(), _compile_dynamic())])]

    return _compile_static()
