from core.trees.abstract_tree import AbstractTree


# Of course dictionary in python is not a tree, but it has the same functionality
class BuiltinTree(AbstractTree):
    def __init__(self):
        self.dict = {}

    def insert(self, key, value):
        self.dict[key] = value

    def get(self, key):
        return self.dict[key]

    def contains(self, key) -> bool:
        return key in self.dict

    def delete(self, key):
        del self.dict[key]
