import re
import unittest
from unittest.mock import patch

from expense.Category import Category
from expense.Expense import Expense
from expense.Tag import Tag
from expense.Shop import Shop
from storage.SqliteDatabaseConnectionProvider import SqliteDatabaseConnectionProvider
from storage.SqliteExpensesPersister import SqliteExpensesPersister
from storage.SqliteExpensesRetriever import SqliteExpensesRetriever

from tests.TestValidationUtils import (
    validate_dict,
    validate_non_empty_string,
    validate_object_with_methods,
    validate_provided
)

class TestSqliteExpensesPersister(unittest.TestCase):
    def create(self):
        return SqliteExpensesPersister(self.database_tables,
                                       self.connection_provider)

    def setUp(self):
        self.expenses_table_name = "expenses"
        self.categories_table_name = "categories"
        self.tags_table_name = "tags"
        self.expense_tags_table_name = "expense_tags"
        self.shops_table_name = "shops"
        self.suggestions_table_name = "expense_suggestions"

        self.database_tables = {
            "expenses": self.expenses_table_name,
            "categories": self.categories_table_name,
            "tags": self.tags_table_name,
            "expense_tags": self.expense_tags_table_name,
            "shops": self.shops_table_name,
            "suggestions": self.suggestions_table_name
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

    def test_persists_tags_and_returns_them(self):
        self.sut = self.create()

        tags = [
            Tag("id-1", "first tag"),
            Tag("id-2", "other tag")
        ]

        self.assertEqual(tags, self.sut.persist_tags(tags))

        rows = self.connection_provider.execute_query("SELECT name, tag_id " \
            "FROM {}".format(self.tags_table_name))

        expected_rows = [("first tag", "id-1"), ("other tag", "id-2")]

        self.assertEqual(rows, expected_rows)

    def test_does_not_persist_not_provided_tags_and_returns_empty_list(self):
        self.sut = self.create()

        self.assertEqual([], self.sut.persist_tags(None))

        rows = self.connection_provider.execute_query("SELECT name, tag_id " \
            "FROM {}".format(self.tags_table_name))

        self.assertEqual(rows, [])

    def test_does_not_persist_empty_list_of_tags_and_returns_empty_list(self):
        self.sut = self.create()

        self.assertEqual([], self.sut.persist_tags([]))

        rows = self.connection_provider.execute_query("SELECT name, tag_id " \
            "FROM {}".format(self.tags_table_name))

        self.assertEqual(rows, [])

    def test_does_not_persist_tags_that_already_exist(self):
        self.sut = self.create()

        tags = [
            Tag("id-1", "first tag"),
            Tag("id-2", "other tag")
        ]

        self.connection_provider.execute_query("INSERT INTO {} (tag_id, name)" \
            " VALUES ('id-X', 'first tag')".format(self.tags_table_name))

        result = self.sut.persist_tags(tags)

        expected_tags = [Tag("id-X", "first tag"), tags[-1]]

        self.assertListEqual(expected_tags, result)

    def test_persists_expense_tags_and_relations(self):
        self.sut = self.create()

        category = Category("category-id-1", "Some Category")
        tags = [Tag("id-1", "first tag"), Tag("id-2", "other tag")]
        expense = Expense("expense-id-1", "TEST", 1, 1566172800, category, tags)

        retriever = SqliteExpensesRetriever(self.database_tables,
                                            self.connection_provider)

        self.sut.persist_expense_tags(expense)

        self.assertListEqual(tags, retriever.retrieve_tags())

    @patch('builtins.print')
    def test_persists_shops(self, _mock_print):
        self.sut = self.create()

        self.sut.persist_shop(Shop(1, "Wallmart"))
        self.sut.persist_shop(Shop(2, "7Eleven"))

        rows = self.connection_provider.execute_query(
            "SELECT * FROM {table}".format(table=self.shops_table_name)
        )

        self.assertListEqual(rows, [(1, "Wallmart"), (2, "7Eleven")])

if __name__ == "__main__":
    unittest.main()
