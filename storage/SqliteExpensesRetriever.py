import datetime
import html
import itertools
import pendulum
import time
from expenses_tracker.expense.Expense import Expense
from expenses_tracker.expense.Category import Category
from expenses_tracker.expense.MonthStatistics import MonthStatistics

class SqliteExpensesRetriever():

    def __init__(self, expenses_table_name, categories_table_name,
                 connection_provider):
        self.__validate_expenses_table_name(expenses_table_name)
        self.__validate_categories_table_name(categories_table_name)
        self.__validate_connection_provider(connection_provider)

        self.__expenses_table_name = expenses_table_name
        self.__categories_table_name = categories_table_name
        self.__connection_provider = connection_provider

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

        rows = self.__get_rows(selection)

        return self.__convert_table_row_to_expense(rows[0])

    def retrieve_expenses(self, category_id, month):
        """Returns the list of Expenses for certain category and month"""
        month_start = pendulum.parse(month + "-01")
        month_end = pendulum.datetime(
            month_start.year,
            month_start.month,
            month_start.days_in_month,
            23, 59, 59
        )

        selection = """SELECT {ex_table}.expense_id, {ex_table}.name,
                    {ex_table}.cost, {ex_table}.purchase_date,
                    {cat_table}.category_id,
                    {cat_table}.name AS 'category_name'
                    FROM {ex_table}
                    LEFT JOIN {cat_table} ON
                    {ex_table}.category_id = {cat_table}.category_id
                    WHERE {ex_table}.category_id = '{category_id}'
                    AND {ex_table}.purchase_date
                    BETWEEN {start_date} AND {end_date}
                    ORDER BY purchase_date DESC""".format(
                        ex_table=self.__expenses_table_name,
                        cat_table=self.__categories_table_name,
                        category_id=category_id,
                        start_date=month_start.int_timestamp,
                        end_date=month_end.int_timestamp)

        rows = self.__get_rows(selection)

        return self.__get_models_array(rows, "expense")

    def retrieve_statistics_for_months(self, number_of_months):
        """Returns a list of Statistics for the provided amount of months"""
        today = pendulum.today().set(tz="UTC")
        rows = []
        index = 0

        while index < number_of_months:
            first_day = today.subtract(months=index).set(day=1)
            last_day = pendulum.datetime(
                first_day.year,
                first_day.month,
                first_day.days_in_month,
                23, 59, 59
            )

            month_rows = self.__retrieve_statistics_rows_between_dates(
                first_day.int_timestamp,
                last_day.int_timestamp
            )

            month_rows_with_dates = list(map(
                lambda row: row + tuple([first_day.format("YYYY-MM")]),
                month_rows
            ))

            rows = rows + month_rows_with_dates
            index += 1

        return self.__get_models_array(rows, "month-statistics")

    def retrieve_similar_expense_names(self, expense_name):
        """Returns a list of expense name and category pairs
        for the provided expense name"""
        list_of_rows = self.__get_rows("""SELECT {ex_table}.name,
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
        rows = self.__get_rows("""SELECT * FROM {table_name}
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

    def __get_limit_query_string(self, amount):
        if amount:
            return " LIMIT {amount}".format(amount=amount)

        return ""

    def __retrieve_statistics_rows_between_dates(self, start_date, end_date):
        """Returns a list table rows between start and end date"""
        selection = """SELECT SUM({ex_table}.cost) AS 'total',
                    {cat_table}.category_id,
                    {cat_table}.name AS 'category_name' FROM {ex_table}
                    LEFT JOIN {cat_table} ON
                    {ex_table}.category_id = {cat_table}.category_id
                    WHERE {ex_table}.purchase_date
                    BETWEEN {start_date} AND {end_date}
                    GROUP BY category_name
                    ORDER BY category_name ASC""".format(
                        ex_table=self.__expenses_table_name,
                        cat_table=self.__categories_table_name,
                        start_date=start_date, end_date=end_date)

        return self.__get_rows(selection)

    def __get_rows(self, query):
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

        if model_type == "month-statistics":
            return self.__convert_table_row_to_month_statistics

    def __convert_table_row_to_expense(self, table_row):
        return Expense(table_row[0], html.unescape(table_row[1]), table_row[2],
                       table_row[3], self.__convert_table_row_to_category(
                           [table_row[4], table_row[5]]
                       ))

    def __convert_table_row_to_category(self, table_row):
        return Category(table_row[0], html.unescape(table_row[1]))

    def __convert_table_row_to_month_statistics(self, table_row):
        category = Category(table_row[1], html.unescape(table_row[2]))

        return MonthStatistics(category, float(table_row[0]), table_row[3])

    def __validate_expenses_table_name(self, expenses_table_name):
        if (not expenses_table_name or
            not isinstance(expenses_table_name, str)):
            raise ValueError("InvalidArgument: expenses_table_name must be a "
                             "non-empty string")

    def __validate_categories_table_name(self, categories_table_name):
        if (not categories_table_name or
            not isinstance(categories_table_name, str)):
            raise ValueError("InvalidArgument: categories_table_name must be a "
                             "non-empty string")

    def __validate_connection_provider(self, connection_provider):
        if not connection_provider:
            raise ValueError("InvalidArgument: connection_provider must be "
                             "provided")

        if (not hasattr(connection_provider, "get_connection") or
            not callable(connection_provider.get_connection)):
            raise ValueError("InvalidArgument: connection_provider must have "
                             "get_connection method")
