import os

from pathlib import Path
from unittest import TestCase

from pydbml.classes import Column
from pydbml.classes import Enum
from pydbml.classes import EnumItem
from pydbml.classes import Project
from pydbml.classes import Reference
from pydbml.classes import Table
from pydbml.classes import TableGroup
from pydbml.exceptions import SchemaValidationError
from pydbml.schema import Schema


TEST_DATA_PATH = Path(os.path.abspath(__file__)).parent / 'test_data'


class TestSchema(TestCase):
    def test_add_table(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        schema = Schema()
        res = schema.add_table(t)
        self.assertEqual(t.schema, schema)
        self.assertIs(res, t)
        self.assertIn(t, schema.tables)

    def test_add_table_bad(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        schema = Schema()
        schema.add_table(t)
        with self.assertRaises(SchemaValidationError):
            schema.add_table(t)
        t2 = Table('test_table')
        with self.assertRaises(SchemaValidationError):
            schema.add_table(t2)

    def test_delete_table(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        schema = Schema()
        schema.add_table(t)
        res = schema.delete_table(t)
        self.assertIsNone(t.schema, schema)
        self.assertIs(res, t)
        self.assertNotIn(t, schema.tables)

    def test_delete_missing_table(self) -> None:
        t = Table('test_table')
        schema = Schema()
        with self.assertRaises(SchemaValidationError):
            schema.delete_table(t)
        self.assertIsNone(t.schema, schema)

    def test_add_reference(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        schema = Schema()
        schema.add_table(t)
        c2 = Column('test2', 'integer')
        t2 = Table('test_table2')
        t2.add_column(c2)
        schema.add_table(t2)
        ref = Reference('>', c, c2)
        res = schema.add_reference(ref)
        self.assertEqual(ref.schema, schema)
        self.assertIs(res, ref)
        self.assertIn(ref, schema.refs)

    def test_add_reference_bad(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        schema = Schema()
        schema.add_table(t)
        c2 = Column('test2', 'integer')
        t2 = Table('test_table2')
        t2.add_column(c2)
        schema.add_table(t2)
        ref = Reference('>', c, c2)
        schema.add_reference(ref)
        with self.assertRaises(SchemaValidationError):
            schema.add_reference(ref)

        c3 = Column('test', 'varchar', True)
        t3 = Table('test_table')
        t3.add_column(c3)
        schema3 = Schema()
        schema3.add_table(t3)
        c32 = Column('test2', 'integer')
        t32 = Table('test_table2')
        t32.add_column(c32)
        schema3.add_table(t32)
        ref3 = Reference('>', c3, c32)
        with self.assertRaises(SchemaValidationError):
            schema.add_reference(ref3)

    def test_delete_reference(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        schema = Schema()
        schema.add_table(t)
        c2 = Column('test2', 'integer')
        t2 = Table('test_table2')
        t2.add_column(c2)
        schema.add_table(t2)
        ref = Reference('>', c, c2)
        res = schema.add_reference(ref)
        res = schema.delete_reference(ref)
        self.assertIsNone(ref.schema, schema)
        self.assertIs(res, ref)
        self.assertNotIn(ref, schema.refs)

    def test_delete_missing_reference(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        schema = Schema()
        schema.add_table(t)
        c2 = Column('test2', 'integer')
        t2 = Table('test_table2')
        t2.add_column(c2)
        schema.add_table(t2)
        ref = Reference('>', c, c2)
        with self.assertRaises(SchemaValidationError):
            schema.delete_reference(ref)
        self.assertIsNone(ref.schema)

    def test_add_enum(self) -> None:
        e = Enum('myenum', [EnumItem('a'), EnumItem('b')])
        schema = Schema()
        res = schema.add_enum(e)
        self.assertEqual(e.schema, schema)
        self.assertIs(res, e)
        self.assertIn(e, schema.enums)

    def test_add_enum_bad(self) -> None:
        e = Enum('myenum', [EnumItem('a'), EnumItem('b')])
        schema = Schema()
        schema.add_enum(e)
        with self.assertRaises(SchemaValidationError):
            schema.add_enum(e)
        e2 = Enum('myenum', [EnumItem('a2'), EnumItem('b2')])
        with self.assertRaises(SchemaValidationError):
            schema.add_enum(e2)

    def test_delete_enum(self) -> None:
        e = Enum('myenum', [EnumItem('a'), EnumItem('b')])
        schema = Schema()
        schema.add_enum(e)
        res = schema.delete_enum(e)
        self.assertIsNone(e.schema)
        self.assertIs(res, e)
        self.assertNotIn(e, schema.enums)

    def test_delete_missing_enum(self) -> None:
        e = Enum('myenum', [EnumItem('a'), EnumItem('b')])
        schema = Schema()
        with self.assertRaises(SchemaValidationError):
            schema.delete_enum(e)
        self.assertIsNone(e.schema)

    def test_add_table_group(self) -> None:
        t1 = Table('table1')
        t2 = Table('table2')
        tg = TableGroup('mytablegroup', [t1, t2])
        schema = Schema()
        res = schema.add_table_group(tg)
        self.assertEqual(tg.schema, schema)
        self.assertIs(res, tg)
        self.assertIn(tg, schema.table_groups)

    def test_add_table_group_bad(self) -> None:
        t1 = Table('table1')
        t2 = Table('table2')
        tg = TableGroup('mytablegroup', [t1, t2])
        schema = Schema()
        schema.add_table_group(tg)
        with self.assertRaises(SchemaValidationError):
            schema.add_table_group(tg)
        tg2 = TableGroup('mytablegroup', [t2])
        with self.assertRaises(SchemaValidationError):
            schema.add_table_group(tg2)

    def test_delete_table_group(self) -> None:
        t1 = Table('table1')
        t2 = Table('table2')
        tg = TableGroup('mytablegroup', [t1, t2])
        schema = Schema()
        schema.add_table_group(tg)
        res = schema.delete_table_group(tg)
        self.assertIsNone(tg.schema)
        self.assertIs(res, tg)
        self.assertNotIn(tg, schema.table_groups)

    def test_delete_missing_table_group(self) -> None:
        t1 = Table('table1')
        t2 = Table('table2')
        tg = TableGroup('mytablegroup', [t1, t2])
        schema = Schema()
        with self.assertRaises(SchemaValidationError):
            schema.delete_table_group(tg)
        self.assertIsNone(tg.schema)

    def test_add_project(self) -> None:
        p = Project('myproject')
        schema = Schema()
        res = schema.add_project(p)
        self.assertEqual(p.schema, schema)
        self.assertIs(res, p)
        self.assertIs(schema.project, p)

    def test_add_another_project(self) -> None:
        p = Project('myproject')
        schema = Schema()
        schema.add_project(p)
        p2 = Project('anotherproject')
        res = schema.add_project(p2)
        self.assertEqual(p2.schema, schema)
        self.assertIs(res, p2)
        self.assertIs(schema.project, p2)
        self.assertIsNone(p.schema)

    def test_delete_project(self) -> None:
        p = Project('myproject')
        schema = Schema()
        schema.add_project(p)
        res = schema.delete_project()
        self.assertIsNone(p.schema, schema)
        self.assertIs(res, p)
        self.assertIsNone(schema.project)

    def delete_missing_project(self) -> None:
        schema = Schema()
        with self.assertRaises(SchemaValidationError):
            schema.delete_project()

    def test_add(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        c2 = Column('test2', 'integer')
        t2 = Table('test_table2')
        t2.add_column(c2)
        e = Enum('myenum', [EnumItem('a'), EnumItem('b')])
        schema = Schema()
        res = schema.add(t, t2, e)
        self.assertEqual(res, [t, t2, e])
        self.assertEqual(t.schema, schema)
        self.assertIn(t, schema.tables)
        self.assertEqual(t2.schema, schema)
        self.assertIn(t2, schema.tables)
        self.assertEqual(e.schema, schema)
        self.assertIn(e, schema.enums)
# TODO: unset schema if error
