import re
import unittest
from expense.Tag import Tag
from storage.SqliteExpensesPersister import SqliteExpensesPersister
from tests.TestValidationUtils import (
    validate_dict,
    validate_non_empty_string,
    validate_object_with_methods,
    validate_provided
)

class ConnectionProviderMock:
    def __init__(self, execute_callback=None, fetchall_callback=None):
        self.execute_callback = execute_callback
        self.fetchall_callback = fetchall_callback

    def get_connection(self):
        return ConnectionMock(self.execute_callback, self.fetchall_callback)

class ConnectionMock:
    def __init__(self, execute_callback=None, fetchall_callback=None):
        self.execute_callback = execute_callback
        self.fetchall_callback = fetchall_callback

    def cursor(self):
        return CursorMock(self.execute_callback, self.fetchall_callback)

    def commit(self):
        return None

    def close(self):
        return None

class CursorMock:
    def __init__(self, execute_callback=None, fetchall_callback=None):
        self.execute_callback = execute_callback
        self.fetchall_callback = fetchall_callback

    def execute(self, query):
        if self.execute_callback:
            return self.execute_callback(query)

        return 112

    def fetchall(self):
        if self.fetchall_callback:
            return self.fetchall_callback()

        return []

class TestSqliteExpensesPersister(unittest.TestCase):
    def create(self):
        return SqliteExpensesPersister(self.database_tables,
                                       self.connection_provider)

    def setUp(self):
        self.expenses_table_name = "expenses"
        self.categories_table_name = "categories"
        self.tags_table_name = "tags"

        self.database_tables = {
            "expenses": self.expenses_table_name,
            "categories": self.categories_table_name,
            "tags": self.tags_table_name
        }

        self.connection_provider = ConnectionProviderMock()
        self.sut = self.create()

    def test_validates_database_tables(self):
        def validate_database_tables(value):
            self.database_tables = value
            self.create()

        validator_map = {
            "expenses": (
                validate_non_empty_string,
                "InvalidArgument:.*database_tables.expenses"),
            "categories": (
                validate_non_empty_string,
                "InvalidArgument:.*database_tables.categories"),
            "tags": (
                validate_non_empty_string,
                "InvalidArgument:.*database_tables.tags")
        }

        validate_dict(self, validate_database_tables, self.database_tables,
                      validator_map)

    def test_connection_provider_validation(self):
        def validate_existence(value):
            with self.assertRaises(ValueError) as cm:
                self.connection_provider = value
                self.create()

            self.assertTrue(
                re.compile("InvalidArgument:.*connection_provider")
                .match(str(cm.exception))
            )

        def validate_methods(value, method_name):
            with self.assertRaises(ValueError) as cm:
                self.connection_provider = value
                self.create()


            self.assertTrue(
                re.compile("InvalidArgument:.*connection_provider.*"
                           "{method_name}".format(method_name=method_name)
                ).match(str(cm.exception))
            )

        validate_provided(validate_existence)
        validate_object_with_methods(self, ["get_connection"], validate_methods)

    def test_persists_tags_and_returns_them(self):
        db_queries = []

        def execute_callback(query):
            db_queries.append(query)

        self.connection_provider = ConnectionProviderMock(
                                    execute_callback=execute_callback)

        self.sut = self.create()

        tags = [
            Tag("id-1", "first tag"),
            Tag("id-2", "other tag")
        ]

        result = self.sut.persist_tags(tags)

        expected_query = "INSERT INTO {} (tag_id, name) " \
                            "VALUES ('id-1', 'first tag'), " \
                                "('id-2', 'other tag')".format(
                                    self.tags_table_name
                                )

        self.assertIn(expected_query, db_queries)
        self.assertEqual(tags, result)

    def test_does_not_persist_tags_if_none_provided_and_returns_none(self):
        db_queries = []

        def execute_callback(query):
            db_queries.append(query)

        self.connection_provider = ConnectionProviderMock(
                                    execute_callback=execute_callback)

        self.sut = self.create()

        result = self.sut.persist_tags(None)

        self.assertEqual(db_queries, [])
        self.assertEqual(result, None)

    def test_does_not_persist_tags_that_already_exist(self):
        db_queries = []

        def execute_callback(query):
            db_queries.append(query)

        def fetchall_callback():
            query_for_existing_tag = "SELECT * FROM {} WHERE name " \
                                "LIKE 'first tag'".format(self.tags_table_name)

            if db_queries[-1] == query_for_existing_tag:
                return [("id-X", "first tag")]

            return []

        self.connection_provider = ConnectionProviderMock(
                                    execute_callback=execute_callback,
                                    fetchall_callback=fetchall_callback)

        self.sut = self.create()

        tags = [
            Tag("id-1", "first tag"),
            Tag("id-2", "other tag")
        ]

        result = self.sut.persist_tags(tags)

        expected_query = "INSERT INTO {} (tag_id, name) " \
                            "VALUES ('id-2', 'other tag')".format(
                                    self.tags_table_name
                                )

        expected_tags = [Tag("id-X", "first tag"), tags[-1]]

        self.assertIn(expected_query, db_queries)
        self.assertListEqual(expected_tags, result)

if __name__ is "__main__":
    unittest.main()
