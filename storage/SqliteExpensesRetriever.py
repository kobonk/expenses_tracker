import datetime
import html
import itertools
import pendulum
import time
from validation_utils import validate_dict, validate_non_empty_string
from expense.Expense import Expense
from expense.Category import Category
from storage.ExpensesRetrieverBase import ExpensesRetrieverBase

class SqliteExpensesRetriever(ExpensesRetrieverBase):

    def __init__(self, database_tables, connection_provider):
        self.__validate_database_tables(database_tables)
        self.__validate_connection_provider(connection_provider)

        self.__expenses_table_name = database_tables["expenses"]
        self.__categories_table_name = database_tables["categories"]
        self.__tags_table_name = database_tables["tags"]
        self.__connection_provider = connection_provider

    def ensure_necessary_tables_exist(self):
        """
        Checks if necessary tables exist in the database,
        if they have necessary columns and adds them if they don't.
        """

        self.__ensure_expenses_table_exists()
        self.__ensure_categories_table_exists()
        self.__ensure_tags_table_exists()

    def filter_expenses(self, expense_name):
        """Returns a list of Expenses with matching expense_name"""

        selection = """SELECT {ex_table}.expense_id, {ex_table}.name,
                    {ex_table}.cost, {ex_table}.purchase_date,
                    {cat_table}.category_id,
                    {cat_table}.name AS 'category_name'
                    FROM {ex_table}
                    LEFT JOIN {cat_table} ON
                    {ex_table}.category_id = {cat_table}.category_id
                    WHERE {ex_table}.name COLLATE UTF8_GENERAL_CI LIKE '%{expense_name}%'""".format(
                        ex_table=self.__expenses_table_name,
                        cat_table=self.__categories_table_name,
                        expense_name=expense_name)

        rows = self.__execute_query(selection)

        return self.__get_models_array(rows, "expense")

    def retrieve_common_expense_cost(self, expense_name):
        """Returns the most common price for provided Expense name"""
        selection = """SELECT name, cost, COUNT(name) as 'counter'
                    FROM {ex_table}
                    WHERE name LIKE '{ex_name}'
                    GROUP BY name, cost
                    ORDER BY COUNT(name) DESC
                    LIMIT 1""".format(
                        ex_table=self.__expenses_table_name,
                        ex_name=expense_name
                    )

        rows = self.__execute_query(selection)

        if not rows or rows[0][2] < 5:
            return 0

        return rows[0][1]

    def retrieve_expense(self, expense_id):
        """Returns an Expense from the database"""

        selection = """SELECT {ex_table}.expense_id, {ex_table}.name,
                    {ex_table}.cost, {ex_table}.purchase_date,
                    {cat_table}.category_id,
                    {cat_table}.name AS 'category_name'
                    FROM {ex_table}
                    LEFT JOIN {cat_table} ON
                    {ex_table}.category_id = {cat_table}.category_id
                    WHERE {ex_table}.expense_id = '{expense_id}'""".format(
                        ex_table=self.__expenses_table_name,
                        cat_table=self.__categories_table_name,
                        expense_id=expense_id)

        rows = self.__execute_query(selection)

        return self.__convert_table_row_to_expense(rows[0])

    def retrieve_expenses(self, latest_month, number_of_months):
        """Returns the list of Expenses for certain period of time"""

        month_end = pendulum.parse(latest_month).add(months=1).subtract(seconds=1)
        month_start = month_end.subtract(months=number_of_months).add(seconds=1)

        selection = """SELECT {ex_table}.expense_id, {ex_table}.name,
                    {ex_table}.cost, {ex_table}.purchase_date,
                    {cat_table}.category_id,
                    {cat_table}.name AS 'category_name'
                    FROM {ex_table}
                    LEFT JOIN {cat_table} ON
                    {ex_table}.category_id = {cat_table}.category_id
                    WHERE {ex_table}.purchase_date
                    BETWEEN {start_date} AND {end_date}
                    ORDER BY purchase_date DESC""".format(
                        ex_table=self.__expenses_table_name,
                        cat_table=self.__categories_table_name,
                        start_date=month_start.int_timestamp,
                        end_date=month_end.int_timestamp)

        rows = self.__execute_query(selection)

        return self.__get_models_array(rows, "expense")

    def retrieve_months(self):
        """Returns a list of months which may have Expenses registered"""
        oldest_timestamp = self.__execute_query("""SELECT {ex_table}.purchase_date
                                              FROM {ex_table}
                                              ORDER BY {ex_table}.purchase_date ASC
                                              LIMIT 1""".format(ex_table=self.__expenses_table_name))

        oldest_date = pendulum.from_timestamp(int(oldest_timestamp[0][0]))
        period = pendulum.period(oldest_date, pendulum.now())

        months = [month.format("YYYY-MM") for month in period.range("months")]

        return months

    def retrieve_similar_expense_names(self, expense_name):
        """Returns a list of expense name and category pairs
        for the provided expense name"""
        list_of_rows = self.__execute_query("""SELECT {ex_table}.name,
                        {cat_table}.name AS 'category_name' FROM {ex_table}
                        LEFT JOIN {cat_table}
                        ON {ex_table}.category_id = {cat_table}.category_id
                        WHERE {ex_table}.name LIKE '%{name}%'
                        ORDER BY {ex_table}.name ASC""".format(
                            ex_table=self.__expenses_table_name,
                            cat_table=self.__categories_table_name,
                            name=expense_name
                        ))

        rows = [{ "name": n, "category": c } for n, c in list_of_rows]
        unique_rows = list(rows)
        sorted_by_frequency = sorted(unique_rows, key=unique_rows.count, reverse=True)

        return self.__leave_unique_values(sorted_by_frequency)

    def retrieve_categories(self):
        """Returns the list of Categories"""
        rows = self.__execute_query("""SELECT * FROM {table_name}
                        ORDER BY name ASC""".format(
                            table_name=self.__categories_table_name
                        ))

        return self.__get_models_array(rows, "category")

    def __leave_unique_values(self, list_of_values):
        if not list:
            return []

        unique_list = []

        for value in list_of_values:
            if not value in unique_list:
                unique_list.append(value)

        return unique_list

    def __execute_query(self, query):
        connection = self.__connection_provider.get_connection()
        cursor = connection.cursor()

        cursor.execute(query)

        return cursor.fetchall()

    def __get_models_array(self, rows, model_type):
        models = []
        convert_data_to_model = self.__get_data_converter(model_type)

        for row in rows:
            models.append(convert_data_to_model(row))

        return models

    def __get_data_converter(self, model_type):
        if model_type == "expense":
            return self.__convert_table_row_to_expense

        if model_type == "category":
            return self.__convert_table_row_to_category

    def __convert_table_row_to_expense(self, table_row):
        return Expense(table_row[0], html.unescape(table_row[1]), table_row[2],
                       table_row[3], self.__convert_table_row_to_category(
                           [table_row[4], table_row[5]]
                       ))

    def __convert_table_row_to_category(self, table_row):
        return Category(table_row[0], html.unescape(table_row[1]))

    def __ensure_expenses_table_exists(self):
        columns = [
            ("expense_id", "TEXT PRIMARY KEY"),
            ("name", "TEXT"),
            ("cost", "REAL"),
            ("purchase_date", "REAL"),
            ("category_id", "TEXT"),
            ("tag_ids", "TEXT"),
        ]

        self.__ensure_table_exists(self.__expenses_table_name, columns)

    def __ensure_categories_table_exists(self):
        columns = [("category_id", "TEXT PRIMARY KEY"), ("name", "TEXT")]

        self.__ensure_table_exists(self.__categories_table_name, columns)

    def __ensure_tags_table_exists(self):
        columns = [("tag_id", "TEXT PRIMARY KEY"), ("name", "TEXT")]

        self.__ensure_table_exists(self.__tags_table_name, columns)

    def __ensure_table_exists(self, table_name, columns):
        query = "CREATE TABLE IF NOT EXISTS {} ({})".format(table_name,
                create_columns_schema(columns))

        self.__execute_query(query)
        self.__ensure_table_columns_exist(table_name, columns)

    def __ensure_table_columns_exist(self, table_name, columns):
        selection = "PRAGMA table_info({})".format(table_name)

        rows = self.__execute_query(selection)
        column_names = [row[1] for row in rows]

        for column, schema in columns:
            if not column in column_names:
                selection = "ALTER TABLE {} ADD COLUMN {} {}".format(
                             table_name, column, schema)

                self.__execute_query(selection)

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

def create_columns_schema(columns):
    return ", ".join("{} {}".format(name, schema) for name, schema in columns)
