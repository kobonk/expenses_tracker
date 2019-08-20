"""The module contains Tag class"""
import uuid

class Tag:
    """The class is a model for Categories"""
    def __init__(self, tag_id, name):
        self.__tag_id = tag_id if tag_id else str(uuid.uuid4())
        self.__name = name

    def get_tag_id(self):
        """Returns the tag id"""
        return self.__tag_id

    def get_name(self):
        """Returns the name of the tag"""
        return self.__name

    def to_json(self):
        """Returns JSON representation of the Tag model"""
        return {
            "id": self.__tag_id,
            "name": self.__name
        }

    def __str__(self):
        """Returns a string representation of the Tag"""
        return "{} ({})".format(self.get_name(), self.get_tag_id())

    def __eq__(self, other):
        return self.__name == other.get_name()

    @classmethod
    def from_json(cls, json):
        return Tag(json["id"] if "id" in json else str(uuid.uuid4()), json["name"])
