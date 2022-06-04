"""
AVL Tree
"""
from core.trees.abstract_tree import AbstractTree


class AVLNode:
    """AVL node"""

    def __init__(self, key, val, left=None, right=None):
        """Init"""
        self.key = key
        self.val = val
        self.left = left
        self.right = right
        self.height = 1


class AVLTree(AbstractTree):
    """AVL tree"""

    def __init__(self):
        """Init"""
        self._root = None

    def __iter__(self):
        """Iter"""
        def dfs(node: AVLNode):
            """DFS"""
            if node:
                yield from dfs(node.left)
                yield node.key, node.val
                yield from dfs(node.right)
        yield from dfs(self._root)

    def insert(self, key, val):
        """Insert"""
        def insert_helper(root: AVLNode, key, val):
            """Helper function"""
            if not root:
                root = AVLNode(key, val)
            elif key < root.key:
                root.left = insert_helper(root.left, key, val)
            elif key > root.key:
                root.right = insert_helper(root.right, key, val)
            else:
                root.val = val

            root.height = 1 + max(self.n_height(root.left),
                                  self.n_height(root.right))

            balance = self.balance(root)
            if balance > 1:
                if key < root.left.key:
                    return self.r_rotate(root)
                root.left = self.l_rotate(root.left)
                return self.r_rotate(root)

            if balance < -1:
                if key > root.right.key:
                    return self.l_rotate(root)
                root.right = self.r_rotate(root.right)
                return self.l_rotate(root)

            return root
        if isinstance(key, list):
            for num in zip(key, val):
                self._root = insert_helper(self._root, num[0], num[1])
        else:
            self._root = insert_helper(self._root, key, val)

    def get(self, key):
        """
        Returns node's value if found
        Else raises KeyError
        """
        root = self._root
        while root is not None:
            if key < root.key:
                root = root.left
            elif key > root.key:
                root = root.right
            else:
                return root.val
        raise KeyError

    def contains(self, key) -> bool:
        """
        Checks if element is in tree
        """
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    def delete(self, key):
        """Delete"""
        def helper(root: AVLNode):
            """
            Helper's helper function
            Gets minimal node
            """
            if root is None or root.left is None:
                return root
            return helper(root.left)

        def delete_helper(key, root):
            """Helper function"""
            if not root:
                return root
            if key < root.key:
                root.left = delete_helper(key, root.left)
            elif key > root.key:
                root.right = delete_helper(key, root.right)
            else:
                if root.left is None:
                    temp = root.right
                    root = None
                    return temp
                if root.right is None:
                    temp = root.left
                    root = None
                    return temp
                temp = helper(root.right)
                root.key = temp.key
                root.right = delete_helper(temp.key, root.right)
            if root is None:
                return root

            root.height = 1 + max(self.n_height(root.left),
                                  self.n_height(root.right))

            n_balance = self.balance(root)

            if n_balance > 1:
                if self.balance(root.left) >= 0:
                    return self.r_rotate(root)
                root.left = self.l_rotate(root.left)
                return self.r_rotate(root)

            if n_balance < -1:
                if self.balance(root.right) <= 0:
                    return self.l_rotate(root)
                root.right = self.r_rotate(root.right)
                return self.l_rotate(root)
            return root
        root = self._root
        self._root = delete_helper(key, root)

    def l_rotate(self, node: AVLNode):
        """Left rotation"""
        r_nde = node.right
        lr_nde = r_nde.left
        r_nde.left = node
        node.right = lr_nde
        node.height = 1 + max(self.n_height(node.left),
                              self.n_height(node.right))
        r_nde.height = 1 + max(self.n_height(r_nde.left),
                               self.n_height(r_nde.right))
        return r_nde

    def r_rotate(self, node: AVLNode):
        """Right rotation"""
        l_nde = node.left
        rl_nde = l_nde.right
        l_nde.right = node
        node.left = rl_nde
        node.height = 1 + max(self.n_height(node.left),
                              self.n_height(node.right))
        l_nde.height = 1 + max(self.n_height(l_nde.left),
                               self.n_height(l_nde.right))
        return l_nde

    def n_height(self, root: AVLNode):
        """Returns node height"""
        if not root:
            return 0
        return root.height

    def balance(self, root: AVLNode):
        """Checks balance"""
        if not root:
            return 0
        return self.n_height(root.left) - self.n_height(root.right)
