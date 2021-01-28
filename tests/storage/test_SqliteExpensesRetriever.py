import re
import unittest
from unittest.mock import patch

from expense.Category import Category
from expense.Expense import Expense
from expense.Tag import Tag
from storage.SqliteDatabaseConnectionProvider import SqliteDatabaseConnectionProvider
from storage.SqliteExpensesPersister import SqliteExpensesPersister
from storage.SqliteExpensesRetriever import SqliteExpensesRetriever

from tests.TestValidationUtils import (
    validate_dict,
    validate_non_empty_string,
    validate_object_with_methods,
    validate_provided
)


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

        self.connection_provider = SqliteDatabaseConnectionProvider(":memory:",
                                                self.database_tables)

        self.connection_provider.ensure_necessary_tables_exist()

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
        validate_object_with_methods(self, ["execute_query"], validate_methods)

    def test_retrieve_common_expense_cost_value_if_frequent(self):
        self.sut = self.create()

        query = "INSERT INTO {} (name, cost) VALUES " \
            "('TEST', 4), ('TEST', 3), ('TEST', 4), ('TEST', 4), " \
            "('OTHER', 2), ('OTHER', 2), " \
            "('TEST', 1), ('TEST', 1), ('TEST', 4), ('TEST', 4)".format(
                self.expenses_table_name
            )

        self.connection_provider.execute_query(query)

        self.assertEqual(self.sut.retrieve_common_expense_cost("TEST"), 4)

    def test_retrieve_common_expense_cost_zero_value_if_infrequent(self):
        self.sut = self.create()

        query = "INSERT INTO {} (name, cost) VALUES " \
            "('OTHER', 2), ('OTHER', 2), " \
            "('TEST', 1), ('TEST', 1), ('TEST', 4), ('TEST', 4)".format(
                self.expenses_table_name
            )

        self.connection_provider.execute_query(query)

        self.assertEqual(self.sut.retrieve_common_expense_cost("TEST"), 0)

    def test_retrieves_tags(self):
        self.sut = self.create()

        tag_data = [
            ("uuid4-2", "other tag"),
            ("uuid4-1", "some tag")
        ]

        expected_tags = [
            Tag(tag_data[0][0], tag_data[0][1]),
            Tag(tag_data[1][0], tag_data[1][1])
        ]

        query = "INSERT INTO {} (tag_id, name) VALUES" \
            "('uuid4-1', 'some tag'), " \
            "('uuid4-2', 'other tag')".format(
                self.tags_table_name
            )

        self.connection_provider.execute_query(query)

        self.assertEqual(expected_tags, self.sut.retrieve_tags())

    @patch('builtins.print')
    def test_retrieves_expense_tags(self, _mock_print):
        self.sut = self.create()

        persister = SqliteExpensesPersister(
            self.database_tables, self.connection_provider)

        tags = [
            Tag("tag-1", "First Tag"),
            Tag("tag-2", "Second Tag"),
            Tag("tag-3", "Third Tag")
        ]

        category = Category("category-1", "Some Category")

        expenses = [
            Expense("ex-1", "First Expense", 11, 1566172800, category, tags[:2]),
            Expense("ex-2", "Other Expense", 22, 1566172800, category, tags[1:])
        ]

        for expense in expenses:
            persister.add_expense(expense)

        self.assertListEqual(tags[:2], self.sut.retrieve_expense_tags(expenses[0]))

if __name__ == "__main__":
    unittest.main()
