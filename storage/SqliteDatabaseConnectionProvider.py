"""Provides a connection to Sqlite database"""
import os
import sqlite3

class SqliteDatabaseConnectionProvider:
    """Exposes methods for connecting and disconnecting with database"""
    def __init__(self, database_path):
        self.__database_path = database_path

    def get_connection(self):
        """Connects to Sqlite database and returns the connection"""
        self.__ensure_database_directory_exists()

        return sqlite3.connect(self.__database_path)

    def __ensure_database_directory_exists(self):
        """Based on database_path creates directory if it doesn't exist"""
        directory = os.path.dirname(self.__database_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
