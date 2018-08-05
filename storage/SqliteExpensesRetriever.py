import html
from expenses_tracker.expense.Expense import Expense
from expenses_tracker.expense.Category import Category

class SqliteExpensesRetriever():
    
    def __init__(self, expenses_table_name, categories_table_name,
                 connection_provider):
        if (not expenses_table_name or 
            not isinstance(expenses_table_name, str)):
            raise ValueError("InvalidArgument: expenses_table_name must be a "
                             "non-empty string")

        if (not categories_table_name or 
            not isinstance(categories_table_name, str)):
            raise ValueError("InvalidArgument: categories_table_name must be a "
                             "non-empty string")

        self.__expenses_table_name = expenses_table_name
        self.__categories_table_name = categories_table_name
        self.__connection_provider = connection_provider

    def retrieve_expenses(self):
        """Returns the list of Expenses"""
        rows = self.__get_rows("""SELECT * FROM {table_name} 
                        ORDER BY purchase_date DESC""".format(
                            table_name=self.__expenses_table_name
                        ))

        return self.__get_models_array(rows, "expense")

    def retrieve_categories(self):
        """Returns the list of Categories"""
        rows = self.__get_rows("""SELECT * FROM {table_name} 
                        ORDER BY name ASC""".format(
                            table_name=self.__categories_table_name
                        ))

        return self.__get_models_array(rows, "category")

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

    def __convert_table_row_to_expense(self, table_row):
        return Expense(table_row[0], html.unescape(table_row[1]), table_row[2],
                       table_row[3], html.unescape(table_row[4]))

    def __convert_table_row_to_category(self, table_row):
        return Category(table_row[0], html.unescape(table_row[1]))
