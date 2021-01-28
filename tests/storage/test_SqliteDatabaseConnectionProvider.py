import re
import unittest
from expense.Tag import Tag
from storage.SqliteDatabaseConnectionProvider import SqliteDatabaseConnectionProvider
from tests.TestValidationUtils import validate_dict, validate_non_empty_string

class TestSqliteDatabaseConnectionProvider(unittest.TestCase):
    def create(self):
        return SqliteDatabaseConnectionProvider(self.database_path,
                                                self.database_tables)

    def setUp(self):
        self.database_path = ":memory:"

        self.database_tables = {
            "expenses": "expenses",
            "categories": "categories",
            "tags": "tags",
            "expense_tags": "expense_tags"
        }

        self.sut = self.create()

    def test_validates_database_path(self):
        def validate_database_path(value):
            self.database_path = value
            self.create()

        validate_non_empty_string(self, validate_database_path,
                                  "InvalidArgument:.*database_path")

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

    def test_ensures_expenses_table_exist_in_database(self):
        self.__check_if_table_exists(self.database_tables["expenses"])

    def test_ensures_categories_table_exists_in_database(self):
        self.__check_if_table_exists(self.database_tables["categories"])

    def test_ensures_tags_table_exists_in_database(self):
        self.__check_if_table_exists(self.database_tables["tags"])

    def test_ensures_expense_tags_table_exists_in_database(self):
        self.__check_if_table_exists(self.database_tables["expense_tags"])

    def __check_if_table_exists(self, table_name):
        query = "PRAGMA table_info('{}')".format(table_name)

        self.assertTrue(len(self.sut.execute_query(query)) == 0)

        self.sut.ensure_necessary_tables_exist()

        self.assertTrue(len(self.sut.execute_query(query)) > 0)

if __name__ == "__main__":
    unittest.main()
