"""Uses Sqlite to save and update Expenses in the database"""
import html
import os
import sqlite3
from sqlite3 import Error

from const import DATABASE_TYPE
from validation_utils import validate_dict, validate_non_empty_string
from expense.Expense import Expense
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
        self.__expense_tags_table_name = database_tables["expense_tags"]
        self.__connection_provider = connection_provider

    def add_expense(self, expense : Expense):
        """Adds a new Expense to database"""
        if not expense:
            return None

        query = "INSERT INTO {table_name} (expense_id, name, cost, " \
            "purchase_date, category_id ) VALUES ('{e_id}', '{e_name}', " \
            "{e_cost}, {e_purchase_date}, '{e_category_id}')".format(
                table_name=self.__expenses_table_name,
                e_id=expense.get_expense_id(),
                e_name=html.escape(expense.get_name()),
                e_cost=expense.get_cost(),
                e_purchase_date=expense.get_purchase_date(),
                e_category_id=html.escape(expense.get_category()
                                            .get_category_id())
            )

        self.__connection_provider.execute_query(query)
        self.persist_expense_tags(expense)

        print("Added: {}".format(expense))

    def update_expense(self, expense_id, changes):
        """Updates existing Expense in the database"""

        updates = ["{} = '{}'".format(k, v) for k, v in changes.items()]
        query = "UPDATE {} SET {}  WHERE expense_id = '{}'".format(
                self.__expenses_table_name,
                ", ".join(updates),
                expense_id)

        self.__connection_provider.execute_query(query)

        retriever = ExpensesRetrieverFactory.create(DATABASE_TYPE)
        expense = retriever.retrieve_expense(expense_id)

        print("Updated: {}".format(expense))

        return expense

    def add_category(self, category):
        """Adds a new Category to the database"""

        query = "INSERT INTO {} (category_id, name) VALUES ('{}', '{}')".format(
                    self.__categories_table_name,
                    html.escape(category.get_category_id()),
                    html.escape(category.get_name()))

        self.__connection_provider.execute_query(query)

        print("Added: {}".format(category))

    def persist_tags(self, tags=[]):
        """Adds Tags to the database"""

        if not tags or len(tags) == 0:
            return []

        valid_tag_persisting_query_parts = map(
            self.__create_tag_persisting_query_part,
            self.__filter_out_existing_tags(tags)
        )

        tag_query_parts = list(filter(None, valid_tag_persisting_query_parts))

        self.__connection_provider.execute_query("INSERT INTO {table_name} " \
            "(tag_id, name) VALUES {tags}".format(
                table_name=self.__tags_table_name,
                tags=", ".join(tag_query_parts)))

        return tags

    def persist_expense_tags(self, expense):
        """
        Adds Expense tags to the database
        and stores their relation with the Expense
        """

        if not expense:
            return []

        persisted_tags = self.persist_tags(expense.get_tags())
        delete_query = self.__get_expense_tags_delete_query(expense)

        self.__connection_provider.execute_query(delete_query)

        if persisted_tags and len(persisted_tags) > 0:
            insert_query = "INSERT INTO {} (tag_id, expense_id) " \
                "VALUES {}".format(
                    self.__expense_tags_table_name,
                    ", ".join(["('{}', '{}')".format(
                            tag.get_tag_id(), expense.get_expense_id()
                        ) for tag in persisted_tags])
                )

            self.__connection_provider.execute_query(insert_query)

        return persisted_tags

    def __get_expense_tags_delete_query(self, expense: Expense):
        tags = expense.get_tags()
        expense_id = expense.get_expense_id()

        if tags and len(tags) > 0:
            tag_ids = [tag.get_tag_id() for tag in tags]

            return "DELETE FROM {} WHERE expense_id='{}' " \
                "AND tag_id IN ('{}')".format(
                    self.__expense_tags_table_name,
                    expense_id,
                    "', '".join(tag_ids))

        return "DELETE FROM {} WHERE expense_id='{}'".format(
            self.__expense_tags_table_name, expense_id)

    def __filter_out_existing_tags(self, tags):
        return list(filter(lambda tag: not self.__check_if_tag_exists(tag), tags))

    def __create_tag_persisting_query_part(self, tag):
        return "('{}', '{}')".format(tag.get_tag_id(), tag.get_name())

    def __check_if_tag_exists(self, tag):
        if not tag:
            return False

        rows = self.__connection_provider.execute_query("SELECT * FROM {} " \
            "WHERE name LIKE '{}'".format(self.__tags_table_name,
                                          tag.get_name()))

        return True if rows else False

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
            "tags": validate_non_empty_string,
            "expense_tags": validate_non_empty_string
        }

        validate_dict(database_tables, "database_tables", validator_map)
