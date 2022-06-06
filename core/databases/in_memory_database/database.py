import os.path
from typing import Type, List

from core.databases.utils.binary_io import AdvancedBinaryIO
from core.databases.in_memory_database.table import Table, Column


class Database:
    def __init__(self, tree_type: Type, path: str):
        self._tables = {}
        self._tree_type = tree_type
        self._path = path

        self._load()

    def make_table(self, table_name: str, columns: List[Column]) -> Table:
        if self.table_exists(table_name):
            raise RuntimeError(f'Table with name {table_name} already exists')
        self._tables[table_name] = Table(self._tree_type, columns)
        return self._tables[table_name]

    def table_exists(self, table_name: str) -> bool:
        return table_name in self._tables

    def drop_table(self, table_name: str):
        if not self.table_exists(table_name):
            raise RuntimeError(f'Table with name {table_name} does not exist')
        self._tables.pop(table_name)

    def get_table(self, table_name: str) -> Table:
        if not self.table_exists(table_name):
            raise RuntimeError(f'Table with name {table_name} does not exist')
        return self._tables[table_name]

    def _load(self):
        if os.path.exists(self._path):
            with open(self._path, 'rb') as file:
                binary_io = AdvancedBinaryIO(file)
                table_count = binary_io.read_int()
                for _ in range(table_count):
                    table_name = binary_io.read_string()
                    self._tables[table_name] = Table.load(binary_io, self._tree_type)

    def sync(self):
        with open(self._path, 'wb') as file:
            binary_io = AdvancedBinaryIO(file)
            binary_io.write_int(len(self._tables))
            for name, table in self._tables.items():
                binary_io.write_string(name)
                table.write(binary_io)

    def __del__(self):
        self.sync()
