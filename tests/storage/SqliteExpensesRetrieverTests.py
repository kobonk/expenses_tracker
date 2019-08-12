import re
import unittest
from storage.SqliteExpensesRetriever import SqliteExpensesRetriever
from tests.TestValidationUtils import (
    validate_dict,
    validate_non_empty_string,
    validate_object_with_methods,
    validate_provided
)

class ConnectionProvider:
    def __init__(self, execute_callback=None, fetchall_callback=None):
        self.execute_callback = execute_callback
        self.fetchall_callback = fetchall_callback

    def get_connection(self):
        return Connection(self.execute_callback, self.fetchall_callback)

class Connection:
    def __init__(self, execute_callback=None, fetchall_callback=None):
        self.execute_callback = execute_callback
        self.fetchall_callback = fetchall_callback

    def cursor(self):
        return Cursor(self.execute_callback, self.fetchall_callback)

class Cursor:
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

        return 123

class TestSqliteExpensesRetriever(unittest.TestCase):
    def create(self):
        return SqliteExpensesRetriever(self.database_tables,
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

        self.connection_provider = ConnectionProvider()
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

    def test_retrieve_common_expense_cost_value_if_frequent(self):
        def fetchall_callback():
            return [('Test Expense', 4321, 8)]

        self.connection_provider = ConnectionProvider(
                                    fetchall_callback=fetchall_callback)
        self.sut = self.create()

        self.assertEqual(
            self.sut.retrieve_common_expense_cost("TEST"),
            4321
        )

    def test_retrieve_common_expense_cost_zero_value_if_infrequent(self):
        def fetchall_callback():
            return [('Test Expense', 4321, 4)]

        self.connection_provider = ConnectionProvider(
                                    fetchall_callback=fetchall_callback)
        self.sut = self.create()

        self.assertEqual(
            self.sut.retrieve_common_expense_cost("TEST"),
            0
        )

    def test_ensures_expenses_table_exist_in_database(self):
        db_queries = []

        def execute_callback(query):
            db_queries.append(query)

        def fetchall_callback():
            if db_queries[-1].startswith("PRAGMA"):
                return [(0, "fake_column_name", "TEXT")]

        self.connection_provider = ConnectionProvider(
                                    execute_callback=execute_callback,
                                    fetchall_callback=fetchall_callback)
        self.sut = self.create()

        self.sut.ensure_necessary_tables_exist()

        expected_db_query = "CREATE TABLE IF NOT EXISTS {} (expense_id" \
                            " TEXT PRIMARY KEY, name TEXT, cost REAL," \
                            " purchase_date REAL, category_id TEXT," \
                            " tag_ids TEXT)".format(self.expenses_table_name)

        self.assertEqual(db_queries[0], expected_db_query)

    def test_ensures_categories_table_exists_in_database(self):
        db_queries = []

        def execute_callback(query):
            db_queries.append(query)

        def fetchall_callback():
            if db_queries[-1].startswith("PRAGMA"):
                return [(0, "fake_column_name", "TEXT")]

        self.connection_provider = ConnectionProvider(
                                    execute_callback=execute_callback,
                                    fetchall_callback=fetchall_callback)

        self.sut = self.create()

        self.sut.ensure_necessary_tables_exist()

        expected_db_query = "CREATE TABLE IF NOT EXISTS {} (category_id" \
                            " TEXT PRIMARY KEY, name TEXT)".format(
                                self.categories_table_name)

        self.assertEqual(db_queries[8], expected_db_query)

    def test_ensures_tags_table_exists_in_database(self):
        db_queries = []

        def execute_callback(query):
            db_queries.append(query)

        def fetchall_callback():
            if db_queries[-1].startswith("PRAGMA"):
                return [(0, "fake_column_name", "TEXT")]

        self.connection_provider = ConnectionProvider(
                                    execute_callback=execute_callback,
                                    fetchall_callback=fetchall_callback)

        self.sut = self.create()

        self.sut.ensure_necessary_tables_exist()

        expected_db_query = "CREATE TABLE IF NOT EXISTS {} (tag_id" \
                            " TEXT PRIMARY KEY, name TEXT)".format(
                                self.tags_table_name)

        self.assertEqual(db_queries[12], expected_db_query)

if __name__ is "__main__":
    unittest.main()
