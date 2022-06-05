import itertools
from typing import Type, List, Any, Dict, Tuple

from core.in_memory_database.binary_io import AdvancedBinaryIO
from core.in_memory_database.columns import Column, Columns
from core.in_memory_database.tokenizer import Tokenizer, ColumnToken
from core.trees.abstract_tree import AbstractTree


class Node:
    pass


class BinaryNode(Node):
    def __init__(self, operator: str, left, right):
        self.operator = operator
        self.left = left
        self.right = right


class ValueNode(Node):
    def __init__(self, data):
        self.data = data


class ColumnNode(Node):
    def __init__(self, name: str):
        self.name = name


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


class Table:
    def __init__(self, tree_type: Type, columns: List[Column]):
        self._columns = Columns(columns)
        self._tree: AbstractTree = tree_type()

    def insert(self, *values):
        self._tree.insert(*self._columns.make_key_value_pair(list(values)))

    def select(self, *columns):
        for key, value in self._tree:
            yield self._columns.make_values(key, value, list(columns))

    def _compile_predicate(self, expr: str) -> List[Frame]:
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
                    return [Frame(self._columns, [], {value1.name: value2.data})]
                else:
                    return [Frame(self._columns, [BinaryNode('equals', value1, value2)])]
            elif token.data == 'less':
                return [Frame(self._columns, [BinaryNode('less', _compile_dynamic(), _compile_dynamic())])]
            elif token.data == 'greater':
                return [Frame(self._columns, [BinaryNode('greater', _compile_dynamic(), _compile_dynamic())])]

        return _compile_static()

    def select_where(self, predicate: str, *columns):
        frames = list(self._compile_predicate(predicate))
        unique_frames = filter(lambda x: x.is_unique(), frames)
        standard_frames = filter(lambda x: not x.is_unique(), frames)

        yielded = set()

        for frame in unique_frames:
            if frame.get_unique() not in yielded:
                value = self._tree.get(frame.get_unique())
                values = self._columns.make_values(frame.get_unique(), value, [])

                if frame.check(values):
                    yielded.add(frame.get_unique())
                    yield values
        for frame in standard_frames:
            for key, value in self._tree:
                if key not in yielded:
                    values = self._columns.make_values(key, value, [])
                    if frame.check(values):
                        yielded.add(key)
                        yield self._columns.make_values(key, value, list(columns))

    def write(self, binary_io: AdvancedBinaryIO):
        binary_io.write_int(len(self._columns.columns))
        for column in self._columns.columns:
            binary_io.write_string(column.name)
            binary_io.write_string(column.value_type)
            binary_io.write_bool(column.is_unique)
        rows = list(self._tree)
        binary_io.write_int(len(rows))
        all_rows = list(map(lambda x: x.name, self._columns.columns))
        for row in map(lambda x: self._columns.make_values(x[0], x[1], all_rows), rows):
            for item, column in zip(row, self._columns.columns):
                if column.value_type == "int":
                    binary_io.write_int(item)
                elif column.value_type == "bool":
                    binary_io.write_bool(item)
                elif column.value_type == "float":
                    binary_io.write_float(item)
                elif column.value_type == "str":
                    binary_io.write_string(item)
                else:
                    raise RuntimeError('Unsupported column type')

    @staticmethod
    def load(binary_io: AdvancedBinaryIO, tree_type: Type):
        column_count = binary_io.read_int()
        columns = []
        for _ in range(column_count):
            columns.append(Column(
                binary_io.read_string(),
                binary_io.read_string(),
                binary_io.read_bool()
            ))
        table = Table(tree_type, columns)
        rows_count = binary_io.read_int()
        for _ in range(rows_count):
            values = []
            for column in columns:
                if column.value_type == 'int':
                    values.append(binary_io.read_int())
                elif column.value_type == 'bool':
                    values.append(binary_io.read_bool())
                elif column.value_type == 'float':
                    values.append(binary_io.read_float())
                elif column.value_type == 'str':
                    values.append(binary_io.read_string())
                else:
                    raise RuntimeError('Unsupported column type')
            table.insert(*values)

        return table
