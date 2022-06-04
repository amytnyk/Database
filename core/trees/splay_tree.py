"""Module to create a splay tree"""
# from core.trees.abstract_tree import AbstractTree

class Node:
    def  __init__(self, key, data=None):
        if data is None:
            data = key
        self.key = key
        self.data = data
        self.parent = None
        self.left = None
        self.right = None

class SplayTree:
    """Class to represent a splay tree, based on Abstract tree"""
    def __init__(self):
        self.root = None

    def __iter__(self):
        def iter_helper(node: Node):
            """Additional function to iterate"""
            if node is not None:
                yield from iter_helper(node.left)
                yield node.key, node.data
                yield from iter_helper(node.right)
        yield from iter_helper(self.root)

    def get(self, key):
        node = self.root
        while node is not None:
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            elif key == node.key:
                self._splay(node)
                return node.data
        raise KeyError

    def delete(self, key):
        if self.root is None:
            return
        node = self.root
        while node is not None:
            if node.key == key:
                position = node
                break
            if node.key < key:
                node = node.right
            else:
                node = node.left
        if position is None:
            return
        self._splay(position)
        if position.right is not None:
            t_root = position.right
            t_root.parent = None
        else:
            t_root = None
        s_root = position
        s_root.right = None
        position = None
        if s_root.left is not None:
            s_root.left.parent = None
        self.root = self._join(s_root.left, t_root)
        s_root = None

    def insert(self, key, data=None):
        node = Node(key, data)
        parent = None
        temp = self.root
        while temp is not None:
            parent = temp
            if node.key < temp.key:
                temp = temp.left
            else:
                temp = temp.right
        node.parent = parent
        if parent is None:
            self.root = node
        elif node.key < parent.key:
            parent.left = node
        else:
            parent.right = node
        self._splay(node)

    def contains(self, key) -> bool:
        try:
            self.get(key)
        except KeyError:
            return False
        return True

    def __left_rotate(self, node: Node):
        """Performs a left rotation of the tree"""
        temp = node.right
        node.right = temp.left
        if temp.left is not None:
            temp.left.parent = node
        temp.parent = node.parent
        if node.parent is None:
            self.root = temp
        elif node == node.parent.left:
            node.parent.left = temp
        else:
            node.parent.right = temp
        temp.left = node
        node.parent = temp

    def __right_rotate(self, node: Node):
        """Performs a right rotation of the tree"""
        temp = node.left
        node.left = temp.right
        if temp.right is not None:
            temp.right.parent = node
        temp.parent = node.parent;
        if node.parent is None:
            self.root = temp
        elif node == node.parent.right:
            node.parent.right = temp
        else:
            node.parent.left = temp
        temp.right = node
        node.parent = temp

    def _splay(self, node: Node):
        """Splays a tree, node becomes a root"""
        while node.parent is not None:
            if node.parent.parent is None:
                if node == node.parent.left:
                    self.__right_rotate(node.parent)
                else:
                    self.__left_rotate(node.parent)
            elif node == node.parent.left and node.parent == node.parent.parent.left:
                self.__right_rotate(node.parent.parent)
                self.__right_rotate(node.parent)
            elif node == node.parent.right and node.parent == node.parent.parent.left:
                self.__left_rotate(node.parent)
                self.__right_rotate(node.parent)
            elif node == node.parent.right and node.parent == node.parent.parent.right:
                self.__left_rotate(node.parent.parent)
                self.__left_rotate(node.parent)
            else:
                self.__right_rotate(node.parent)
                self.__left_rotate(node.parent)

    def _join(self, s_root: Node, t_root: Node):
        """Joins two trees, helper for delete operation"""
        if s_root is None:
            return t_root
        if t_root is None:
            return s_root
        node = self._get_maximum(s_root)
        self._splay(node)
        node.right = t_root
        t_root.parent = node
        return node

    def _get_maximum(self, node: Node):
        """Returns the biggest value of the tree"""
        while node.right is not None:
            node = node.right
        return node
