from typing import Any, Type
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from ._classes.sticky_note import StickyNote
from .classes import Enum, Project, Reference, Table, TableGroup
from .exceptions import DatabaseValidationError
from .renderer.base import BaseRenderer
from .renderer.dbml.default.renderer import DefaultDBMLRenderer
from .renderer.sql.default import DefaultSQLRenderer


class Database:
    def __init__(
        self,
        sql_renderer: Type[BaseRenderer] = DefaultSQLRenderer,
        dbml_renderer: Type[BaseRenderer] = DefaultDBMLRenderer,
        allow_properties: bool = False
    ) -> None:
        self.sql_renderer = sql_renderer
        self.dbml_renderer = dbml_renderer
        self.tables: List['Table'] = []
        self.table_dict: Dict[str, 'Table'] = {}
        self.refs: List['Reference'] = []
        self.enums: List['Enum'] = []
        self.table_groups: List['TableGroup'] = []
        self.sticky_notes: List['StickyNote'] = []
        self.project: Optional['Project'] = None
        self.allow_properties = allow_properties

    def __repr__(self) -> str:
        return f"<Database>"

    def __getitem__(self, k: Union[int, str]) -> Table:
        if isinstance(k, int):
            return self.tables[k]
        elif isinstance(k, str):
            return self.table_dict[k]
        else:
            raise TypeError('indeces must be str or int')

    def __iter__(self):
        return iter(self.tables)

    def _set_database(self, obj: Any) -> None:
        obj.database = self

    def _unset_database(self, obj: Any) -> None:
        obj.database = None

    def add(self, obj: Any) -> Any:
        if isinstance(obj, Table):
            return self.add_table(obj)
        elif isinstance(obj, Reference):
            return self.add_reference(obj)
        elif isinstance(obj, Enum):
            return self.add_enum(obj)
        elif isinstance(obj, TableGroup):
            return self.add_table_group(obj)
        elif isinstance(obj, Project):
            return self.add_project(obj)
        elif isinstance(obj, StickyNote):
            return self.add_sticky_note(obj)
        else:
            raise DatabaseValidationError(f'Unsupported type {type(obj)}.')

    def add_table(self, obj: Table) -> Table:
        if obj in self.tables:
            raise DatabaseValidationError(f'{obj} is already in the database.')
        if obj.full_name in self.table_dict:
            raise DatabaseValidationError(f'Table {obj.full_name} is already in the database.')
        if obj.alias and obj.alias in self.table_dict:
            raise DatabaseValidationError(f'Table {obj.alias} is already in the database.')

        self._set_database(obj)

        self.tables.append(obj)
        self.table_dict[obj.full_name] = obj
        if obj.alias:
            self.table_dict[obj.alias] = obj
        return obj

    def add_reference(self, obj: Reference):
        for col in (*obj.col1, *obj.col2):
            if col.table and col.table.database == self:
                break
        else:
            raise DatabaseValidationError(
                'Cannot add reference. At least one of the referenced tables'
                ' should belong to this database'
            )
        if obj in self.refs:
            raise DatabaseValidationError(f'{obj} is already in the database.')

        self._set_database(obj)
        self.refs.append(obj)
        return obj

    def add_enum(self, obj: Enum) -> Enum:
        if obj in self.enums:
            raise DatabaseValidationError(f'{obj} is already in the database.')
        for enum in self.enums:
            if enum.name == obj.name and enum.schema == obj.schema:
                raise DatabaseValidationError(f'Enum {obj.schema}.{obj.name} is already in the database.')

        self._set_database(obj)
        self.enums.append(obj)
        return obj

    def add_sticky_note(self, obj: StickyNote) -> StickyNote:
        self._set_database(obj)
        self.sticky_notes.append(obj)
        return obj

    def add_table_group(self, obj: TableGroup) -> TableGroup:
        if obj in self.table_groups:
            raise DatabaseValidationError(f'{obj} is already in the database.')
        for table_group in self.table_groups:
            if table_group.name == obj.name:
                raise DatabaseValidationError(f'TableGroup {obj.name} is already in the database.')

        self._set_database(obj)
        self.table_groups.append(obj)
        return obj

    def add_project(self, obj: Project) -> Project:
        if self.project:
            self.delete_project()
        self._set_database(obj)
        self.project = obj
        return obj

    def delete(self, obj: Any) -> Any:
        if isinstance(obj, Table):
            return self.delete_table(obj)
        elif isinstance(obj, Reference):
            return self.delete_reference(obj)
        elif isinstance(obj, Enum):
            return self.delete_enum(obj)
        elif isinstance(obj, TableGroup):
            return self.delete_table_group(obj)
        elif isinstance(obj, Project):
            return self.delete_project()
        else:
            raise DatabaseValidationError(f'Unsupported type {type(obj)}.')

    def delete_table(self, obj: Table) -> Table:
        try:
            index = self.tables.index(obj)
        except ValueError:
            raise DatabaseValidationError(f'{obj} is not in the database.')
        self._unset_database(self.tables.pop(index))
        result = self.table_dict.pop(obj.full_name)
        if obj.alias:
            self.table_dict.pop(obj.alias)
        return result

    def delete_reference(self, obj: Reference) -> Reference:
        try:
            index = self.refs.index(obj)
        except ValueError:
            raise DatabaseValidationError(f'{obj} is not in the database.')
        result = self.refs.pop(index)
        self._unset_database(result)
        return result

    def delete_enum(self, obj: Enum) -> Enum:
        try:
            index = self.enums.index(obj)
        except ValueError:
            raise DatabaseValidationError(f'{obj} is not in the database.')
        result = self.enums.pop(index)
        self._unset_database(result)
        return result

    def delete_table_group(self, obj: TableGroup) -> TableGroup:
        try:
            index = self.table_groups.index(obj)
        except ValueError:
            raise DatabaseValidationError(f'{obj} is not in the database.')
        result = self.table_groups.pop(index)
        self._unset_database(result)
        return result

    def delete_project(self) -> Project:
        if self.project is None:
            raise DatabaseValidationError(f'Project is not set.')
        result = self.project
        self.project = None
        self._unset_database(result)
        return result

    @property
    def sql(self):
        '''Returs SQL of the parsed results'''
        return self.sql_renderer.render_db(self)

    @property
    def dbml(self):
        '''Generates DBML code out of parsed results'''
        return self.dbml_renderer.render_db(self)
