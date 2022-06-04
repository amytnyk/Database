import itertools
import unittest

from core.trees.abstract_tree import AbstractTree
from core.trees.avl_tree import AVLTree
from core.trees.b_tree import BTree
from core.trees.builtin_tree import BuiltinTree
from core.trees.red_black_tree import RedBlackTree
from core.trees.splay_tree import SplayTree
from core.trees.two_three_tree import TwoThreeTree

trees = [AVLTree, RedBlackTree, SplayTree, BTree, TwoThreeTree, BuiltinTree]


class TreeTest(unittest.TestCase):
    @staticmethod
    def run_tests(func):
        def run(self):
            for tree_type in trees:
                with self.subTest(f"Checking {tree_type.__name__}"):
                    func(self, tree_type)
        return run

    @run_tests
    def test_basic(self, tree_type):
        tree: AbstractTree = tree_type()

        tree.insert("A", 1)
        tree.insert("B", 2)
        tree.insert("C", 4)

        self.assertTrue(tree.contains("A"))
        self.assertTrue(tree.contains("B"))
        self.assertTrue(tree.contains("C"))
        self.assertFalse(tree.contains("D"))

        tree.delete("B")
        self.assertFalse(tree.contains("B"))

    @run_tests
    def test_large(self, tree_type):
        tree = tree_type()

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

    @run_tests
    def test_advanced(self, tree_type):
        for lst in itertools.permutations(range(7)):
            insertion_order = list(lst)
            deletion_order = list(lst)
            with self.subTest(f"InsertionOrder({insertion_order}), DeletionOrder({deletion_order})"):
                tree: AbstractTree = tree_type()

                for item in insertion_order:
                    tree.insert(item, item)
                    self.assertTrue(tree.contains(item))

                for idx, item in enumerate(deletion_order):
                    tree.delete(item)
                    self.assertFalse(tree.contains(item))
                    for item2 in deletion_order[idx + 1:]:
                        self.assertTrue(tree.contains(item2))

    @run_tests
    def test_no_element(self, test_type):
        tree = test_type()

        tree.insert("A", 1)
        tree.insert("B", 2)
        tree.insert("C", 3)

        self.assertRaises(KeyError, lambda: tree.get("D"))

    @run_tests
    def test_duplicate(self, test_type):
        tree = test_type()

        tree.insert("A", 1)
        tree.insert("B", 2)
        tree.insert("C", 3)

        self.assertEqual(tree.get("A"), 1)
        tree.insert("A", 5)
        self.assertEqual(tree.get("A"), 5)

        self.assertEqual(tree.get("B"), 2)
        tree.insert("B", "A")
        self.assertEqual(tree.get("B"), "A")

    @run_tests
    def test_iter(self, test_type):
        tree = test_type()

        tree.insert(2, 1)
        tree.insert(4, 2)
        tree.insert(1, 3)
        tree.insert(10, 1)
        tree.insert(11, 2)
        tree.insert(0, 1)

        self.assertEqual(list(iter(tree)), [(0, 1), (1, 3), (2, 1), (4, 2), (10, 1), (11, 2)])
