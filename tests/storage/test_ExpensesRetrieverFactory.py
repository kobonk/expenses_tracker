import unittest

from tests.TestValidationUtils import validate_non_empty_string
from const import DATABASE_TYPE
from storage.ExpensesRetrieverFactory import ExpensesRetrieverFactory
from storage.ExpensesRetrieverBase import ExpensesRetrieverBase


class TestExpensesRetrieverFactory(unittest.TestCase):
    def create(self, type="xyz"):
        return ExpensesRetrieverFactory.create(type)

    def test_create_throws_with_invalid_type(self):
        def validate_database_type(value):
            self.create(type=None)

        validate_non_empty_string(self, validate_database_type,
                                  "InvalidArgument:.*type")

    def test_create_returns_none_for_unsupported_db_type(self):
        sut = self.create(type="unsupported")

        self.assertIsNone(sut)

    def test_create_returns_expensesretriever_instance(self):
        sut = self.create(type=DATABASE_TYPE)

        self.assertIsInstance(sut, ExpensesRetrieverBase)
