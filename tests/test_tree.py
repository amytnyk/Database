import unittest

from core.trees.abstract_tree import AbstractTree
from core.trees.avl_tree import AVLTree
from core.trees.b_tree import BTree
from core.trees.builtin_tree import BuiltinTree
from core.trees.red_black_tree import RedBlackTree
from core.trees.splay_tree import SplayTree
from core.trees.two_three_tree import TwoThreeTree

trees = [BuiltinTree]  # TODO [AVLTree, RedBlackTree, BTree, TwoThreeTree, SplayTree]


class TreeTest(unittest.TestCase):
    def test_basic(self):
        for tree_type in trees:
            tree: AbstractTree = tree_type()
            with self.subTest(f"Checking {tree.__class__.__name__}"):
                tree.insert("A", 1)
                tree.insert("B", 2)
                tree.insert("C", 4)

                self.assertTrue(tree.contains("A"))
                self.assertTrue(tree.contains("B"))
                self.assertTrue(tree.contains("C"))
                self.assertFalse(tree.contains("D"))

                tree.delete("B")
                self.assertFalse(tree.contains("B"))

                self.assertEqual(tree.get("A"), 1)
                tree.insert("A", 5)
                self.assertEqual(tree.get("A"), 5)

                for i in range(200000):
                    tree.insert(str(i), i)

                for i in range(200000):
                    self.assertTrue(tree.contains(str(i)))

                for i in range(200000):
                    self.assertEqual(tree.get(str(i)), i)

                for i in range(20000):
                    tree.delete(str(i))

                for i in range(20000):
                    self.assertFalse(tree.contains(str(i)))
