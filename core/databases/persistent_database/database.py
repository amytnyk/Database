import os.path
from typing import List

from core.databases.persistent_database.table import Table
from core.databases.utils.binary_io import AdvancedBinaryIO
from core.databases.utils.columns import Column, Columns

DATABASE_DESCRIPTOR_SIZE = 32765
MAX_TABLE_NAME_SIZE = 20
MAX_TABLE_COLUMN_COUNT = 20
MAX_TABLE_COLUMN_NAME_SIZE = 20
COLUMN_DESCRIPTOR_SIZE = 4 + MAX_TABLE_COLUMN_NAME_SIZE + 1 + 1
TABLE_DESCRIPTOR_SIZE = 4 + MAX_TABLE_NAME_SIZE + 4 + MAX_TABLE_COLUMN_COUNT * COLUMN_DESCRIPTOR_SIZE + 4
MAX_TABLE_COUNT = (DATABASE_DESCRIPTOR_SIZE - 4) // TABLE_DESCRIPTOR_SIZE


class Database:
    def __init__(self, path: str):
        if os.path.exists(path):
            self.file = AdvancedBinaryIO(open(path, 'rb+'))
        else:
            self.file = AdvancedBinaryIO(open(path, 'wb+'))
            self.file.write_int(0)
            self.file.fill(DATABASE_DESCRIPTOR_SIZE - 4)
        self._path = path

    def table_count(self) -> int:
        self.file.seek(0, 0)
        return self.file.read_int()

    @staticmethod
    def _byte_to_value_type(byte: int) -> str:
        return ['str', 'float', 'int', 'bool'][byte]

    @staticmethod
    def _value_type_to_byte(value_type: str) -> int:
        return ['str', 'float', 'int', 'bool'].index(value_type)

    def make_table(self, table_name: str, columns: List[Column]) -> Table:
        if self.table_exists(table_name):
            raise RuntimeError(f'Table with name {table_name} already exists')
        if self.table_count() == MAX_TABLE_COUNT:
            raise RuntimeError('Maximum table count exceeded')
        if len(table_name.encode('utf-8')) > MAX_TABLE_NAME_SIZE:
            raise RuntimeError('Maximum table size exceeded')

        self.file.seek(0, 0)
        self.file.write_int(self.table_count() + 1)
        self.file.seek(TABLE_DESCRIPTOR_SIZE * (self.table_count() - 1), 1)
        self.file.write_string(table_name)
        self.file.fill(MAX_TABLE_NAME_SIZE - len(table_name.encode('utf-8')))
        self.file.write_int(len(columns))
        for column in columns:
            if len(column.name.encode('utf-8')) > MAX_TABLE_COLUMN_NAME_SIZE:
                raise RuntimeError('Maximum column name size exceeded')
            self.file.write_string(column.name)
            self.file.fill(MAX_TABLE_COLUMN_NAME_SIZE - len(column.name.encode('utf-8')))
            self.file.write_byte(self._value_type_to_byte(column.value_type))
            self.file.write_bool(column.is_unique)
        self.file.seek(0, 2)
        root_ptr = self.file.tell()
        self.file.write_int(root_ptr)

        return Table(self.file, root_ptr, Columns(columns))

    def table_exists(self, table_name: str) -> bool:
        for idx in range(self.table_count()):
            self.file.seek(4 + idx * TABLE_DESCRIPTOR_SIZE, 0)
            if self.file.read_string() == table_name:
                return True
        return False

    def get_table(self, table_name: str) -> Table:
        if not self.table_exists(table_name):
            raise RuntimeError(f'Table with name {table_name} does not exist')
        for idx in range(self.table_count()):
            self.file.seek(4 + idx * TABLE_DESCRIPTOR_SIZE, 0)
            if self.file.read_string() == table_name:
                self.file.seek(MAX_TABLE_NAME_SIZE - len(table_name.encode('utf-8')), 1)
                column_count = self.file.read_int()
                columns = []
                for idx2 in range(column_count):
                    column_name = self.file.read_string()
                    self.file.seek(MAX_TABLE_COLUMN_NAME_SIZE - len(column_name.encode('utf-8')))
                    value_type = self.file.read_byte()
                    is_unique = self.file.read_bool()
                    columns.append(Column(column_name, self._byte_to_value_type(value_type), is_unique))
                root_ptr = self.file.read_int()

                return Table(self.file, root_ptr, Columns(columns))

        raise RuntimeError
