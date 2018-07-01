"""The module contains Expense class"""
import time

class Expense:
    """The class is a model for a single planned Expense"""

    def __init__(self, expense_id, name, cost, purchase_date, category):
        self.__expense_id = expense_id
        self.__name = name
        self.__cost = cost
        self.__purchase_date = purchase_date
        self.__category = category

    def get_expense_id(self):
        """Returns the id of the Expense"""
        return self.__expense_id

    def get_name(self):
        """Returns the name of the Expense"""
        return self.__name

    def get_cost(self):
        """Returns the cost of the Expense"""
        return self.__cost

    def get_purchase_date(self):
        """Returns the purchase_date (seconds since epoch) of the Expense"""
        return self.__purchase_date

    def get_category(self):
        """Returns the name of the category"""
        return self.__category

    def get_purchase_date_string(self):
        """Returns the purchase_date in form of user-friendly string"""
        return time.ctime(self.__purchase_date)

    def to_string(self):
        """Returns a string representation of Expense object"""
        return ("------------------------------------------------------\n"
                # "Expense {id}:\n"
                # "------------------------------------------------------\n"
                "Name: {name}\n"
                "Category: {category}\n"
                "Cost: {cost}\n"
                "Date: {purchase_date}"
               ).format(id=self.__expense_id, name=self.__name,
                        category=self.__category, cost=self.__cost,
                        purchase_date=self.get_purchase_date_string())
