"""Uses Sqlite to save and update Expenses in the database"""
import html
import os
import sqlite3
from sqlite3 import Error

from const import (
    DATABASE_TABLES,
    DATABASE_PATH,
    EXPENSES_TABLE_NAME,
    CATEGORIES_TABLE_NAME
)

from storage.ExpensesRetrieverFactory import ExpensesRetrieverFactory

class SqliteExpensesPersister():
    """Persists Expenses data in a database"""

    def __init__(self, expenses_table_name, categories_table_name,
                 connection_provider):
        self.__expenses_table_name = expenses_table_name
        self.__categories_table_name = categories_table_name
        self.__connection_provider = connection_provider

        self.__create_categories_table()
        self.__create_expenses_table()

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

        retriever = ExpensesRetrieverFactory.create("sqlite", DATABASE_PATH,
                                        DATABASE_TABLES)

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

    def __create_expenses_table(self):
        """Creates the Expenses table in the database"""

        connection = self.__connection_provider.get_connection()
        cursor = connection.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS {table_name} (
                        expense_id  TEXT PRIMARY KEY,
                        name TEXT,
                        cost REAL,
                        purchase_date REAL,
                        category_id TEXT)"""
                        .format(table_name=self.__expenses_table_name)
        )

        connection.commit()
        connection.close()

    def __create_categories_table(self):
        """Creates the Categories table in the database"""

        connection = self.__connection_provider.get_connection()
        cursor = connection.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS {table_name} (
                        category_id  TEXT PRIMARY KEY,
                        name TEXT)"""
                        .format(table_name=self.__categories_table_name)
        )

        connection.commit()
        connection.close()
