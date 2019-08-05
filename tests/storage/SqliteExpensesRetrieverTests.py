import re
import unittest
from storage.SqliteExpensesRetriever import SqliteExpensesRetriever
from tests.TestValidationUtils import (
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
        return SqliteExpensesRetriever(self.expenses_table_name,
                                       self.categories_table_name,
                                       self.connection_provider)

    def setUp(self):
        self.expenses_table_name = "expenses"
        self.categories_table_name = "categories"
        self.connection_provider = ConnectionProvider()
        self.sut = self.create()

    def test_expenses_table_name_validation(self):
        def validate_expenses_table_name(value):
            self.expenses_table_name = value
            self.create()

        validate_non_empty_string(self, validate_expenses_table_name,
                                  "InvalidArgument:.*expenses_table_name")

    def test_categories_table_name_validation(self):
        def validate_categories_table_name(value):
            self.categories_table_name = value
            self.create()

        validate_non_empty_string(self, validate_categories_table_name,
                                  "InvalidArgument:.*categories_table_name")

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

        self.connection_provider = ConnectionProvider(fetchall_callback=fetchall_callback)
        self.sut = self.create()

        self.assertEqual(
            self.sut.retrieve_common_expense_cost("TEST"),
            4321
        )

    def test_retrieve_common_expense_cost_zero_value_if_infrequent(self):
        def fetchall_callback():
            return [('Test Expense', 4321, 4)]

        self.connection_provider = ConnectionProvider(fetchall_callback=fetchall_callback)
        self.sut = self.create()

        self.assertEqual(
            self.sut.retrieve_common_expense_cost("TEST"),
            0
        )

if __name__ is "__main__":
    unittest.main()
