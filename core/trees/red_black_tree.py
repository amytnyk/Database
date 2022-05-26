from copy import copy

from core.trees.abstract_tree import AbstractTree
class Leaf:

    def __init__(self, color="black"):
        self.key = None
        self.color = color


class BSTNode:
    """Represents a node for a linked binary search tree."""
    def __init__(self, key, data, parent=None, color='red', left=None, right=None):
        self.key = key
        self.data = data
        self.parent = parent
        self.color = color
        self.left = Leaf()
        self.right = Leaf()


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
        # temp = node.left
        # node.left = parent
        # parent.right = temp
        # node.parent = parent.parent
        # if parent != self._root:
        #     if parent.parent.left == parent:
        #         parent.parent.left = node
        #     else:
        #         parent.parent.right = node
        # parent.parent = node
        # node.color = "black"
        # parent.color = "red"
        # if self._root == parent:
        #     self._root = node

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
        # temp = parent.right
        # parent.right = grand
        # grand.left = temp
        # parent.parent = grand.parent
        # if grand != self._root:
        #     if grand.parent.left == grand:
        #         grand.parent.left = parent
        #     else:
        #         grand.parent.right = parent
        # grand.parent = parent
        # parent.color = "black"
        # grand.color = "red"
        # if self._root == grand:
        #     self._root = parent


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

    def delete(self, key):
        """
        Deletes the given key from the tree
        :param key:
        :return:
        """

        node = self._root
        while 1:
            if node.key > key:
                node = node.right
            elif node.key < key:
                node = node.left
            else:
                break
        if node.right is None and node.left is None and node.color == "red":
            node = None
        if node.right is None and node.left is None and node.color == "black":
            pass
        if (node.right is not None or node.left is not None) and node.color == "black":
            pass

    def __iter__(self):
        pass

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.insert(key, value)

    def __contains__(self, item):
        return self.contains(item)

a = RedBlackTree()
a.insert(0, 0)
a.insert(1, 1)
a.insert(2, 2)
a.insert(7, 7)
a.insert(8, 8)
a.insert(3, 3)
a.insert(4, 4)
a.insert(5, 5)
a.insert(6, 6)
t1 = a.get(0)
t2 = a.get(1)
t3 = a.get(2)
t4 = a.get(3)
t5 = a.get(4)
t6 = a.get(5)
t7 = a.get(6)
t8 = a.get(7)
t9 = a.get(8)
# print(a._root.key)
# a.insert("A", 1)
# a.insert("B", 2)
# a.insert("C", 4)
# a.insert(68, 67)
# a.insert(1, 1)
# a.insert(2, 2)
# a = a
# for i in range(1, 12, 1):
#     a.insert(i, i)
# a = a
# print(a.get(10))
