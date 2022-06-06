class Node:
    pass


class BinaryNode(Node):
    def __init__(self, operator: str, left, right):
        self.operator = operator
        self.left = left
        self.right = right


class ValueNode(Node):
    def __init__(self, data):
        self.data = data


class ColumnNode(Node):
    def __init__(self, name: str):
        self.name = name
