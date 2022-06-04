""" Two Three Tree implementation """

from core.trees.abstract_tree import AbstractTree


class Node:
    """ Node class of Two Three Tree """

    def __init__(self, key, value, parent=None):
        self.data = [(key, value)]
        self.children = []
        self.parent = parent

    def __str__(self, level=0):
        """ Convert node and all children to string """
        string = ""
        for _ in range(level):
            string += "\t"
        string += f"{self.data}\n"
        for child in self.children:
            string += child.__str__(level + 1)
        return string

    def __lt__(self, node):
        """ Return True if self node is less than node """
        return self.data[0][0] < node.data[0][0]

    def __gt__(self, node):
        """ Return True if self node is greater than node """
        return self.data[0][0] > node.data[0][0]

    def __eq__(self, node):
        """ Return True if self node is equal to node """
        return self.data == node.data

    def __ne__(self, node):
        """ Return True if self node is not equal to node """
        return self.data != node.data

    def __len__(self):
        """ Return number of keys in node """
        return len(self.data)

    @property
    def data_list(self):
        """ Return list of data """
        return [x[0] for x in self.data]

    @property
    def size(self):
        """ Return size of tree """
        return len(self) + sum(child.size for child in self.children)

    @property
    def is_leaf(self):
        """ Return True if node has no children (is a leaf) """
        return len(self.children) == 0

    def set_parent(self, parent):
        """ Set parent node """
        self.parent = parent

    def set_parent_for_node_children(self, node):
        """ Set parent for node's children """
        for child in node.children:
            child.set_parent(self)

    def delete_child(self, node):
        """ Delete child node """
        if node in self.children:
            self.children.remove(node)

    def split(self):
        """ Split node if it is full """
        if len(self) != 3:
            # If node is not full, do nothing
            return

        # Create new 2 nodes and middle item
        left = Node(self.data[0][0], self.data[0][1], self)
        middle = self.data[1]
        right = Node(self.data[2][0], self.data[2][1], self)

        if not self.is_leaf:
            # Split own children into left and right nodes if not a leaf
            for child_n in range(4):
                self.children[child_n].set_parent(left if child_n in (0, 1) else right)
            left.children, right.children = self.children[0:2], self.children[2:4]
        # Assign new children and new data as middle item
        self.children, self.data = [left, right], [middle]

        if self.parent:
            # If node has a parent, insert into parent
            self.parent.delete_child(self)
            self.parent.combine_nodes(self)
            return

        # If node has no parent, new root node is self
        left.set_parent(self)
        right.set_parent(self)

    def combine_nodes(self, node):
        """ Combine node with self """
        self.set_parent_for_node_children(node)
        self.data.extend(node.data)
        self.children.extend(node.children)
        self.data.sort(key=lambda x: x[0])
        self.children.sort(key=lambda x: x.data[0])
        self.split()

    def insert(self, node):
        """ Insert node into tree """
        if node.data[0][0] in self.data_list:
            # If key is already in data, replace value
            for key_data, _ in enumerate(self.data):
                if self.data[key_data][0] == node.data[0][0]:
                    self.data[key_data] = node.data[0]
                    break
        elif self.is_leaf:
            # If node is leaf, insert into data
            self.combine_nodes(node)
        else:
            # If node is not leaf, insert into children
            if node < self:
                # If node is less than self, insert into left child
                self.children[0].insert(node)
            elif node.data[0][0] > self.data[-1][0]:
                # If node is greater than self, insert into right child
                self.children[-1].insert(node)
            else:
                # If node is between self, insert into middle child
                self.children[1].insert(node)

    def insert_all(self, items):
        """ Insert all items into tree """
        for item in items:
            self.insert(Node(*item))

    def get(self, key):
        """ Return value of key in tree, or None if key not found """
        if key in self.data_list:
            # If key is in data, it is in tree
            for key_data in self.data:
                if key_data[0] == key:
                    return key_data[1]
        if self.is_leaf:
            # If node is leaf, key not found
            return None
        if key < self.data[0][0]:
            # If key is less than self, search left child
            return self.children[0].get(key)
        if key > self.data[-1][0]:
            # If key is greater than self, search right child
            return self.children[-1].get(key)
        # If key is between self, search middle child
        return self.children[1].get(key)

    def get_all_children_data_recursive(self):
        """ Return all data in tree """
        if self.is_leaf:
            return self.data

        children_data = []
        for child in self.children:
            children_data.extend(child.get_all_children_data_recursive())
        children_data.extend(self.data)

        return children_data

    def inorder(self):
        """ Return all data in tree """
        if self.is_leaf:
            return self.data

        children_data = []

        if len(self) == 1:
            children_data.extend(self.children[0].inorder())
            children_data.extend(self.data)
            children_data.extend(self.children[1].inorder())
        else:
            if len(self.children) == 2:
                children_data.extend(self.children[0].inorder())
                children_data.extend(self.data)
                children_data.extend(self.children[1].inorder())
            else:
                children_data.extend(self.children[0].inorder())
                children_data.extend([self.data[0]])
                children_data.extend(self.children[1].inorder())
                children_data.extend([self.data[1]])
                children_data.extend(self.children[2].inorder())

        return children_data

    def search_node_with_minimum_key(self):
        """ Return node with minimum key """
        if self.is_leaf:
            return self

        return self.children[0].search_node_with_minimum_key()

    def delete_from_node(self, key):
        """ Delete key from node """
        for key_n in range(len(self)):
            if self.data[key_n][0] == key:
                if self.is_leaf and self.parent is None:
                    self.data.pop(key_n)
                    return
                if self.is_leaf:
                    minimum_node = self
                else:
                    if key_n == 0:
                        minimum_node = self.children[1].search_node_with_minimum_key()
                    else:
                        minimum_node = self.children[-1].search_node_with_minimum_key()
                    minimum_node.data[0], self.data[key_n] = self.data[key_n], minimum_node.data[0]
                    self.data.sort(key=lambda x: x[0])

                children_data = minimum_node.parent.get_all_children_data_recursive()
                for child in children_data:
                    if child[0] == key:
                        children_data.remove(child)
                        break

                minimum_node.parent.data, minimum_node.parent.children = [], []
                minimum_node.parent.insert_all(children_data)
                break

    def delete(self, key):
        """ Delete key from tree """
        if key in self.data_list:
            # If key is in data, delete from data

            # # Slow realization
            # children_data = self.get_all_children_data_recursive()
            #
            # for child in children_data:
            #     if child[0] == key:
            #         children_data.remove(child)
            #
            # self.data, self.children = [], []
            # self.insert_all(children_data)

            # Fast realization
            self.delete_from_node(key)
        elif self.is_leaf:
            # If node is leaf, key not found
            return False
        else:
            if key < self.data[0][0]:
                # If key is less than self, search left child
                self.children[0].delete(key)
            elif key > self.data[-1][0]:
                # If key is greater than self, search right child
                self.children[-1].delete(key)
            else:
                # If key is between self, search middle child
                self.children[1].delete(key)


