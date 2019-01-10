import datetime
import html
import time
from expenses_tracker.expense.Expense import Expense
from expenses_tracker.expense.Category import Category
from expenses_tracker.expense.Statistics import Statistics

class SqliteExpensesRetriever():
    
    def __init__(self, expenses_table_name, categories_table_name,
                 connection_provider):
        self.__validate_expenses_table_name(expenses_table_name)
        self.__validate_categories_table_name(categories_table_name)
        self.__validate_connection_provider(connection_provider)        

        self.__expenses_table_name = expenses_table_name
        self.__categories_table_name = categories_table_name
        self.__connection_provider = connection_provider

    def retrieve_expenses(self, amount):
        """Returns the list of Expenses"""
        selection = """SELECT {ex_table}.expense_id, {ex_table}.name, {ex_table}.cost, 
                    {ex_table}.purchase_date, {cat_table}.category_id, 
                    {cat_table}.name AS 'category_name' FROM {ex_table} 
                    LEFT JOIN {cat_table} ON 
                    {ex_table}.category_id = {cat_table}.category_id
                    ORDER BY purchase_date DESC{limit}""".format(
                        ex_table=self.__expenses_table_name,
                        cat_table=self.__categories_table_name,
                        limit=self.__get_limit_query_string(amount))
        rows = self.__get_rows(selection)

        return self.__get_models_array(rows, "expense")

    def retrieve_category_statistics_between_dates(self, start_date, end_date):
        """Returns a list of Statistics added between start and end date"""
        selection = """SELECT SUM({ex_table}.cost) AS 'total', 
                    {cat_table}.category_id, 
                    {cat_table}.name AS 'category_name' FROM {ex_table} 
                    LEFT JOIN {cat_table} ON 
                    {ex_table}.category_id = {cat_table}.category_id
                    WHERE {ex_table}.purchase_date 
                    BETWEEN {start_date} AND {end_date}
                    GROUP BY category_name
                    ORDER BY total DESC""".format(
                        ex_table=self.__expenses_table_name,
                        cat_table=self.__categories_table_name,
                        start_date=start_date, end_date=end_date)
        rows = self.__get_rows(selection)

        return self.__get_models_array(rows, "statistics")

    def retrieve_statistics_for_months(self, number_of_months):
        """Returns a list of Statistics for the provided amount of months"""
        now = datetime.datetime.now()
        current_year, current_month = now.year, now.month
        first_day_of_month = datetime.datetime(current_year, current_month, 1)
        return {}

    def retrieve_similar_expense_names(self, expense_name):
        """Returns a list of expense names similar to the one provided"""
        rows = self.__get_rows("""SELECT name FROM {table_name} 
                        WHERE name LIKE '%{name}%' 
                        ORDER BY name ASC""".format(
                            name=expense_name,
                            table_name=self.__expenses_table_name
                        ))

        return list(set(rows))

    def retrieve_categories(self):
        """Returns the list of Categories"""
        rows = self.__get_rows("""SELECT * FROM {table_name} 
                        ORDER BY name ASC""".format(
                            table_name=self.__categories_table_name
                        ))

        return self.__get_models_array(rows, "category")

    def __get_limit_query_string(self, amount):
        if amount:
            return " LIMIT {amount}".format(amount=amount)

        return ""

    def __get_rows(self, query):
        connection = self.__connection_provider.get_connection()
        cursor = connection.cursor()
        
        cursor.execute(query)

        return cursor.fetchall()

    def __get_models_array(self, rows, model_type):
        expenses = []
        convert_data_to_model = self.__get_data_converter(model_type)

        for row in rows:
            expenses.append(convert_data_to_model(row))

        return expenses

    def __get_data_converter(self, model_type):
        if model_type is "expense":
            return self.__convert_table_row_to_expense

        if model_type is "category":
            return self.__convert_table_row_to_category

        if model_type is "statistics":
            return self.__convert_table_row_to_statistics

    def __convert_table_row_to_expense(self, table_row):
        return Expense(table_row[0], html.unescape(table_row[1]), table_row[2],
                       table_row[3], self.__convert_table_row_to_category(
                           [table_row[4], table_row[5]]
                       ))

    def __convert_table_row_to_category(self, table_row):
        return Category(table_row[0], html.unescape(table_row[1]))

    def __convert_table_row_to_statistics(self, table_row):
        category = Category(table_row[1], html.unescape(table_row[2]))

        return Statistics(category, float(table_row[0]))

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
