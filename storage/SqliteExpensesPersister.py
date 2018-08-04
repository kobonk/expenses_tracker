"""Uses SqlLite to save and update Expenses in the database"""
import html
import os
import sqlite3
from sqlite3 import Error

class SqliteExpensesPersister():
    """Persists Expenses data in a database"""
    
    def __init__(self, expenses_table_name, categories_table_name,
                 connection_provider):
        self.__expenses_table_name = expenses_table_name
        self.__categories_table_name = categories_table_name
        self.__connection_provider = connection_provider

        self.__create_categories_table()
        self.__create_expenses_table()
    
    def add_expense(self, expense):
        """Adds a new Expense to database"""

        connection = self.__connection_provider.get_connection()
        cursor = connection.cursor()

        cursor.execute("""INSERT INTO {table_name} (
                    expense_id, 
                    name, 
                    cost, 
                    purchase_date, 
                    category_id
                ) VALUES (
                    '{e_id}', 
                    '{e_name}', 
                    {e_cost}, 
                    {e_purchase_date},
                    '{e_category_id}')"""
                .format(
                    table_name=self.__expenses_table_name,
                    e_id=expense.get_expense_id(), 
                    e_name=html.escape(expense.get_name()),
                    e_cost=expense.get_cost(),
                    e_purchase_date=expense.get_purchase_date(),
                    e_category_id=html.escape(expense.get_category_id())
                )
        )

        connection.commit()
        connection.close()

        print("Added: {expense_string}".format(
            expense_string=expense.to_string()))

    def __create_expenses_table(self):
        """Creates the Expenses table in the database"""

        connection = self.__connection_provider.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS {table_name} (
                        expense_id  TEXT PRIMARY KEY, 
                        name TEXT, 
                        cost REAL, 
                        purchase_date REAL, 
                        category_id TEXT)"""
                        .format(table_name=self.__expenses_table_name)
        )
        
        connection.commit()
        connection.close()

    def __create_categories_table(self):
        """Creates the Categories table in the database"""

        connection = self.__connection_provider.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS {table_name} (
                        category_id  TEXT PRIMARY KEY, 
                        name TEXT)"""
                        .format(table_name=self.__categories_table_name)
        )
        
        connection.commit()
        connection.close()
