import os
from pathlib import Path

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
DATABASE_PATH = str(Path("{DIR_PATH}/dbs/expenses-tracker.db".format(**locals())))

DATABASE_TYPES = {
    "sqlite": "sqlite"
}

DATABASE_TABLES = {
    "categories": "categories",
    "expenses": "expenses",
    "tags": "tags"
}

DATABASE_TYPE = DATABASE_TYPES["sqlite"]

EXPENSES_TABLE_NAME = DATABASE_TABLES["expenses"]
CATEGORIES_TABLE_NAME = DATABASE_TABLES["categories"]
TAGS_TABLE_NAME = DATABASE_TABLES["tags"]
