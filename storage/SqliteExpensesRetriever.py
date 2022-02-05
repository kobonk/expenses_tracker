import datetime
import html
import itertools
import pendulum
import time
from validation_utils import validate_dict, validate_non_empty_string
from expense.Expense import Expense
from expense.Category import Category
from expense.Tag import Tag
from storage.ExpensesRetrieverBase import ExpensesRetrieverBase

class SqliteExpensesRetriever(ExpensesRetrieverBase):

    def __init__(self, database_tables, connection_provider):
        self.__validate_database_tables(database_tables)
        self.__validate_connection_provider(connection_provider)

        self.__expenses_table_name = database_tables["expenses"]
        self.__categories_table_name = database_tables["categories"]
        self.__tags_table_name = database_tables["tags"]
        self.__expense_tags_table_name = database_tables["expense_tags"]
        self.__suggestions_table_name = database_tables["suggestions"]
        self.__connection_provider = connection_provider

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

        expense_query = """SELECT {ex_table}.expense_id, {ex_table}.name,
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

        expense_rows = self.__execute_query(expense_query)

        if not expense_rows:
            return None

        tag_query = "SELECT {tag_table}.name, {tag_table}.tag_id " \
            "FROM {tag_table} " \
            "JOIN {ex_tag_table} " \
            "ON {tag_table}.tag_id = {ex_tag_table}.tag_id " \
            "JOIN {ex_table} " \
            "ON {ex_tag_table}.expense_id = {ex_table}.expense_id " \
            "WHERE {ex_table}.expense_id = '{expense_id}'".format(
                tag_table=self.__tags_table_name,
                ex_tag_table=self.__expense_tags_table_name,
                ex_table=self.__expenses_table_name,
                expense_id=expense_rows[0][0]
            )

        tag_rows = self.__execute_query(tag_query)

        return self.__convert_table_row_to_expense(expense_rows[0], tag_rows)

    def retrieve_expenses(self, latest_month, number_of_months):
        """Returns the list of Expenses for certain period of time"""

        month_end = pendulum.parse(latest_month).add(months=1).subtract(seconds=1)
        month_start = month_end.subtract(months=number_of_months).add(seconds=1)

        expenses_query = """SELECT {ex_table}.expense_id, {ex_table}.name,
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

        expense_rows = self.__execute_query(expenses_query)

        tags_query = "SELECT " \
            "{ex_table}.expense_id, {tag_table}.name, {tag_table}.tag_id " \
            "FROM {tag_table} " \
            "JOIN {ex_tag_table} " \
            "ON {tag_table}.tag_id = {ex_tag_table}.tag_id " \
            "JOIN {ex_table} " \
            "ON {ex_tag_table}.expense_id = {ex_table}.expense_id".format(
                tag_table=self.__tags_table_name,
                ex_tag_table=self.__expense_tags_table_name,
                ex_table=self.__expenses_table_name
            )

        tag_rows = self.__execute_query(tags_query)

        return self.__get_models_array(expense_rows, "expense", tag_rows)

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
        """Returns the list of all Categories"""
        rows = self.__execute_query("""SELECT * FROM {table_name}
                        ORDER BY name ASC""".format(
                            table_name=self.__categories_table_name
                        ))

        return self.__get_models_array(rows, "category")

    def retrieve_tags(self):
        """Returns the list of all Tags"""
        rows = self.__execute_query("SELECT name, tag_id FROM {} ORDER BY name ASC".format(
                                    self.__tags_table_name))

        return self.__get_models_array(rows, "tag")

    def retrieve_expense_tags(self, expense: Expense):
        """Returns the list of all Tags"""
        rows = self.__execute_query("SELECT name, {tag_table}.tag_id FROM {tag_table} " \
            "JOIN {ex_tag_table} ON " \
            "{tag_table}.tag_id = {ex_tag_table}.tag_id " \
            "WHERE {ex_tag_table}.expense_id='{expense_id}'".format(
                tag_table=self.__tags_table_name,
                ex_tag_table=self.__expense_tags_table_name,
                expense_id=expense.get_expense_id())
            )

        return self.__get_models_array(rows, "tag")

    def retrieve_expense_suggestions(self, month_date):
      """Returns a list of expense suggestions for the provided month_date"""

      month_end = pendulum.parse(month_date).add(months=1).subtract(seconds=1)
      month_start = month_end.subtract(months=1).add(seconds=1)
      month = month_start.month

      s_table = self.__suggestions_table_name
      e_table = self.__expenses_table_name
      c_table = self.__categories_table_name

      query = f"SELECT s.name, s.category_id, c.name AS category_name, s.cost FROM {s_table} s " \
        f"LEFT JOIN {c_table} c ON s.category_id = c.category_id " \
        f"WHERE NOT EXISTS (SELECT * FROM {e_table} e WHERE s.name = e.name " \
        f"AND e.purchase_date < {month_end.int_timestamp} AND e.purchase_date >= {month_start.int_timestamp}) " \
        f"AND REGEXP('^{month},|,{month},|,{month}$', s.months)"

      print(query)

      rows = self.__execute_query(query)

      return self.__get_models_array(list(rows), "suggestion")

    def __leave_unique_values(self, list_of_values):
        if not list:
            return []

        unique_list = []

        for value in list_of_values:
            if not value in unique_list:
                unique_list.append(value)

        return unique_list

    def __execute_query(self, query):
        return self.__connection_provider.execute_query(query)

    def __get_models_array(self, rows, model_type, additional_rows=[]):
        models = []

        if not rows:
            return models

        convert_data_to_model = self.__get_data_converter(model_type)

        for row in rows:
            models.append(convert_data_to_model(row, additional_rows))

        return models

    def __get_data_converter(self, model_type):
        if model_type == "expense":
            return self.__convert_table_row_to_expense

        if model_type == "category":
            return self.__convert_table_row_to_category

        if model_type == "tag":
            return self.__convert_table_row_to_tag

        if model_type == "suggestion":
            return self.__convert_table_row_to_suggestion

    def __convert_table_row_to_expense(self, table_row, tag_rows):
        expense_tag_rows = self.__extract_expense_tag_rows(table_row[0], tag_rows)

        return Expense(
            expense_id=table_row[0],
            name=html.unescape(table_row[1]),
            cost=table_row[2],
            date=table_row[3],
            category=self.__convert_table_row_to_category(table_row[4:]),
            tags=[self.__convert_table_row_to_tag(tag_row)
                for tag_row in expense_tag_rows]
        )

    def __convert_table_row_to_category(self, table_row, additional_rows=[]):
        return Category(table_row[0], html.unescape(table_row[1]))

    def __convert_table_row_to_tag(self, table_row, additional_rows=[]):
        return Tag(table_row[1], html.unescape(table_row[0]))

    def __convert_table_row_to_suggestion(self, table_row, additional_rows=[]):
        category = Category(table_row[1], table_row[2])

        return Expense('', table_row[0], table_row[3], None, category, [])

    def __extract_expense_tag_rows(self, expense_id, tag_rows):
        filtered = list(filter(lambda row: row[0] == expense_id, tag_rows))

        return [tuple(row[1:]) for row in filtered]

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
