"""Provides a connection to Sqlite database"""
import mariadb
import json

from validation_utils import validate_dict, validate_non_empty_string

def create_columns_schema(columns):
    return ", ".join("{} {}".format(name, schema) for name, schema in columns)

class MariaDbDatabaseConnectionProvider:
    __connection = None
    __settings = None

    """Exposes methods for connecting and disconnecting with database"""
    def __init__(self, database_tables):
        self.__validate_database_tables(database_tables)
        self.__settings = json.load(open('settings.json'))
        self.__database_tables = database_tables

        self.__connection = self.__get_connection()

    def __del__(self):
        if self.__connection:
            self.__connection.close()

    def __get_connection(self):
        """Connects to Sqlite database and returns the connection"""
        connection = mariadb.connect(
          host=self.__settings['sql_host'],
          database=self.__settings['sql_db'],
          user=self.__settings['sql_user'],
          password=self.__settings['sql_pass']
        )

        return connection

    def ensure_necessary_tables_exist(self):
        """
        Checks if necessary tables exist in the database,
        if they have necessary columns and adds them if they don't.
        """

        cursor = self.__connection.cursor()

        cursor.execute('SHOW TABLES')
        self.__connection.commit()

        tables = cursor.fetchall()

        if tables == None or len(tables) == 0:
          self.__ensure_categories_table_exists()
          self.__ensure_expenses_table_exists()

    def execute_query(self, query, params = ()):
        """Makes a request to the database"""
        cursor = self.__connection.cursor()

        cursor.execute(query, params)
        self.__connection.commit()

        result = None

        try:
          result = cursor.fetchall()
        except Exception as ex:
          print(ex)

        cursor.close()

        return result

    def __ensure_expenses_table_exists(self):
        columns = [
            ("expense_id", "INT PRIMARY KEY AUTO_INCREMENT"),
            ("name", "VARCHAR(150) NOT NULL"),
            ("cost", "INT NOT NULL DEFAULT 0"),
            ("purchase_date", "INT NOT NULL"),
            ("day", "INT NOT NULL"),
            ("month", "INT NOT NULL"),
            ("year", "INT NOT NULL"),
            ("category_id", "INT NOT NULL"),
            ("FOREIGN KEY(category_id)", "REFERENCES categories(category_id)")
        ]

        self.__ensure_table_exists(self.__database_tables["expenses"], columns)

    def __ensure_categories_table_exists(self):
        columns = [
          ("category_id", "INT PRIMARY KEY AUTO_INCREMENT"),
          ("name", "VARCHAR(100) UNIQUE NOT NULL")
        ]

        self.__ensure_table_exists(self.__database_tables["categories"], columns)

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
        }

        validate_dict(database_tables, "database_tables", validator_map)
