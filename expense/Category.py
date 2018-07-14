"""The module contains Category class"""

class Category:
    """The class is a model for Categories"""
    def __init__(self, category_id, name):
        self.__category_id = category_id
        self.__name = name

    def get_category_id(self):
        """Returns the category id"""
        return self.__category_id

    def get_name(self):
        """Returns the name of the category"""
        return self.__name

    def to_json(self):
        """Returns JSON representation of the Category model"""
        return {
            "id": self.__category_id,
            "name": self.__name
        }
