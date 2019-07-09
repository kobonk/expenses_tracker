import os
from pathlib import Path

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
DATABASE_PATH = str(Path("{DIR_PATH}/dbs/expenses-tracker.db".format(**locals())))
EXPENSES_TABLE_NAME = "expenses"
CATEGORIES_TABLE_NAME = "categories"
