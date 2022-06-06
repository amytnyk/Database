from typing import Type, List

from core.databases.utils.binary_io import AdvancedBinaryIO
from core.databases.utils.columns import Column, Columns
from core.databases.utils.predicate_compiler import compile_predicate
from core.trees.abstract_tree import AbstractTree


class Table:
    def __init__(self, tree_type: Type, columns: List[Column]):
        self._columns = Columns(columns)
        self._tree: AbstractTree = tree_type()

    def insert(self, *values):
        self._tree.insert(*self._columns.make_key_value_pair(list(values)))

    def select(self, *columns):
        for key, value in self._tree:
            yield self._columns.make_values(key, value, list(columns))

    def select_where(self, predicate: str, *columns):
        frames = list(compile_predicate(predicate))
        unique_frames = filter(lambda x: x.is_unique(), frames)
        standard_frames = filter(lambda x: not x.is_unique(), frames)

        yielded = set()

        for frame in unique_frames:
            if frame.get_unique() not in yielded:
                if frame.get_unique() in self._tree:
                    value = self._tree.get(frame.get_unique())
                    values = self._columns.make_values(frame.get_unique(), value, [])

                    if frame.check(values):
                        yielded.add(frame.get_unique())
                        yield self._columns.make_values(frame.get_unique(), value, list(columns))
        for frame in standard_frames:
            for key, value in self._tree:
                if key not in yielded:
                    values = self._columns.make_values(key, value, [])
                    if frame.check(values):
                        yielded.add(key)
                        yield self._columns.make_values(key, value, list(columns))

    def delete(self, predicate: str):
        frames = list(compile_predicate(predicate, self._columns))
        unique_frames = filter(lambda x: x.is_unique(), frames)
        standard_frames = filter(lambda x: not x.is_unique(), frames)

        deleted = set()

        for frame in unique_frames:
            if frame.get_unique() not in deleted:
                if frame.get_unique() in self._tree:
                    value = self._tree.get(frame.get_unique())
                    values = self._columns.make_values(frame.get_unique(), value, [])

                    if frame.check(values):
                        deleted.add(frame.get_unique())
                        self._tree.delete(frame.get_unique())

        for frame in standard_frames:
            for key, value in self._tree:
                if key not in deleted:
                    values = self._columns.make_values(key, value, [])
                    if frame.check(values):
                        deleted.add(key)
                        self._tree.delete(key)

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
