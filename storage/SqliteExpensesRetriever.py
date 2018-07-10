import html
import os
import time
import sqlite3
from expenses_tracker.expense.Expense import Expense

class SqliteExpensesRetriever():
    
    def __init__(self, expenses_table_name, connection_provider):
        self.__expenses_table_name = expenses_table_name
        self.__connection_provider = connection_provider

    def retrieve_expenses(self):
        """Returns the list of Expenses"""
        rows = self.__get_rows("""SELECT * FROM {table_name} 
                        ORDER BY purchase_date ASC""".format(
                            table_name=self.__expenses_table_name
                        ))

        return self.__get_expenses_table(rows)

    def __get_rows(self, query):
        connection = self.__connection_provider.get_connection()
        cursor = connection.cursor()
        
        cursor.execute(query)

        return cursor.fetchall()

    def __get_expenses_table(self, rows):
        expenses = []

        for row in rows:
            expenses.append(self.__convert_table_row_to_expense(row))

        return expenses

    def __convert_table_row_to_expense(self, table_row):
        return Expense(table_row[0], html.unescape(table_row[1]), table_row[2],
                       table_row[3], html.unescape(table_row[4]))
