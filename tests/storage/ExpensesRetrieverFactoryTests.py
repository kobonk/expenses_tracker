import unittest

from tests.TestValidationUtils import (
    validate_non_empty_string,
    validate_dict_keys
)

from const import DATABASE_TYPE
from storage.ExpensesRetrieverFactory import ExpensesRetrieverFactory
from storage.ExpensesRetrieverBase import ExpensesRetrieverBase


class TestExpensesRetrieverFactory(unittest.TestCase):
    def create(self, type="xyz", database_path="/etc/expenses_tracker.db",
               database_tables={
                   "expenses": "xyz",
                   "categories": "xyz",
                   "tags": "xyz"
                   }
                ):

        return ExpensesRetrieverFactory.create(type, database_path,
                                               database_tables)

    def test_create_throws_with_no_type(self):
        def validate_database_type(value):
            self.create(type=None)

        validate_non_empty_string(self, validate_database_type,
                                  "InvalidArgument:.*type")

    def test_create_throws_with_no_db_path(self):
        def validate_database_path(value):
            self.create(database_path=None)

        validate_non_empty_string(self, validate_database_path,
                                  "InvalidArgument:.*database_path")

    def test_create_throws_with_invalid_db_tables_dict(self):
        def validate_database_tables(value):
            self.create(database_tables=value)

        keys = ["expenses", "categories", "tags"]

        validate_dict_keys(self, validate_database_tables,
                           "InvalidArgument:.*database_tables", keys)

    def test_create_returns_none_for_unsupported_db_type(self):
        sut = self.create(type="unsupported")

        self.assertIsNone(sut)

    def test_create_returns_expensesretriever_instance(self):
        sut = self.create(type=DATABASE_TYPE)

        self.assertIsInstance(sut, ExpensesRetrieverBase)
