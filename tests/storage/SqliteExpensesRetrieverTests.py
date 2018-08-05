import re
import unittest
from expenses_tracker.storage.SqliteExpensesRetriever import SqliteExpensesRetriever
from expenses_tracker.tests.TestValidationUtils import validate_non_empty_string

class ConnectionProvider:
    def get_connection(self):
        return Connection()

class Connection:
    def cursor(self):
        return Cursor()

class Cursor:
    def execute(self, query):
        return 112

    def fetchall(self):
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

if __name__ is "__main__":
    unittest.main()
