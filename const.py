import os
from pathlib import Path

DEBUG_MODE = True if 'DEBUG_BACKEND' in os.environ and os.environ['DEBUG_BACKEND'] else False

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

DATABASE_TYPES = {
    "sqlite": "sqlite"
}

SQLITE_DATABASE_PATH = str(Path("{DIR_PATH}/dbs/expenses-tracker.db".format(**locals())))

DATABASE_TABLES = {
    "categories": "categories",
    "expenses": "expenses",
    "expense_tags": "expense_tags",
    "tags": "tags"
}

DATABASE_TYPE = DATABASE_TYPES["sqlite"]

EXPENSES_TABLE_NAME = DATABASE_TABLES["expenses"]
CATEGORIES_TABLE_NAME = DATABASE_TABLES["categories"]
TAGS_TABLE_NAME = DATABASE_TABLES["tags"]
