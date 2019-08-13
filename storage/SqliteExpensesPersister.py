"""Uses Sqlite to save and update Expenses in the database"""
import html
import os
import sqlite3
from sqlite3 import Error

from validation_utils import validate_dict, validate_non_empty_string
from storage.ExpensesRetrieverFactory import ExpensesRetrieverFactory
from storage.ExpensesPersisterBase import ExpensesPersisterBase

class SqliteExpensesPersister(ExpensesPersisterBase):
    """Persists Expenses data in a database"""

    def __init__(self, database_tables, connection_provider):
        self.__validate_database_tables(database_tables)
        self.__validate_connection_provider(connection_provider)

        self.__expenses_table_name = database_tables["expenses"]
        self.__categories_table_name = database_tables["categories"]
        self.__tags_table_name = database_tables["tags"]
        self.__connection_provider = connection_provider

    def add_expense(self, expense):
        """Adds a new Expense to database"""

        connection = self.__connection_provider.get_connection()
        cursor = connection.cursor()

        cursor.execute("""INSERT INTO {table_name} (
                    expense_id,
                    name,
                    cost,
                    purchase_date,
                    category_id
                ) VALUES (
                    '{e_id}',
                    '{e_name}',
                    {e_cost},
                    {e_purchase_date},
                    '{e_category_id}')"""
                .format(
                    table_name=self.__expenses_table_name,
                    e_id=expense.get_expense_id(),
                    e_name=html.escape(expense.get_name()),
                    e_cost=expense.get_cost(),
                    e_purchase_date=expense.get_purchase_date(),
                    e_category_id=html.escape(expense.get_category()
                                              .get_category_id())
                )
        )

        connection.commit()
        connection.close()

        print("Added: {}".format(expense))

    def update_expense(self, expense_id, changes):
        """Updates existing Expense in the database"""

        connection = self.__connection_provider.get_connection()
        cursor = connection.cursor()

        updates = ", ".join(["""{} = '{}'""".format(key, value) for key, value in changes.items()])

        cursor.execute("""UPDATE {} SET {} WHERE expense_id = '{}'"""
            .format(self.__expenses_table_name, updates, expense_id)
        )

        connection.commit()
        connection.close()

        retriever = ExpensesRetrieverFactory.create("sqlite")

        expense = retriever.retrieve_expense(expense_id)

        print("Updated: {}".format(expense))

        return expense

    def add_category(self, category):
        """Adds a new Category to the database"""

        connection = self.__connection_provider.get_connection()
        cursor = connection.cursor()

        cursor.execute("""INSERT INTO {table_name} (
                    category_id, name
                ) VALUES ('{id}', '{name}')""".format(
                    table_name=self.__categories_table_name,
                    id=html.escape(category.get_category_id()),
                    name=html.escape(category.get_name())
                )
        )

        connection.commit()
        connection.close()

        print("Added: {}".format(category))

    def persist_tags(self, tags=[]):
        """Adds Tags to the database"""

        if not tags:
            return None

        connection = self.__connection_provider.get_connection()
        cursor = connection.cursor()
        tag_entries = ["', '".join([tag.get_tag_id(), tag.get_name()]) for tag in tags]

        cursor.execute("INSERT INTO {table_name} (tag_id, name) VALUES " \
                       "('{tags}')".format(
                    table_name=self.__tags_table_name,
                    tags="'), ('".join(tag_entries)))

        connection.commit()
        connection.close()

        return tags

    def __validate_connection_provider(self, connection_provider):
        if not connection_provider:
            raise ValueError("InvalidArgument: connection_provider must be "
                                "provided")

        if (not hasattr(connection_provider, "get_connection") or
            not callable(connection_provider.get_connection)):
            raise ValueError("InvalidArgument: connection_provider must have "
                                "get_connection method")

    def __validate_database_tables(self, database_tables):
        validator_map = {
            "expenses": validate_non_empty_string,
            "categories": validate_non_empty_string,
            "tags": validate_non_empty_string
        }

        validate_dict(database_tables, "database_tables", validator_map)
