import re
import unittest
from expense.Tag import Tag
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
        self.connection = Connection(self.execute_callback, self.fetchall_callback)

    def get_connection(self):
        return self.connection

    def get_queries(self):
        if not self.connection:
            return []

        return self.connection.get_queries()

class Connection:
    def __init__(self, execute_callback=None, fetchall_callback=None):
        self.execute_callback = execute_callback
        self.fetchall_callback = fetchall_callback
        self.cursor_object = Cursor(self.execute_callback, self.fetchall_callback)

    def cursor(self):
        return self.cursor_object

    def get_queries(self):
        if not self.cursor_object:
            return []

        return self.cursor_object.db_queries

class Cursor:
    def __init__(self, execute_callback=None, fetchall_callback=None):
        self.execute_callback = execute_callback
        self.fetchall_callback = fetchall_callback
        self.db_queries = []

    def execute(self, query):
        self.db_queries.append(query)

        if self.execute_callback:
            return self.execute_callback(query)

        return 112

    def fetchall(self):
        if self.fetchall_callback:
            return self.fetchall_callback()

        if self.db_queries[-1].startswith("PRAGMA"):
                return [(0, "fake_column_name", "TEXT")]

        return []

class TestSqliteExpensesRetriever(unittest.TestCase):
    def create(self):
        return SqliteExpensesRetriever(self.database_tables,
                                       self.connection_provider)

    def setUp(self):
        self.expenses_table_name = "expenses"
        self.categories_table_name = "categories"
        self.tags_table_name = "tags"
        self.expense_tags_table_name = "expense_tags"

        self.database_tables = {
            "expenses": self.expenses_table_name,
            "categories": self.categories_table_name,
            "tags": self.tags_table_name,
            "expense_tags": self.expense_tags_table_name
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
                "InvalidArgument:.*database_tables.tags"),
            "expense_tags": (
                validate_non_empty_string,
                "InvalidArgument:.*database_tables.expense_tags")
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
        self.connection_provider = ConnectionProvider()
        self.sut = self.create()

        self.sut.ensure_necessary_tables_exist()

        expected_db_query = "CREATE TABLE IF NOT EXISTS {} (expense_id" \
                            " TEXT PRIMARY KEY, name TEXT, cost REAL," \
                            " purchase_date REAL, category_id TEXT)" \
                            "".format(self.expenses_table_name)

        self.assertEqual(
            self.connection_provider.get_queries()[0],
            expected_db_query
        )

    def test_ensures_categories_table_exists_in_database(self):
        self.connection_provider = ConnectionProvider()
        self.sut = self.create()

        self.sut.ensure_necessary_tables_exist()

        expected_db_query = "CREATE TABLE IF NOT EXISTS {} (category_id" \
                            " TEXT PRIMARY KEY, name TEXT)".format(
                                self.categories_table_name)

        self.assertEqual(
            self.connection_provider.get_queries()[7],
            expected_db_query
        )

    def test_ensures_tags_table_exists_in_database(self):
        self.connection_provider = ConnectionProvider()
        self.sut = self.create()

        self.sut.ensure_necessary_tables_exist()

        expected_db_query = "CREATE TABLE IF NOT EXISTS {} (tag_id" \
                            " TEXT PRIMARY KEY, name TEXT)".format(
                                self.tags_table_name)

        self.assertEqual(
            self.connection_provider.get_queries()[11],
            expected_db_query
        )

    def test_ensures_expense_tags_table_exists_in_database(self):
        self.connection_provider = ConnectionProvider()
        self.sut = self.create()

        self.sut.ensure_necessary_tables_exist()

        expected_db_query = "CREATE TABLE IF NOT EXISTS {} (" \
                            "id INTEGER PRIMARY KEY AUTOINCREMENT" \
                            ", expense_id TEXT, tag_id TEXT)".format(
                                self.expense_tags_table_name)

        self.assertEqual(
            self.connection_provider.get_queries()[15],
            expected_db_query
        )

    def test_retrieves_tags(self):
        db_queries = []
        db_response = [
            ("uuid4-1", "some tag"),
            ("uuid4-2", "other tag")
        ]

        def execute_callback(query):
            db_queries.append(query)

        def fetchall_callback():
            expected_query = "SELECT * FROM {} ORDER BY name ASC".format(
                                self.tags_table_name)

            if db_queries[-1] == expected_query:
                return db_response

        self.connection_provider = ConnectionProvider(
                                    execute_callback=execute_callback,
                                    fetchall_callback=fetchall_callback)

        self.sut = self.create()

        expected_tags = [
            Tag(db_response[0][0], db_response[0][1]),
            Tag(db_response[1][0], db_response[1][1])
        ]

        self.assertEqual(expected_tags, self.sut.retrieve_tags())

if __name__ is "__main__":
    unittest.main()
