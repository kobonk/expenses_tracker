"""The module contains Shop class"""

class Shop:
    """The class is a model for Shops"""
    def __init__(self, shop_id, name):
        self.__shop_id = shop_id if shop_id else None
        self.__name = name

    def get_shop_id(self):
        """Returns the shop id"""
        return self.__shop_id

    def get_name(self):
        """Returns the name of the shop"""
        return self.__name

    def to_json(self):
        """Returns JSON representation of the Shop model"""
        return {
            "id": self.__shop_id,
            "name": self.__name
        }

    def __str__(self):
        """Returns a string representation of the Shop"""
        return "{} ({})".format(self.get_name(), self.get_shop_id())

    def __eq__(self, other):
        return self.__name == other.get_name()

    def __hash__(self):
        return int("".join([str(ord(ch)) for ch in self.__name]))

    @classmethod
    def from_json(cls, json):
        return Shop(json["id"] if "id" in json else None, json["name"])
