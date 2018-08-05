import unittest
from expenses_tracker.storage.SqliteExpensesRetriever import SqliteExpensesRetriever

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
        with self.assertRaises(ValueError) as cm:
            self.expenses_table_name = None
            self.create()

        self.assertEqual(str(cm.exception), "InvalidArgument: expenses_table_name must be provided")

if __name__ is "__main__":
    unittest.main()
