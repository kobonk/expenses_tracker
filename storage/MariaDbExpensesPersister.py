"""Uses MariaDb to save and update Expenses in the database"""
from typing import Tuple
import html
from datetime import date

from const import DATABASE_TYPE
from validation_utils import validate_dict, validate_non_empty_string
from expense.Expense import Expense, convert_date_string_to_timestamp
from storage.ExpensesRetrieverFactory import ExpensesRetrieverFactory
from storage.ExpensesPersisterBase import ExpensesPersisterBase
from storage.DbQueryProvider import DbQueryProvider, DbQueryType

SaveExpenseParams = Tuple[str, int, int, str, int, int, int]

class MariaDbExpensesPersister(ExpensesPersisterBase):
    """Persists Expenses data in a database"""

    def __init__(self, database_tables, connection_provider, query_provider: DbQueryProvider):
        self.__validate_database_tables(database_tables)
        self.__validate_connection_provider(connection_provider)

        self.__categories_table_name = database_tables["categories"]
        self.__expenses_table_name = database_tables["expenses"]
        self.__connection_provider = connection_provider
        self.__query_provider = query_provider

    def add_expense(self, expense : Expense):
        """Adds a new Expense to database"""
        if not expense:
            return None

        query = self.__query_provider.create_query(DbQueryType.SAVE_EXPENSE)
        purchase_date = date.fromtimestamp(expense.get_purchase_date())

        params: SaveExpenseParams = (
          expense.get_name(),
          expense.get_cost(),
          expense.get_purchase_date(),
          expense.get_category().get_category_id(),
          purchase_date.day,
          purchase_date.month,
          purchase_date.year
        )

        self.__connection_provider.execute_query(query, params)

        print("Added: {}".format(expense))

    def update_expense(self, expense_id, changes):
        """Updates existing Expense in the database"""

        updates = []

        for key, value in changes.items():
          if key == 'purchase_date':
            timestamp = convert_date_string_to_timestamp(value)
            purchase_date = date.fromtimestamp(timestamp)

            updates.append("{} = '{}'".format(key, timestamp))
            updates.append("day = '{}'".format(purchase_date.day))
            updates.append("month = '{}'".format(purchase_date.month))
            updates.append("year = '{}'".format(purchase_date.year))
          elif key == 'cost':
            updates.append("{} = {}".format(key, value))
          else:
            updates.append("{} = '{}'".format(key, value))

        query = "UPDATE {} SET {}  WHERE expense_id = {}".format(
                self.__expenses_table_name,
                ", ".join(updates),
                expense_id)

        print(query)

        self.__connection_provider.execute_query(query)

        retriever = ExpensesRetrieverFactory.create(DATABASE_TYPE)
        expense = retriever.retrieve_expense(expense_id)

        print("Updated: {}".format(expense))

        return expense

    def add_category(self, category):
        """Adds a new Category to the database"""

        query = "INSERT INTO {} (name) VALUES ('{}', '{}')".format(
                    self.__categories_table_name,
                    html.escape(category.get_name()))

        self.__connection_provider.execute_query(query)

        print("Added: {}".format(category))

    def __validate_connection_provider(self, connection_provider):
        if not connection_provider:
            raise ValueError("InvalidArgument: connection_provider must be "
                                "provided")

        if (not hasattr(connection_provider, "execute_query") or
            not callable(connection_provider.execute_query)):
            raise ValueError("InvalidArgument: connection_provider must have "
                                "execute_query method")

    def __validate_database_tables(self, database_tables):
        validator_map = {
            "expenses": validate_non_empty_string,
            "categories": validate_non_empty_string,
        }

        validate_dict(database_tables, "database_tables", validator_map)
