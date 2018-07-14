import html
import os
import sqlite3
import uuid
from colorama import init, Fore, Style
from datetime import datetime
from expenses_tracker.const import DATABASE_PATH, EXPENSES_TABLE_NAME, CATEGORIES_TABLE_NAME
from expenses_tracker.expense.Expense import Expense
from TexttableExpensesRenderer import TexttableExpensesRenderer

def get_database_connection(database_path):
    directory = os.path.dirname(database_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    return sqlite3.connect(database_path)

def create_expenses_table(connection, expenses_table_name):
    """Creates the Expenses table in the database"""

    cursor = connection.cursor()
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS {table_name} (
                    expense_id  TEXT PRIMARY KEY, 
                    name TEXT, 
                    cost REAL, 
                    purchase_date REAL,
                    category TEXT)"""
                    .format(table_name=expenses_table_name)
    )
    
    connection.commit()

def create_categories_table(connection, categories_table_name):
    """Creates the Categories table in the database"""

    cursor = connection.cursor()
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS {table_name} (
                    category_id  TEXT PRIMARY KEY, 
                    name TEXT)"""
                    .format(table_name=categories_table_name)
    )
    
    connection.commit()

def add_expense_to_database(connection, expenses_table_name, expense):
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO {table_name} (
                    expense_id, 
                    name, 
                    cost, 
                    purchase_date, 
                    category
                ) VALUES (
                    '{e_id}', 
                    '{e_name}', 
                    {e_cost}, 
                    {e_purchase_date},
                    '{e_category}')"""
                .format(
                    table_name=expenses_table_name,
                    e_id=expense.get_expense_id(), 
                    e_name=html.escape(expense.get_name()),
                    e_cost=expense.get_cost(),
                    e_purchase_date=expense.get_purchase_date(),
                    e_category=html.escape(expense.get_category_id())
                )
    )

    connection.commit()

def get_purchase_date():
    """Retrieves the purchase_date of the Expense from the user"""
    purchase_date = input("Date of Purchase (YYYY-MM-DD): ")

    try:
        purchase_date = convert_date_string_to_timestamp(purchase_date)
    except ValueError as exception:
        print(Fore.RED + "ERROR: {exception}".format(exception=exception) +
                Style.RESET_ALL)
        purchase_date = get_purchase_date()

    return purchase_date

def convert_date_string_to_timestamp(date_string):
    """Converts date (YYYY-MM-DD) to a number"""
    try:
        year, month, day = map(int, date_string.split("-"))
        date = datetime(year, month, day)

        return date.timestamp()
    except Exception as exception:
        raise ValueError(exception)

def retrieve_all_expenses(connection, expenses_table_name):
    """Returns the list of Expenses"""
    rows = get_rows(connection, """SELECT * FROM {table_name} 
                    ORDER BY purchase_date ASC""".format(
                        table_name=expenses_table_name
                    ))

    return get_expenses_table(rows)

def get_rows(connection, query):
    cursor = connection.cursor()
    
    cursor.execute(query)

    return cursor.fetchall()

def get_expenses_table(rows):
    expenses = []

    for row in rows:
        expenses.append(convert_table_row_to_expense(row))

    return expenses

def convert_table_row_to_expense(table_row):
    return Expense(table_row[0], html.unescape(table_row[1]), table_row[2],
                    table_row[3], html.unescape(table_row[4]))

def main():
    option = input("Type '1' to add a new Expense\nType '2' to display Expenses list\nType any other character to exit\n")

    if option is "1":
        os.system("cls" if os.name == "nt" else "clear")
        connection = get_database_connection(DATABASE_PATH)
        create_expenses_table(connection, EXPENSES_TABLE_NAME)
        create_categories_table(connection, CATEGORIES_TABLE_NAME)

        name = input("\nExpense name: ")
        expense_id = uuid.uuid4()
        category = input("Expense category: ")
        purchase_date = get_purchase_date()
        cost = input("Cost: ")

        expense = Expense(expense_id, name, cost, purchase_date, category)
        add_expense_to_database(connection, EXPENSES_TABLE_NAME, expense)
        connection.close()
        print("\n")
        return main()

    if option is "2":
        os.system("cls" if os.name == "nt" else "clear")
        connection = get_database_connection(DATABASE_PATH)
        expenses = retrieve_all_expenses(connection, EXPENSES_TABLE_NAME)

        renderer = TexttableExpensesRenderer()
        renderer.render_expenses(expenses)

        print("\n")
        return main()

    return 0
    
os.system("cls" if os.name == "nt" else "clear")
main()
