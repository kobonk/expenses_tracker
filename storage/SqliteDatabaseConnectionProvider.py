"""Provides a connection to Sqlite database"""
import os
import sqlite3
import re

from validation_utils import validate_dict, validate_non_empty_string

def create_columns_schema(columns):
    return ", ".join("{} {}".format(name, schema) for name, schema in columns)

def regexp(pattern, string, search=re.search):
    return 1 if search(pattern, string) else 0

class SqliteDatabaseConnectionProvider:
    __connection = None

    """Exposes methods for connecting and disconnecting with database"""
    def __init__(self, database_path, database_tables):
        validate_non_empty_string(database_path, "database_path")
        self.__validate_database_tables(database_tables)

        self.__database_path = database_path
        self.__database_tables = database_tables

        self.__connection = self.__get_connection()

    def __del__(self):
        if self.__connection:
            self.__connection.close()

    def __get_connection(self):
        """Connects to Sqlite database and returns the connection"""
        self.__ensure_database_directory_exists()

        connection = sqlite3.connect(self.__database_path)

        connection.create_function('regexp', 2, regexp)

        return connection

    def ensure_necessary_tables_exist(self):
        """
        Checks if necessary tables exist in the database,
        if they have necessary columns and adds them if they don't.
        """

        self.__ensure_expenses_table_exists()
        self.__ensure_categories_table_exists()
        self.__ensure_tags_table_exists()
        self.__ensure_expense_tags_table_exists()

    def execute_query(self, query):
        """Makes a request to the database"""
        cursor = self.__connection.cursor()

        cursor.execute(query)
        self.__connection.commit()

        return cursor.fetchall()

    def __ensure_database_directory_exists(self):
        """Based on database_path creates directory if it doesn't exist"""
        if ":memory" in self.__database_path:
            return True

        directory = os.path.dirname(self.__database_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def __ensure_expenses_table_exists(self):
        columns = [
            ("expense_id", "TEXT PRIMARY KEY"),
            ("name", "TEXT"),
            ("cost", "REAL"),
            ("purchase_date", "REAL"),
            ("category_id", "TEXT")
        ]

        self.__ensure_table_exists(self.__database_tables["expenses"], columns)

    def __ensure_categories_table_exists(self):
        columns = [("category_id", "TEXT PRIMARY KEY"), ("name", "TEXT")]

        self.__ensure_table_exists(self.__database_tables["categories"], columns)

    def __ensure_tags_table_exists(self):
        columns = [("tag_id", "TEXT PRIMARY KEY"), ("name", "TEXT")]

        self.__ensure_table_exists(self.__database_tables["tags"], columns)

    def __ensure_expense_tags_table_exists(self):
        columns = [
            ("expense_id", "TEXT"),
            ("tag_id", "TEXT")
        ]

        self.__ensure_table_exists(self.__database_tables["expense_tags"], columns)

    def __ensure_table_exists(self, table_name, columns):
        query = "CREATE TABLE IF NOT EXISTS {} ({})".format(table_name,
                create_columns_schema(columns))

        self.execute_query(query)
        self.__ensure_table_columns_exist(table_name, columns)

    def __ensure_table_columns_exist(self, table_name, columns):
        selection = "PRAGMA table_info({})".format(table_name)

        rows = self.execute_query(selection)
        column_names = [row[1] for row in rows]

        for column, schema in columns:
            if not column in column_names:
                selection = "ALTER TABLE {} ADD COLUMN {} {}".format(
                             table_name, column, schema)

                self.execute_query(selection)

    def __validate_database_tables(self, database_tables):
        validator_map = {
            "expenses": validate_non_empty_string,
            "categories": validate_non_empty_string,
            "tags": validate_non_empty_string,
            "expense_tags": validate_non_empty_string
        }

        validate_dict(database_tables, "database_tables", validator_map)
