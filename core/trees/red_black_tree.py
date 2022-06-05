from core.trees.abstract_tree import AbstractTree


class Leaf:
    """
    Leaf class
    """

    def __init__(self, parent):
        self.key = None
        self.color = "black"
        self.parent = parent


class BSTNode:
    """Represents a node for a linked binary search tree."""

    def __init__(self, key, data, parent=None, color='red'):
        self.key = key
        self.data = data
        self.parent = parent
        self.color = color
        self.left = Leaf(self)
        self.right = Leaf(self)


class RedBlackTree(AbstractTree):

    def __init__(self):
        self._root = None

    def insert(self, key, value):
        """
        Inserts key-value pair into the tree
        Overwrites the existing record if the key is already in the tree
        :param key:
        :param value:
        :return: None
        """
        if self._root is None:
            self._root = BSTNode(key, value, None, 'black')
        else:
            node = self._root
            while 1:
                if key < node.key:
                    if node.left.key is not None:
                        node = node.left
                    else:
                        node.left = BSTNode(key, value, node)
                        node = node.left
                        break
                elif key > node.key:
                    if node.right.key is not None:
                        node = node.right
                    else:
                        node.right = BSTNode(key, value, node)
                        node = node.right
                        break
                else:
                    node.data = value
                    break
            self.checker(node)

    def checker(self, node):
        while node != self._root and node.parent.color == "red":
            uncle = node.parent.parent.left if node.parent.parent.right == node.parent else node.parent.parent.right
            if uncle.color == "red":
                node.parent.color = "black"
                uncle.color = "black"
                node.parent.parent.color = "red"
                node = node.parent.parent
            else:
                if node.parent == node.parent.parent.right:
                    if node == node.parent.left:
                        node = node.parent
                        self.rotate_right(node)
                    node.parent.color = "black"
                    node.parent.parent.color = "red"
                    self.rotate_left(node.parent.parent)
                else:
                    if node == node.parent.right:
                        node = node.parent
                        self.rotate_left(node)
                    node.parent.color = "black"
                    node.parent.parent.color = "red"
                    self.rotate_right(node.parent.parent)
        self._root.color = "black"

    def rotate_left(self, node):
        temp = node.right
        node.right = temp.left
        temp.left.parent = node
        temp.parent = node.parent
        if node.parent is None:
            self._root = temp
        elif node == node.parent.left:
            node.parent.left = temp
        else:
            node.parent.right = temp
        temp.left = node
        node.parent = temp

    def rotate_right(self, node):
        temp = node.left
        node.left = temp.right
        temp.right.parent = node
        temp.parent = node.parent
        if node.parent is None:
            self._root = temp
        elif node == node.parent.right:
            node.parent.right = temp
        else:
            node.parent.left = temp
        temp.right = node
        node.parent = temp

    def get(self, key):
        """
        Returns value for the given key
        Raises KeyError if the tree does not contain the given key
        :param key:
        :return:
        """
        node = self._root
        while 1:
            if node.key is not None:
                if node.key > key:
                    node = node.left
                elif node.key < key:
                    node = node.right
                else:
                    return node.data
            else:
                raise KeyError

    def contains(self, key) -> bool:
        """
        Check if the tree contains the given key
        :param key:
        :return:
        """
        node = self._root
        if node is None:
            return False
        while 1:
            if node.key is not None:
                if node.key > key:
                    node = node.left
                elif node.key < key:
                    node = node.right
                else:
                    return True
            else:
                return False

    def _find_subtree_minimal(self, node):
        while node.left.key is not None:
            node = node.left
        return node

    def _transplant(self, node1, node2):
        node1.key, node1.data, node2.key, node2.data = node2.key, node2.data, node1.key, node1.data

    def _replace(self, node, child):
        if node.parent is None:
            self._root = child
            return
        elif node.parent.left == node:
            node.parent.left = child
            child.parent = node.parent
        else:
            node.parent.right = child
            child.parent = node.parent

    def _delete_node_without_children(self, node):
        if not isinstance(node.left, Leaf):
            self._replace(node, node.left)
            return node.left
        if not isinstance(node.right, Leaf):
            self._replace(node, node.right)
            return node.right
        child = Leaf(node)
        self._replace(node, child)
        return child

    def delete(self, key):
        """
        Deletes the given key from the tree
        :param key:
        :return:
        """
        if key == self._root.key and isinstance(self._root.right, Leaf) and isinstance(self._root.left, Leaf):
            self._root = Leaf(None)
            return
        node = self._root
        while 1:
            if node.key is not None:
                if node.key > key:
                    node = node.left
                elif node.key < key:
                    node = node.right
                else:
                    break
            else:
                return

        if isinstance(node.left, Leaf) or isinstance(node.right, Leaf):
            child = self._delete_node_without_children(node)
            deleted_color = node.color
        else:
            min_right = self._find_subtree_minimal(node.right)
            self._transplant(node, min_right)
            child = self._delete_node_without_children(min_right)
            deleted_color = min_right.color
        if deleted_color == "black":
            self._delete_balance(child)

    def _delete_balance(self, node):
        if node == self._root:
            if self._root.color == "red":
                self._root.color = "black"
            return
        brother = node.parent.left if node == node.parent.right else node.parent.right
        if brother.color == "red":
            brother.color = "black"
            node.parent.color = "red"
            if node == node.parent.left:
                self.rotate_left(node.parent)
            else:
                self.rotate_right(node.parent)
            brother = node.parent.left if node == node.parent.right else node.parent.right
        if brother.left.color == brother.right.color == "black":
            brother.color = "red"
            if node.parent.color == "red":
                node.parent.color = "black"
            else:
                self._delete_balance(node.parent)
        else:
            if node == node.parent.left and brother.right.color == "black":
                brother.left.color = "black"
                brother.color = "red"
                self.rotate_right(brother)
                brother = node.parent.left if node == node.parent.right else node.parent.right
            elif node == node.parent.right and brother.left.color == "black":
                brother.right.color = "black"
                brother.color = "red"
                self.rotate_left(brother)
                brother = node.parent.left if node == node.parent.right else node.parent.right
            brother.color = node.parent.color
            node.parent.color = "black"
            if node == node.parent.left:
                brother.right.color = "black"
                self.rotate_left(node.parent)
            else:
                brother.left.color = "black"
                self.rotate_right(node.parent)

    def __iter__(self):
        """Iter"""
        def dfs(node: BSTNode):
            """DFS"""
            if not isinstance(node, Leaf):
                yield from dfs(node.left)
                yield node.key, node.data
                yield from dfs(node.right)
        yield from dfs(self._root)

