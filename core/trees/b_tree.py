from dataclasses import dataclass
from typing import List, Any, Optional, Tuple

from core.trees.abstract_tree import AbstractTree


class BTree(AbstractTree):
    @dataclass
    class _Pair:
        key: Any
        value: Any

    @dataclass
    class _Node:
        items: List
        children: List

        def is_inner(self) -> bool:
            return not self.is_leaf()

        def is_leaf(self) -> bool:
            return not self.children

    def __init__(self, order: int = 3):
        self._order = order
        self._root = None

    def __iter__(self):
        def dfs(node: BTree._Node):
            for idx, item in enumerate(node.items):
                if node.children:
                    yield from dfs(node.children[idx])
                yield node.items[idx]
            if node.children:
                yield from dfs(node.children[-1])

        yield from dfs(self._root)

    @staticmethod
    def _get_new_child_index(node: _Node, item: _Pair) -> Optional[int]:
        for idx, parent in enumerate(node.items):
            if parent.key == item.key:
                parent.value = item.value
                return None
            elif parent.key > item.key:
                return idx
        return len(node.items)

    def _insert(self, node: _Node, item: _Pair) -> Optional[Tuple[_Pair, _Node, _Node]]:
        if (child_idx := BTree._get_new_child_index(node, item)) is not None:
            if node.children:
                splitted_node = self._insert(node.children[child_idx], item)
                if splitted_node is not None:
                    parent, left, right = splitted_node
                    node.items.insert(child_idx, parent)
                    node.children[child_idx:child_idx + 1] = [left, right]
            else:
                node.items.insert(child_idx, item)

            if len(node.items) == self._order:
                middle_idx = len(node.items) // 2
                middle_item = node.items[middle_idx]
                left_node = BTree._Node(node.items[:middle_idx], node.children[:middle_idx + 1])
                right_node = BTree._Node(node.items[middle_idx + 1:], node.children[middle_idx + 1:])
                return middle_item, left_node, right_node

    def insert(self, key, value):
        if self._root:
            splitted_node = self._insert(self._root, BTree._Pair(key, value))
            if splitted_node is not None:
                parent, left, right = splitted_node
                self._root = self._Node([parent], [left, right])
        else:
            self._root = self._Node([BTree._Pair(key, value)], [])

    def _get(self, key):
        root = self._root
        while root is not None:
            for i in range(len(root.items)):
                if key < root.items[i].key:
                    if not root.children:
                        return
                    root = root.children[i]
                    break
                elif key == root.items[i].key:
                    return root.items[i]
            else:
                if key == root.items[-1].key:
                    return root.items[-1]
                if root.children:
                    root = root.children[-1]
                else:
                    break

    def get(self, key):
        pair = self._get(key)
        if pair is None:
            raise IndexError
        return pair.value

    def contains(self, key) -> bool:
        return self._get(key) is not None

    def _get_min_degree(self) -> int:
        return (self._order + 1) // 2 - 1

    def _fix_missing(self, node: _Node, child_idx: int):
        if len(node.children[child_idx].items) < self._get_min_degree():
            if child_idx != 0 and len(node.children[child_idx - 1].items) > self._get_min_degree():
                new_parent = node.children[child_idx - 1].items.pop()
                new_item = node.items[child_idx - 1]
                node.items[child_idx - 1] = new_parent
                node.children[child_idx].items.insert(0, new_item)
                if node.children[child_idx - 1].is_inner():
                    node.children[child_idx].children.insert(0, node.children[child_idx - 1].children.pop())
            elif child_idx != len(node.children) - 1 and \
                    len(node.children[child_idx + 1].items) > self._get_min_degree():
                new_parent = node.children[child_idx + 1].items.pop(0)
                new_item = node.items[child_idx]
                node.items[child_idx] = new_parent
                node.children[child_idx].items.append(new_item)
                if node.children[child_idx + 1].is_inner():
                    node.children[child_idx].children.append(node.children[child_idx + 1].children.pop(0))
            else:
                if child_idx != 0:
                    left_sibling = node.children[child_idx - 1]
                    left_sibling.items.extend([node.items.pop(child_idx - 1)] + node.children[child_idx].items)
                    if node.children[child_idx].is_inner():
                        left_sibling.children.extend(node.children[child_idx].children)
                    node.children.pop(child_idx)
                elif child_idx != len(node.children) - 1:
                    right_sibling = node.children[child_idx + 1]
                    right_sibling.items[:0] = node.children[child_idx].items + [node.items.pop(child_idx)]
                    if node.children[child_idx].is_inner():
                        right_sibling.children[:0] = node.children[child_idx].children
                    node.children.pop(child_idx)
                else:
                    raise RuntimeError('Invalid BTree structure')

    def _shift_left(self, node: _Node, key, root: _Node, item_idx: int):
        if node.children:
            self._shift_left(node.children[-1], key, root, item_idx)
            self._fix_missing(node, len(node.children) - 1)
        else:
            root.items[item_idx] = node.items.pop(-1)

    def _shift_right(self, node: _Node, key, root: _Node, item_idx: int):
        if node.children:
            self._shift_right(node.children[0], key, root, item_idx)
            self._fix_missing(node, 0)
        else:
            root.items[item_idx] = node.items.pop(0)

    def _delete(self, node: _Node, key):
        child_idx = 0
        while child_idx < len(node.items) and node.items[child_idx].key < key:
            child_idx += 1

        if child_idx < len(node.items) and node.items[child_idx].key == key:
            if node.children:
                if key > node.children[child_idx].items[-1].key:
                    self._shift_left(node.children[child_idx], key, node, child_idx)
                elif key < node.children[child_idx + 1].items[0].key:
                    self._shift_right(node.children[child_idx + 1], key, node, child_idx)
                    child_idx += 1
                else:
                    raise RuntimeError('Invalid BTree structure')
            else:
                node.items.pop(child_idx)
                return
        else:
            if not len(node.children):
                raise KeyError(key)

            self._delete(node.children[child_idx], key)

        self._fix_missing(node, child_idx)

    def delete(self, key):
        self._delete(self._root, key)

        if not self._root.items:
            if self._root.children:
                self._root = self._root.children[0]
            else:
                self._root = None
