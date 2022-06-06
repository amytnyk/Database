from typing import List, Dict, Any, Tuple

from core.databases.utils.columns import Columns
from core.databases.utils.node import Node, ColumnNode, ValueNode, BinaryNode


class Frame:
    def __init__(self, columns: Columns, nodes: List[Node] = None, unique: Dict[str, Any] = None):
        self.columns = columns
        self.unique = unique if unique else {}
        self.additional = nodes if nodes else []
        self.alwaysFalse = False

    def __add__(self, other):
        if isinstance(other, FalseFrame):
            return FalseFrame(self.columns)
        for key, value in other.unique.items():
            if key in self.unique and self.unique[key] != value:
                return FalseFrame(self.columns)
        return Frame(self.columns, self.additional + other.additional, self.unique | other.unique)

    def is_unique(self):
        return len(self.unique) == len(list(self.columns.get_unique()))

    def get_unique(self) -> Tuple:
        columns = []
        for idx, item in enumerate(self.columns.columns):
            if item.is_unique:
                columns.append(self.unique[item.name])
        return tuple(columns)

    def check(self, values):
        def _check(node: Node):
            if isinstance(node, BinaryNode):
                if node.operator == 'less':
                    return _check(node.left) < _check(node.right)
                if node.operator == 'greater':
                    return _check(node.left) > _check(node.right)
                if node.operator == 'equal':
                    return _check(node.left) == _check(node.right)
                if node.operator == 'and':
                    return _check(node.left) and _check(node.right)
                if node.operator == 'or':
                    return _check(node.left) or _check(node.right)
            if isinstance(node, ColumnNode):
                return self.columns.get_value(values, node.name)
            if isinstance(node, ValueNode):
                return node.data
            raise RuntimeError

        if not all(map(_check, self.additional)):
            return False
        if not self.is_unique():
            for unique_key, unique_value in self.unique.items():
                if self.columns.get_value(values, unique_key) != unique_value:
                    return False
        return True


class FalseFrame(Frame):
    def check(self, values):
        return False

