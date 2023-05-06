import os
from pathlib import Path

DEBUG_MODE = True if 'DEBUG_MODE' in os.environ and os.environ['DEBUG_MODE'] else False

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

DATABASE_TYPES = {
    "sqlite": "sqlite"
}

DATABASE_PATH = "/dbs/expenses-tracker.db"
FULL_DATABASE_PATH = str(Path("{DIR_PATH}{DATABASE_PATH}".format(**locals())))

DATABASE_TABLES = {
    "categories": "categories",
    "expenses": "expenses",
    "expense_tags": "expense_tags",
    "tags": "tags",
    "shops": "shops",
    "suggestions": "expense_suggestions"
}

DATABASE_TYPE = DATABASE_TYPES["sqlite"]

EXPENSES_TABLE_NAME = DATABASE_TABLES["expenses"]
CATEGORIES_TABLE_NAME = DATABASE_TABLES["categories"]
TAGS_TABLE_NAME = DATABASE_TABLES["tags"]
