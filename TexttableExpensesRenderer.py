"""The module uses Texttable library to display Expenses"""
import html
from texttable import Texttable

class TexttableExpensesRenderer:
    """The class displays Expenses in a table"""

    def render_expenses(self, expenses):
        """Displays a list of Expenses in a table"""
        table = Texttable()
        table.set_cols_align(["r", "l", "r", "r", "l"])
        table.header(["#", "Name", "Cost", "Date", "Category"])
        table.set_cols_dtype(["i", "t", "f", "t", "t"])
        table.set_precision(2)
        table.set_deco(Texttable.HEADER | Texttable.HLINES)

        for index, expense in enumerate(expenses):
            table.add_row([index + 1, html.unescape(expense.get_name()),
                           expense.get_cost(), 
                           expense.get_purchase_date_string(),
                           expense.get_category().get_name()])

        print(table.draw())

    def render_expense(self, expense):
        """Displays a single Expense in a table"""
        table = Texttable()
        table.set_cols_align(["l", "l"])
        table.set_precision(2)
        table.set_deco(Texttable.HLINES)
        table.add_row(["Id:", expense.get_expense_id()])
        table.add_row(["Name:", html.unescape(expense.get_name())])
        table.add_row(["Cost:", expense.get_cost()])
        table.add_row(["Purchase Date:", expense.get_purchase_date_string()])
        table.add_row(["Category:", expense.get_category().get_name()])

        print(table.draw())
