"""The module contains Statistics class"""

class Statistics:
    """The class is a model for Statistics"""
    def __init__(self, category, total):
        self.__category = category
        self.__total = total

    def get_category(self):
        """Returns the category"""
        return self.__category

    def get_total(self):
        """Returns the sum of Expenses for the Category"""
        return self.__total

    def to_json(self):
        """Returns JSON representation of the Statistics model"""
        return {
            "category": self.__category.to_json(),
            "total": self.__total
        }
