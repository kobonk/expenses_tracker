"""The module contains Expense class"""
import uuid
from datetime import date, datetime
from expense.Category import Category
import pendulum

class Expense:
    """The class is a model for a single Expense"""

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
        """Returns the expense category"""
        return self.__category

    def get_purchase_date_string(self):
        """Returns the purchase_date in form of user-friendly string"""
        return date.fromtimestamp(self.__purchase_date).strftime("%Y-%m-%d")

    def to_json(self):
        """Returns a directory which can be used for JSON output"""
        return {
            "category": self.__category.to_json(),
            "cost": self.__cost,
            "date": self.get_purchase_date_string(),
            "id": self.__expense_id,
            "name": self.__name
        }

    def __str__(self):
        """Returns a string representation of Expense"""
        return "{date}, {name} : {cost}".format(
            date=self.get_purchase_date_string(),
            name=self.get_name(),
            cost=self.get_cost())

    @classmethod
    def from_json(cls, json):
        category_dict = json["category"]
        category = Category(category_dict["id"], category_dict["name"])

        return Expense(uuid.uuid4(), json["name"], json["cost"],
                       convert_date_string_to_timestamp(json["purchase_date"]),
                       category)

def convert_date_string_to_timestamp(date_string):
    """Converts date (YYYY-MM-DD) to a number"""
    try:
        year, month, day = map(int, date_string.split("-"))

        return pendulum.datetime(year, month, day).int_timestamp
    except Exception as exception:
        raise ValueError(exception)
