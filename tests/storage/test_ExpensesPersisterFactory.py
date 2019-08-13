import unittest

from tests.TestValidationUtils import validate_non_empty_string
from const import DATABASE_TYPE
from storage.ExpensesPersisterFactory import ExpensesPersisterFactory
from storage.ExpensesPersisterBase import ExpensesPersisterBase


class TestExpensesPersisterFactory(unittest.TestCase):
    def create(self, type="xyz"):
        return ExpensesPersisterFactory.create(type)

    def test_create_throws_with_invalid_type(self):
        def validate_database_type(value):
            self.create(type=None)

        validate_non_empty_string(self, validate_database_type,
                                  "InvalidArgument:.*type")

    def test_create_returns_none_for_unsupported_db_type(self):
        sut = self.create(type="unsupported")

        self.assertIsNone(sut)

    def test_create_returns_expensespersister_instance(self):
        sut = self.create(type=DATABASE_TYPE)

        self.assertIsInstance(sut, ExpensesPersisterBase)