class TwoThreeTree(AbstractTree):
    """ Two-Three Tree """

    def __init__(self):
        self.root = None

    def __str__(self):
        """ Return string representation of tree """
        if not self._has_root:
            return ""
        return str(self.root)[:-1]

    def __len__(self):
        """ Return number of keys in tree """
        return self.root.size

    @property
    def _has_root(self):
        """ Return True if tree has root """
        return self.root is not None

    def _find_root(self):
        """ Find root of tree """
        if not self._has_root:
            return False
        while self.root.parent is not None:
            self.root = self.root.parent
        return self.root

    def insert(self, key, value):
        """ Insert key, value pair into tree """
        if not self._has_root:
            self.root = Node(key, value)
        else:
            self.root.insert(Node(key, value))
            self._find_root()

    def get(self, key):
        """ Return key in tree, or None if not found """
        if not self._has_root:
            raise KeyError("Key not found")
        element = self.root.get(key)
        if element is None:
            raise KeyError("Key not found")
        return element

    def contains(self, key) -> bool:
        """ Return True if key is in tree """
        if not self._has_root:
            return False
        return self.root.get(key) is not None

    def delete(self, key):
        """ Delete key from tree """
        if not self._has_root:
            return False
        if self.root.delete(key):
            self._find_root()
            if not self.root.data:
                self.root = None
            return True
        return False

    def __iter__(self):
        """ Return iterator over keys in tree """
        if not self._has_root:
            return iter([])
        return iter(self.root.inorder())


if __name__ == '__main__':
    tree = TwoThreeTree()

    dct = {'A': 5, 'B': 7, 'C': 9, 'D': 11, 'E': 13, 'F': 15,
           'G': 17, 'H': 19, 'I': 21, 'J': 23, 'K': 25, 'L': 27,
           'M': 29, 'N': 31, 'O': 33, 'P': 35, 'Q': 37, 'R': 39,
           'S': 41, 'T': 43, 'U': 45, 'V': 47, 'W': 49, 'X': 51}

    for a, b in dct.items():
        tree.insert(a, b)

    print("Size of dictionary:", len(dct))
    print()
    print(tree)
    print()
    TO_DELETE = 'H'
    print(
        f"Tree contains '{TO_DELETE}': {tree.contains(TO_DELETE)}, Tree value of '{TO_DELETE}': {tree.get(TO_DELETE)}")
    print(f"Size of tree: {len(tree)}")

    print(f"Deleting {TO_DELETE}: {tree.delete(TO_DELETE)}")
    print(f"Deleting {TO_DELETE}: {tree.delete(TO_DELETE)}")

    print()
    print(tree)
    print()
    print(f"Tree contains '{TO_DELETE}': {tree.contains(TO_DELETE)}")
    print(f"Size of tree: {len(tree)}")
    print()
    print(f"Iterate over tree: {list(tree)}")
