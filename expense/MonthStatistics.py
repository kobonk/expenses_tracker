"""The module contains a class for single-month Statistics"""

class MonthStatistics:
    """The class represents the statistics for a category
    in a single month time period"""

    def __init__(self, category, total, month):
        """Instantiates the model"""
        self.__category = category
        self.__month = month
        self.__total = total

    def to_json(self):
        """Returns the model representation in JSON format"""
        return {
            "category": self.__category.to_json(),
            "month": self.__month,
            "total": self.__total
        }
