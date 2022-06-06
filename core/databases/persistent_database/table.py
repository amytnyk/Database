from typing import List, Tuple, Optional

from core.databases.utils.binary_io import AdvancedBinaryIO
from core.databases.utils.columns import Columns

MINIMUM_BTREE_ORDER = 5
MINIMUM_PAGE_SIZE = 4096


class Pair:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class Node:
    def __init__(self, parent_ptr: int, ptr: int, items: List[Pair], child_ptrs: List[int]):
        self.parent_ptr = parent_ptr
        self.ptr = ptr
        self.items = items
        self.child_ptrs = child_ptrs


class Table:
    def __init__(self, file: AdvancedBinaryIO, root_ptr: int, columns: Columns):
        self._file = file
        self._root_ptr = root_ptr
        self._columns = columns
        self._order = (MINIMUM_PAGE_SIZE - 4 - 4) // (columns.get_size() + 4 + 4) + 1
        self._page_size = MINIMUM_PAGE_SIZE
        if self._order < MINIMUM_BTREE_ORDER:
            self._order = MINIMUM_BTREE_ORDER
            self._page_size = (self._order - 1) * (columns.get_size() + 4 + 4)

    def _get_node(self, ptr: int):
        self._file.seek(ptr, 0)
        parent_ptr = self._file.read_int()
        item_count = self._file.read_int()
        items = []
        child_ptrs = [self._file.read_int()]
        for child_idx in range(item_count):
            data = []
            for column in self._columns.columns:
                if column.value_type == 'str':
                    data.append(self._file.read_string())
                elif column.value_type == 'int':
                    data.append(self._file.read_int())
                elif column.value_type == 'bool':
                    data.append(self._file.read_bool())
                elif column.value_type == 'float':
                    data.append(self._file.read_float())
                else:
                    raise RuntimeError

            items.append(Pair(*self._columns.make_key_value_pair(data)))
            child_ptrs.append(self._file.read_int())

        return Node(parent_ptr, ptr, items, child_ptrs)

    def _write_ptr(self, ptr: int, child_ptr: int):
        self._file.seek(ptr, 0)
        self._file.write_int(child_ptr)

    def _read_ptr(self, ptr: int):
        self._file.seek(ptr, 0)
        return self._file.read_int()

    def _add_node(self, parent: int, items: List, child_ptrs: List[int]):
        ptr = self._file.seek(0, 2)
        self._write_ptr(parent, ptr)
        self._set_node(Node(parent, ptr, items, child_ptrs))

    def _set_node(self, node: Node):
        self._file.seek(node.ptr, 0)
        self._file.write_int(node.parent_ptr)
        self._file.write_int(len(node.items))
        self._file.write_int(node.child_ptrs[0])
        for idx, item in enumerate(node.items):
            values = self._columns.make_values(item.key, item.value, [])
            for idx2, column in enumerate(self._columns.columns):
                if column.value_type == 'str':
                    self._file.write_string(values[idx2])
                elif column.value_type == 'int':
                    self._file.write_int(values[idx2])
                elif column.value_type == 'bool':
                    self._file.write_bool(values[idx2])
                elif column.value_type == 'float':
                    self._file.write_float(values[idx2])
                else:
                    raise RuntimeError
            self._file.write_int(node.child_ptrs[idx + 1])

    @staticmethod
    def _get_new_child_index(node: Node, item: Pair) -> Optional[int]:
        for idx, parent in enumerate(node.items):
            if parent.key == item.key:
                parent.value = item.value
                return None
            if parent.key > item.key:
                return idx
        return len(node.items)

    def _insert_node(self, node_ptr: int, item: Pair) -> Optional[Tuple[Pair, Node, Node]]:
        node = self._get_node(node_ptr)
        if (child_idx := self._get_new_child_index(node, item)) is not None:
            if node.child_ptrs:
                splitted_node = self._insert_node(node.child_ptrs[child_idx], item)
                if splitted_node is not None:
                    parent, left, right = splitted_node
                    node.items.insert(child_idx, parent)
                    node.child_ptrs[child_idx:child_idx + 1] = [left.ptr, right.ptr]
            else:
                node.items.insert(child_idx, item)

            if len(node.items) == self._order:
                middle_idx = len(node.items) // 2
                middle_item = node.items[middle_idx]
                left_node = Node(node.items[:middle_idx], node.child_ptrs[:middle_idx + 1])
                right_node = Node(node.items[middle_idx + 1:], node.child_ptrs[middle_idx + 1:])
                return middle_item, left_node, right_node
            else:
                self._set_node(node)
        return None

    def _insert(self, key, value):
        if self._read_ptr(self._root_ptr):
            splitted_node = self._insert_node(self._root_ptr, Pair(key, value))
            if splitted_node is not None:
                parent, left, right = splitted_node
                self._add_node(self._root_ptr, [parent], [left.ptr, right.ptr])
        else:
            self._add_node(self._root_ptr, [Pair(key, value)], [])

    def insert(self, *values):
        self._insert(*self._columns.make_key_value_pair(list(values)))

    def select(self, *columns):
        for key, value in self:
            yield self._columns.make_values(key, value, list(columns))

    def __iter__(self):
        def dfs(ptr: int):
            node = self._get_node(ptr)
            for idx, item in enumerate(node.items):
                if node.child_ptrs:
                    yield from dfs(node.child_ptrs[idx])
                yield item.key, item.value
            if node.child_ptrs:
                yield from dfs(node.child_ptrs[-1])

        return dfs(self._root_ptr)
