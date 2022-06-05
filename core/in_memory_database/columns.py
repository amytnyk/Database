from dataclasses import dataclass
from typing import Literal, List, Tuple


@dataclass
class Column:
    name: str
    value_type: str | Literal['int', 'float', 'bool', 'str']
    is_unique: bool = False


class UniqueColumn(Column):
    def __init__(self, name: str, value_type: str | Literal['int', 'float', 'bool', 'str']):
        super().__init__(name, value_type, True)


class Columns:
    def __init__(self, columns: List[Column]):
        self.columns = columns
        if not any(map(lambda column: column.is_unique, self.columns)):
            raise RuntimeError('At least one column should be unique')

    def make_key_value_pair(self, values: List) -> Tuple:
        key = []
        value_list = []
        for idx, value in enumerate(values):
            if self.columns[idx].is_unique:
                key.append(value)
            else:
                value_list.append(value)
        return tuple(key), tuple(value_list)

    def make_values(self, key: Tuple, value: Tuple, columns: List[str]) -> List:
        key = list(key)
        value_list = list(value)
        values = []
        for column in self.columns:
            if column.is_unique:
                item = key.pop(0)
            else:
                item = value_list.pop(0)
            if not columns or column.name in columns:
                values.append(item)
        return values

    def get_value(self, values: List, name: str):
        for idx, column in enumerate(self.columns):
            if column.name == name:
                return values[idx]
        raise ValueError

    def get_unique(self):
        for idx, column in enumerate(self.columns):
            if column.is_unique:
                yield idx, column
